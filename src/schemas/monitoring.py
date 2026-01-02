"""Monitoring and metrics response schemas."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MetricsResponse(BaseModel):
    """Base metrics response model."""
    success: bool = Field(description="Whether the request was successful")
    data: Dict[str, Any] = Field(description="The metrics data")


class HealthStatusResponse(BaseModel):
    """Health status response model."""
    success: bool = Field(description="Whether the request was successful")
    data: Dict[str, Any] = Field(description="Health check results")


class SystemMetricsResponse(BaseModel):
    """System metrics response model."""
    success: bool = Field(description="Whether the request was successful")
    data: Dict[str, Any] = Field(description="System metrics data")


class EndpointMetricsResponse(BaseModel):
    """Endpoint metrics response model."""
    success: bool = Field(description="Whether the request was successful")
    data: Dict[str, Any] = Field(description="Endpoint metrics data")


class RequestMetrics(BaseModel):
    """Request metrics model."""
    total_requests: int = Field(description="Total number of requests")
    successful_requests: int = Field(description="Number of successful requests")
    failed_requests: int = Field(description="Number of failed requests")
    average_response_time: float = Field(description="Average response time in seconds")
    p95_response_time: float = Field(description="95th percentile response time in seconds")


class DatabaseMetrics(BaseModel):
    """Database metrics model."""
    size_mb: float = Field(description="Database size in megabytes")
    active_connections: int = Field(description="Number of active database connections")


class SessionMetrics(BaseModel):
    """Session metrics model."""
    active_sessions: int = Field(description="Number of active sessions")
    sessions_last_hour: int = Field(description="Number of sessions started in the last hour")


class BusinessMetrics(BaseModel):
    """Business metrics model."""
    total_messages: int = Field(description="Total number of messages sent")
    prd_generated: int = Field(description="Total number of PRDs generated")
    bookings_created: int = Field(description="Total number of bookings created")
    expert_matches: int = Field(description="Total number of expert matches")


class EndpointMetric(BaseModel):
    """Individual endpoint metric model."""
    request_count: int = Field(description="Number of requests to this endpoint")
    average_response_time: float = Field(description="Average response time in seconds")
    p95_response_time: float = Field(description="95th percentile response time in seconds")
    success_rate: float = Field(description="Success rate percentage")


class HealthCheck(BaseModel):
    """Health check model."""
    status: str = Field(description="Health status: ok, warning, error, or unknown")
    message: str = Field(description="Detailed health check message")
    last_check: str = Field(description="ISO timestamp of last check")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional health check details")