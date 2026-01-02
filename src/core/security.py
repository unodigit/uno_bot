"""Security utilities and middleware for UnoBot API."""
import base64
import hashlib
import hmac
import logging
import re
import secrets
from datetime import datetime, timedelta
from typing import Any

from cryptography.fernet import Fernet
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config import settings

logger = logging.getLogger(__name__)

# Rate limiting storage (in-memory for now, can be swapped with Redis)
_rate_limit_store: dict[str, dict[str, Any]] = {}


class RateLimiter:
    """Rate limiter to prevent API abuse."""

    def __init__(self, requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests: Maximum number of requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = requests
        self.window_seconds = window_seconds

    def is_allowed(self, identifier: str) -> tuple[bool, int]:
        """
        Check if request is allowed under rate limit.

        Args:
            identifier: Unique identifier (IP, API key, etc.)

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)

        # Clean old entries
        to_remove = [
            key for key, data in _rate_limit_store.items()
            if datetime.fromisoformat(data["timestamp"]) < window_start
        ]
        for key in to_remove:
            del _rate_limit_store[key]

        # Get current window data
        if identifier not in _rate_limit_store:
            _rate_limit_store[identifier] = {
                "count": 1,
                "timestamp": now.isoformat()
            }
            return True, self.max_requests - 1

        data = _rate_limit_store[identifier]
        data_timestamp = datetime.fromisoformat(data["timestamp"])

        # Check if window has expired
        if data_timestamp < window_start:
            _rate_limit_store[identifier] = {
                "count": 1,
                "timestamp": now.isoformat()
            }
            return True, self.max_requests - 1

        # Increment count
        data["count"] += 1
        remaining = self.max_requests - data["count"]

        if data["count"] > self.max_requests:
            return False, remaining

        return True, remaining

    def reset(self, identifier: str) -> None:
        """Reset rate limit for a specific identifier.

        Args:
            identifier: Unique identifier to reset
        """
        if identifier in _rate_limit_store:
            del _rate_limit_store[identifier]


def reset_rate_limiter() -> None:
    """Clear all rate limit data. Useful for testing."""
    global _rate_limit_store
    _rate_limit_store = {}


# Global rate limiter instance
rate_limiter = RateLimiter(requests=100, window_seconds=60)


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent XSS attacks.

    Args:
        text: User input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Truncate to max length
    text = text[:max_length]

    # Remove or escape potentially dangerous characters
    # Note: We escape rather than remove to preserve user input
    # but prevent execution

    # Remove null bytes
    text = text.replace('\x00', '')

    # Escape HTML special characters
    replacements = {
        '&': '&',
        '<': '<',
        '>': '>',
        '"': '"',
        "'": "'",
        '`': '`',
        'javascript:': '',  # Remove javascript: protocol
        'vbscript:': '',    # Remove vbscript: protocol
        'onload=': '',      # Remove event handlers
        'onerror=': '',     # Remove event handlers
        'onclick=': '',     # Remove event handlers
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # Remove multiple consecutive spaces to prevent obfuscation
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def validate_sql_input(text: str) -> bool:
    """
    Validate input to prevent SQL injection.

    Args:
        text: Input to validate

    Returns:
        True if safe, False if potential SQL injection detected
    """
    if not text:
        return True

    # Common SQL injection patterns
    sql_patterns = [
        r'(?i)\b(OR|AND)\s+\d+\s*=\s*\d+',  # tautologies: OR 1=1
        r'(?i)\b(OR|AND)\s+[\'"]?\w+[\'"]?\s*=\s*[\'"]?\w+[\'"]?',  # OR '1'='1'
        r'(?i)\bUNION\s+ALL\s+SELECT',      # union attacks
        r'(?i)\bDROP\s+(TABLE|DATABASE)',   # drop statements
        r'(?i)\bDELETE\s+FROM',             # delete statements
        r'(?i)\bINSERT\s+INTO',             # insert statements
        r'(?i)\bUPDATE\s+\w+\s+SET',        # update statements
        r'(?i)\bEXEC\s+\w+\s*\(',           # exec function with procedure
        r'(?i)\bEXEC\s*\(',                 # exec function
        r'(?i)\bWAITFOR\s+DELAY',           # time-based attacks
        r'(?i)\bSELECT\s+\*\s+FROM',        # select all pattern
        r'--',                              # SQL comment
        r'/\*.*\*/',                        # SQL block comment
        r';\s*(DROP|DELETE|UPDATE|INSERT)', # multiple statements
    ]

    for pattern in sql_patterns:
        if re.search(pattern, text):
            logger.warning(f"Potential SQL injection detected: {text[:100]}")
            return False

    return True


def mask_sensitive_data(text: str) -> str:
    """
    Mask sensitive data in logs and responses.

    Args:
        text: Text that may contain sensitive data

    Returns:
        Text with sensitive data masked
    """
    if not text:
        return ""

    # Mask email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = re.sub(email_pattern, '[EMAIL_MASKED]', text)

    # Mask API keys (common patterns) - BEFORE phone numbers to avoid conflicts
    api_key_patterns = [
        r'sk-[A-Za-z0-9]{16,}',  # Anthropic-style keys (16+ chars after sk-)
        r'pk-[A-Za-z0-9]{16,}',  # Public keys
        r'AKIA[A-Z0-9]{16}',     # AWS access keys
    ]
    for pattern in api_key_patterns:
        text = re.sub(pattern, '[API_KEY_MASKED]', text)

    # Mask phone numbers (handles formats like 555-123-4567, (555) 123-4567, 555.123.4567)
    # Use word boundaries to avoid matching parts of longer strings
    phone_pattern = r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    text = re.sub(phone_pattern, '[PHONE_MASKED]', text)

    # Mask credit card numbers (basic)
    cc_pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    text = re.sub(cc_pattern, '[CC_MASKED]', text)

    return text


def sign_data(data: str, secret: str | None = None) -> str:
    """
    Create HMAC signature for data verification.

    Args:
        data: Data to sign
        secret: Secret key (uses settings.secret_key if None)

    Returns:
        Hex signature
    """
    if secret is None:
        secret = settings.secret_key

    return hmac.new(
        secret.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def verify_signature(data: str, signature: str, secret: str | None = None) -> bool:
    """
    Verify HMAC signature.

    Args:
        data: Original data
        signature: Signature to verify
        secret: Secret key

    Returns:
        True if signature is valid
    """
    expected = sign_data(data, secret)
    return hmac.compare_digest(expected, signature)


class TokenManager:
    """Secure token management for OAuth and sessions."""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate cryptographically secure token."""
        return secrets.token_hex(length)

    @staticmethod
    def encrypt_token(token: str, secret: str | None = None) -> str:
        """
        Encrypt token using HMAC.

        Note: For production, use proper encryption like Fernet.
        This is a simplified version for the feature requirement.
        """
        if secret is None:
            secret = settings.secret_key

        # Create signature
        signature = sign_data(token, secret)
        return f"{token}:{signature}"

    @staticmethod
    def decrypt_token(encrypted: str, secret: str | None = None) -> str | None:
        """
        Decrypt and verify token.

        Returns:
            Token if valid, None if invalid
        """
        if secret is None:
            secret = settings.secret_key

        try:
            token, signature = encrypted.rsplit(':', 1)
            if verify_signature(token, signature, secret):
                return token
        except ValueError:
            pass

        return None


# OAuth Token Encryption using Fernet (symmetric encryption)
# This is used for storing OAuth refresh tokens securely in the database
def get_fernet_cipher() -> Fernet:
    """Get Fernet cipher using the secret key."""
    # Derive a key from the secret key (Fernet requires 32-byte URL-safe base64 key)
    secret = settings.secret_key.encode('utf-8')
    # Use SHA256 to create a 32-byte key, then base64 encode it
    key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
    return Fernet(key)


def encrypt_oauth_token(token: str) -> str:
    """Encrypt OAuth token for secure storage.

    Args:
        token: OAuth token to encrypt

    Returns:
        Encrypted token as string
    """
    if not token:
        return ""
    cipher = get_fernet_cipher()
    return cipher.encrypt(token.encode('utf-8')).decode('utf-8')


def decrypt_oauth_token(encrypted_token: str) -> str | None:
    """Decrypt OAuth token from storage.

    Args:
        encrypted_token: Encrypted token from database

    Returns:
        Decrypted token or None if decryption fails
    """
    if not encrypted_token:
        return None
    try:
        cipher = get_fernet_cipher()
        return cipher.decrypt(encrypted_token.encode('utf-8')).decode('utf-8')
    except Exception as e:
        logger.warning(f"Failed to decrypt OAuth token: {e}")
        return None


class AdminSecurity:
    """Admin route security and authentication."""

    # Simple admin token system (in production, use JWT or OAuth)
    _admin_tokens: dict[str, dict[str, Any]] = {}

    @staticmethod
    def create_admin_token(username: str, expires_minutes: int = 60) -> str:
        """
        Create an admin access token.

        Args:
            username: Admin username
            expires_minutes: Token lifetime

        Returns:
            Admin token
        """
        token = TokenManager.generate_token(32)
        expiry = datetime.utcnow() + timedelta(minutes=expires_minutes)

        AdminSecurity._admin_tokens[token] = {
            "username": username,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expiry.isoformat(),
            "is_active": True
        }

        return token

    @staticmethod
    def verify_admin_token(token: str) -> dict[str, Any] | None:
        """
        Verify admin token.

        Args:
            token: Admin token to verify

        Returns:
            Token data if valid, None if invalid
        """
        if token not in AdminSecurity._admin_tokens:
            return None

        data = AdminSecurity._admin_tokens[token]

        if not data.get("is_active", False):
            return None

        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.utcnow() > expires_at:
            # Remove expired token
            del AdminSecurity._admin_tokens[token]
            return None

        return data

    @staticmethod
    def revoke_token(token: str) -> None:
        """Revoke an admin token."""
        if token in AdminSecurity._admin_tokens:
            AdminSecurity._admin_tokens[token]["is_active"] = False


# FastAPI security dependencies
security = HTTPBearer(auto_error=False)


async def get_api_key(
    api_key: str = Header(None, alias="X-API-Key")
) -> str:
    """
    Dependency to get and validate API key.

    Args:
        api_key: API key from header

    Returns:
        API key if valid

    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In production, validate against database
    # For now, we'll accept any key for demo purposes
    # but log the attempt

    logger.info(f"API key used: {api_key[:8]}...")
    return api_key


async def require_admin_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict[str, Any]:
    """
    Dependency to require admin authentication.

    Args:
        credentials: Bearer token

    Returns:
        Admin token data

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = AdminSecurity.verify_admin_token(credentials.credentials)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware for FastAPI.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response
    """
    # Get client identifier (IP address)
    client_ip = request.client.host if request.client else "unknown"

    # Check rate limit
    is_allowed, remaining = rate_limiter.is_allowed(client_ip)

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={"X-RateLimit-Remaining": str(remaining)}
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)

    return response


def sanitize_request_data(request_data: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize all data in a request.

    Args:
        request_data: Raw request data

    Returns:
        Sanitized data
    """
    sanitized = {}

    for key, value in request_data.items():
        # Skip internal fields
        if key.startswith('_'):
            sanitized[key] = value
            continue

        if isinstance(value, str):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_request_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_input(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


# Export for use in other modules
__all__ = [
    "RateLimiter",
    "rate_limiter",
    "sanitize_input",
    "validate_sql_input",
    "mask_sensitive_data",
    "sign_data",
    "verify_signature",
    "TokenManager",
    "encrypt_oauth_token",
    "decrypt_oauth_token",
    "AdminSecurity",
    "get_api_key",
    "require_admin_auth",
    "rate_limit_middleware",
    "sanitize_request_data",
]
