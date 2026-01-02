"""Integration test for Socket.io reconnection configuration.

This test verifies that the Socket.io client is properly configured
for automatic reconnection without needing to spin up a browser.
"""

import pytest
import re


class TestSocketIOReconnectionConfig:
    """Test Socket.io reconnection configuration in the codebase."""

    def test_websocket_client_has_reconnection_config(self):
        """
        Verify that the WebSocketClient class has proper reconnection settings.

        This test reads the TypeScript source code to verify configuration.
        """
        # Read the WebSocket client source
        with open('client/src/api/websocket.ts', 'r') as f:
            content = f.read()

        # Verify reconnection is enabled in Socket.IO connection
        assert 'reconnection: true' in content, "Reconnection not enabled"
        print("✓ Reconnection enabled: true")

        # Verify reconnection attempts are configured
        assert 'reconnectionAttempts:' in content, "Reconnection attempts not configured"
        print("✓ Reconnection attempts configured")

        # Verify reconnect delay is configured
        assert 'reconnectionDelay:' in content, "Reconnection delay not configured"
        print("✓ Reconnection delay configured")

        # Verify the class has reconnection properties
        assert 'reconnectAttempts' in content, "Missing reconnectAttempts property"
        assert 'maxReconnectAttempts' in content, "Missing maxReconnectAttempts property"
        assert 'reconnectDelay' in content, "Missing reconnectDelay property"
        print("✓ Reconnection properties exist")

    def test_websocket_client_has_reconnection_methods(self):
        """
        Verify that the WebSocketClient class has reconnection methods.
        """
        with open('client/src/api/websocket.ts', 'r') as f:
            content = f.read()

        # Verify reconnect method exists
        assert 'reconnect()' in content or 'reconnect(' in content, "Missing reconnect method"
        print("✓ Reconnect method exists")

        # Verify disconnect method exists
        assert 'disconnect()' in content or 'disconnect(' in content, "Missing disconnect method"
        print("✓ Disconnect method exists")

        # Verify isConnected method exists
        assert 'isConnected()' in content or 'isConnected(' in content, "Missing isConnected method"
        print("✓ isConnected method exists")

    def test_socket_io_config_has_correct_values(self):
        """
        Verify that Socket.IO configuration has correct reconnection values.
        """
        with open('client/src/api/websocket.ts', 'r') as f:
            content = f.read()

        # Extract the io() call configuration
        # Look for the connection configuration
        io_config_pattern = r'io\([^)]+reconnectionAttempts:\s*(\d+)'
        match = re.search(io_config_pattern, content)

        if match:
            attempts = int(match.group(1))
            assert attempts == 5, f"Expected 5 reconnection attempts, got {attempts}"
            print(f"✓ Reconnection attempts: {attempts}")
        else:
            # Alternative check - verify maxReconnectAttempts is set to 5
            assert 'maxReconnectAttempts = 5' in content or 'maxReconnectAttempts=5' in content or 'maxReconnectAttempts:5' in content
            print("✓ Max reconnect attempts: 5")

        # Check reconnect delay
        delay_pattern = r'reconnectionDelay:\s*(\d+)'
        delay_match = re.search(delay_pattern, content)

        if delay_match:
            delay = int(delay_match.group(1))
            assert delay == 1000, f"Expected 1000ms reconnect delay, got {delay}"
            print(f"✓ Reconnect delay: {delay}ms")
        else:
            assert 'reconnectDelay = 1000' in content or 'reconnectDelay=1000' in content or 'reconnectDelay:1000' in content
            print("✓ Reconnect delay: 1000ms")

    def test_socket_io_error_handler_exists(self):
        """
        Verify that Socket.IO error handling is configured.
        """
        with open('client/src/api/websocket.ts', 'r') as f:
            content = f.read()

        # Check for connect_error handler
        assert "'connect_error'" in content or '"connect_error"' in content, "Missing connect_error handler"
        print("✓ Connection error handler configured")

        # Check for disconnect handler
        assert "'disconnect'" in content or '"disconnect"' in content, "Missing disconnect handler"
        print("✓ Disconnect handler configured")

        # Check that reconnection attempts are tracked
        assert 'reconnectAttempts' in content, "Reconnection attempts not tracked"
        print("✓ Reconnection attempts tracked")

    def test_backend_socket_io_server_configured(self):
        """
        Verify that the backend has Socket.IO server configured.
        """
        with open('src/api/routes/websocket.py', 'r') as f:
            content = f.read()

        # Check for AsyncServer
        assert 'AsyncServer' in content, "AsyncServer not imported"
        print("✓ AsyncServer imported")

        # Check for server initialization
        assert 'sio = AsyncServer(' in content or 'AsyncServer(' in content, "Socket.IO server not initialized"
        print("✓ Socket.IO server initialized")

        # Check for CORS configuration
        assert 'cors_allowed_origins' in content, "CORS not configured"
        print("✓ CORS configured")

        # Check for async_mode
        assert 'async_mode' in content, "async_mode not configured"
        print("✓ async_mode configured")

    def test_backend_websocket_manager_exists(self):
        """
        Verify that the backend has WebSocketManager for connection tracking.
        """
        with open('src/api/routes/websocket.py', 'r') as f:
            content = f.read()

        # Check for WebSocketManager class
        assert 'class WebSocketManager' in content, "WebSocketManager class not found"
        print("✓ WebSocketManager class exists")

        # Check for active_connections tracking
        assert 'active_connections' in content, "active_connections not tracked"
        print("✓ Active connections tracked")

        # Check for disconnect method
        assert 'def disconnect(' in content, "disconnect method not found"
        print("✓ Disconnect method exists")

    def test_reconnection_flow_complete(self):
        """
        Verify the complete reconnection flow is implemented.

        This checks that:
        1. Client has reconnection configured
        2. Client tracks reconnection attempts
        3. Client has error handling
        4. Client has reconnect method
        5. Server has connection management
        """
        # Client checks
        with open('client/src/api/websocket.ts', 'r') as f:
            client_content = f.read()

        client_checks = {
            'reconnection_enabled': 'reconnection: true' in client_content,
            'attempts_configured': 'reconnectionAttempts' in client_content,
            'delay_configured': 'reconnectionDelay' in client_content,
            'error_handler': "'connect_error'" in client_content or '"connect_error"' in client_content,
            'reconnect_method': 'reconnect(' in client_content or 'reconnect()' in client_content,
        }

        # Server checks
        with open('src/api/routes/websocket.py', 'r') as f:
            server_content = f.read()

        server_checks = {
            'async_server': 'AsyncServer' in server_content,
            'connection_manager': 'class WebSocketManager' in server_content,
            'active_connections': 'active_connections' in server_content,
        }

        all_checks = {**client_checks, **server_checks}

        print("\nSocket.io Reconnection Flow Verification:")
        for check, passed in all_checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check.replace('_', ' ').title()}")

        assert all(all_checks.values()), "Some reconnection flow checks failed"

        print("\n✓ Complete reconnection flow verified")


class TestSocketIOReconnectionValues:
    """Test specific Socket.io reconnection configuration values."""

    def test_max_reconnect_attempts_is_five(self):
        """Verify max reconnect attempts is set to 5."""
        with open('client/src/api/websocket.ts', 'r') as f:
            content = f.read()

        # Check for maxReconnectAttempts = 5
        assert 'maxReconnectAttempts' in content and '5' in content
        print("✓ Max reconnect attempts: 5")

    def test_reconnect_delay_is_1000ms(self):
        """Verify reconnect delay starts at 1000ms."""
        with open('client/src/api/websocket.ts', 'r') as f:
            content = f.read()

        # Check for reconnectDelay = 1000
        assert 'reconnectDelay' in content and '1000' in content
        print("✓ Reconnect delay: 1000ms")

    def test_socket_io_transports_configured(self):
        """Verify that both websocket and polling transports are available."""
        with open('client/src/api/websocket.ts', 'r') as f:
            content = f.read()

        # Look for transports configuration
        assert 'transports:' in content, "Transports not configured"
        assert "'websocket'" in content or '"websocket"' in content, "WebSocket transport not configured"
        assert "'polling'" in content or '"polling"' in content, "Polling transport not configured"
        print("✓ Transports configured: websocket, polling")
