"""Performance monitoring and metrics service for UnoBot."""
import logging
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from src.core.config import settings
from src.core.database import get_database_size

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    path: str
    method: str
    status_code: int
    duration: float
    timestamp: datetime
    user_agent: str | None = None
    ip_address: str | None = None


@dataclass
class SystemMetrics:
    """System-level metrics."""
    timestamp: datetime
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    # Database metrics
    database_size_mb: float = 0.0
    active_connections: int = 0
    # Session metrics
    active_sessions: int = 0
    sessions_last_hour: int = 0
    # Business metrics
    total_messages: int = 0
    prd_generated: int = 0
    bookings_created: int = 0
    expert_matches: int = 0


class MonitoringService:
    """Service for collecting and analyzing application metrics."""

    def __init__(self):
        # Request tracking
        self.request_history: deque[RequestMetrics] = deque(maxlen=10000)
        self._active_requests: dict[str, float] = {}  # request_id -> start_time
        self._request_counts: dict[str, int] = defaultdict(int)
        self._response_times: dict[str, list[float]] = defaultdict(list)

        # Session tracking
        self._session_starts: deque[datetime] = deque(maxlen=10000)
        self._active_sessions_count: int = 0

        # Business metrics
        self._message_count: int = 0
        self._prd_count: int = 0
        self._booking_count: int = 0
        self._expert_match_count: int = 0

        # Health checks
        self._last_health_check: datetime | None = None
        self._health_status: dict[str, Any] = {}

    def record_request_start(self, request_id: str, path: str, method: str, user_agent: str | None = None, ip_address: str | None = None) -> None:
        """Record the start of a request."""
        self._active_requests[request_id] = time.time()

        # Log slow requests in development
        if settings.debug:
            logger.debug(f"Request started: {method} {path}")

    def record_request_end(self, request_id: str, status_code: int, path: str, method: str, user_agent: str | None = None, ip_address: str | None = None) -> None:
        """Record the end of a request and calculate metrics."""
        start_time = self._active_requests.pop(request_id, None)
        if start_time is None:
            logger.warning(f"Request end recorded for unknown request: {request_id}")
            return

        duration = time.time() - start_time

        # Store request metrics
        request_metrics = RequestMetrics(
            path=path,
            method=method,
            status_code=status_code,
            duration=duration,
            timestamp=datetime.now(),
            user_agent=user_agent,
            ip_address=ip_address
        )
        self.request_history.append(request_metrics)

        # Update counters
        self._request_counts[f"{method} {path}"] += 1
        self._response_times[f"{method} {path}"].append(duration)

        # Keep only last 1000 response times per endpoint
        if len(self._response_times[f"{method} {path}"]) > 1000:
            self._response_times[f"{method} {path}"].pop(0)

        if settings.debug:
            logger.debug(f"Request completed: {method} {path} - {status_code} - {duration:.3f}s")

    def record_session_start(self) -> None:
        """Record a new session start."""
        self._session_starts.append(datetime.now())
        self._active_sessions_count += 1

    def record_session_end(self) -> None:
        """Record a session end."""
        if self._active_sessions_count > 0:
            self._active_sessions_count -= 1

    def record_message_sent(self) -> None:
        """Record a message being sent."""
        self._message_count += 1

    def record_prd_generated(self) -> None:
        """Record a PRD being generated."""
        self._prd_count += 1

    def record_booking_created(self) -> None:
        """Record a booking being created."""
        self._booking_count += 1

    def record_expert_match(self) -> None:
        """Record an expert match."""
        self._expert_match_count += 1

    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        # Calculate request metrics
        recent_requests = [r for r in self.request_history if r.timestamp >= one_hour_ago]
        total_requests = len(recent_requests)
        successful_requests = len([r for r in recent_requests if 200 <= r.status_code < 400])
        failed_requests = len([r for r in recent_requests if r.status_code >= 400])

        # Calculate response times
        if recent_requests:
            response_times = [r.duration for r in recent_requests]
            response_times.sort()
            average_response_time = sum(response_times) / len(response_times)
            p95_response_time = response_times[int(0.95 * len(response_times))]
        else:
            average_response_time = 0.0
            p95_response_time = 0.0

        # Calculate sessions last hour
        sessions_last_hour = len([s for s in self._session_starts if s >= one_hour_ago])

        return SystemMetrics(
            timestamp=now,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=average_response_time,
            p95_response_time=p95_response_time,
            database_size_mb=self._get_database_size_mb(),
            active_connections=self._get_active_connections(),
            active_sessions=self._active_sessions_count,
            sessions_last_hour=sessions_last_hour,
            total_messages=self._message_count,
            prd_generated=self._prd_count,
            bookings_created=self._booking_count,
            expert_matches=self._expert_match_count,
        )

    def get_endpoint_metrics(self) -> dict[str, dict[str, Any]]:
        """Get metrics per endpoint."""
        metrics = {}

        for endpoint in self._request_counts:
            request_count = self._request_counts[endpoint]
            response_times = self._response_times[endpoint]

            if response_times:
                avg_time = sum(response_times) / len(response_times)
                response_times_sorted = sorted(response_times)
                p95_time = response_times_sorted[int(0.95 * len(response_times_sorted))]
            else:
                avg_time = 0.0
                p95_time = 0.0

            metrics[endpoint] = {
                "request_count": request_count,
                "average_response_time": avg_time,
                "p95_response_time": p95_time,
                "success_rate": self._calculate_success_rate(endpoint)
            }

        return metrics

    def get_health_status(self) -> dict[str, Any]:
        """Get application health status."""
        now = datetime.now()

        # Check if we should run health checks
        if (self._last_health_check is None or
            now - self._last_health_check > timedelta(minutes=1)):
            self._run_health_checks()

        return {
            "timestamp": now.isoformat(),
            "status": "healthy" if all(v["status"] == "ok" for v in self._health_status.values()) else "degraded",
            "checks": self._health_status
        }

    def _run_health_checks(self) -> None:
        """Run health checks and update status."""
        now = datetime.now()

        # Database connectivity check
        try:
            db_size = self._get_database_size_mb()
            self._health_status["database"] = {
                "status": "ok",
                "message": f"Database accessible, size: {db_size:.2f}MB",
                "last_check": now.isoformat(),
                "size_mb": db_size
            }
        except Exception as e:
            self._health_status["database"] = {
                "status": "error",
                "message": f"Database check failed: {str(e)}",
                "last_check": now.isoformat()
            }

        # Memory usage check (basic)
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            self._health_status["memory"] = {
                "status": "ok" if memory_percent < 90 else "warning",
                "message": f"Memory usage: {memory_percent:.1f}%",
                "last_check": now.isoformat(),
                "usage_percent": memory_percent
            }
        except ImportError:
            self._health_status["memory"] = {
                "status": "unknown",
                "message": "psutil not available",
                "last_check": now.isoformat()
            }

        self._last_health_check = now

    def _get_database_size_mb(self) -> float:
        """Get database size in megabytes."""
        try:
            return get_database_size()
        except Exception as e:
            logger.error(f"Failed to get database size: {e}")
            return 0.0

    def _get_active_connections(self) -> int:
        """Get number of active database connections."""
        # This would need to be implemented based on your database setup
        # For now, return 0
        return 0

    def _calculate_success_rate(self, endpoint: str) -> float:
        """Calculate success rate for an endpoint."""
        # This would need to track successful vs failed requests per endpoint
        # For now, return 100%
        return 100.0

    @contextmanager
    def track_request(self, request_id: str, path: str, method: str, user_agent: str | None = None, ip_address: str | None = None):
        """Context manager for tracking request metrics."""
        self.record_request_start(request_id, path, method, user_agent, ip_address)
        try:
            yield
        except Exception:
            # Record failed request
            self.record_request_end(request_id, 500, path, method, user_agent, ip_address)
            raise
        else:
            # Record successful request (status code will be set by the endpoint)
            pass


# Global monitoring service instance
monitoring_service = MonitoringService()


# Middleware for automatic request tracking
class MonitoringMiddleware:
    """FastAPI middleware for automatic metrics collection."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract request info
        path = scope.get("path", "/")
        method = scope.get("method", "GET")
        headers = dict(scope.get("headers", []))

        # Get user agent and IP
        user_agent = headers.get(b"user-agent", b"").decode()
        ip_address = headers.get(b"x-forwarded-for", b"").decode() or headers.get(b"x-real-ip", b"").decode()

        # Generate request ID
        import uuid
        request_id = str(uuid.uuid4())

        # Track request start
        monitoring_service.record_request_start(request_id, path, method, user_agent, ip_address)

        # Wrap send to capture response
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)

                # Track request end
                monitoring_service.record_request_end(request_id, status_code, path, method, user_agent, ip_address)

            await send(message)

        await self.app(scope, receive, send_wrapper)


def get_monitoring_service() -> MonitoringService:
    """Get the monitoring service instance."""
    return monitoring_service
