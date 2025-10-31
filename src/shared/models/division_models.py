"""
Division-related data models
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DivisionPermissions(BaseModel):
    """Division permissions configuration"""
    division_id: str = Field(..., description="Division identifier")
    allowed_divisions: List[str] = Field(default_factory=list, description="Divisions allowed to access this division's agents")
    shared_agents: List[str] = Field(default_factory=list, description="Agent IDs that are shared with other divisions")
    restricted_agents: List[str] = Field(default_factory=list, description="Agent IDs that are restricted to this division only")
    
    # Cross-division access controls
    allow_cross_division_discovery: bool = Field(default=True, description="Allow other divisions to discover this division's agents")
    allow_cross_division_invocation: bool = Field(default=True, description="Allow other divisions to invoke this division's agents")
    
    # Rate limiting
    max_requests_per_minute: int = Field(default=1000, description="Maximum requests per minute from other divisions")
    max_concurrent_requests: int = Field(default=100, description="Maximum concurrent requests from other divisions")
    
    # Audit and compliance
    audit_cross_division_access: bool = Field(default=True, description="Audit cross-division access attempts")
    log_all_interactions: bool = Field(default=False, description="Log all agent interactions")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DivisionConfig(BaseModel):
    """Division configuration model"""
    division_id: str = Field(..., description="Unique division identifier")
    division_name: str = Field(..., description="Human-readable division name")
    description: str = Field(..., description="Division description")
    
    # Gateway configuration
    gateway_endpoint: str = Field(..., description="Division gateway endpoint URL")
    bedrock_region: str = Field(default="us-east-1", description="AWS region for Bedrock services")
    foundation_model: str = Field(default="anthropic.claude-3-sonnet-20240229-v1:0", description="Default foundation model")
    
    # Authentication configuration
    cognito_user_pool_id: str = Field(..., description="Cognito User Pool ID for authentication")
    allowed_origins: List[str] = Field(default_factory=list, description="Allowed CORS origins")
    
    # Rate limiting configuration
    requests_per_second: int = Field(default=100, description="Requests per second limit")
    burst_limit: int = Field(default=200, description="Burst limit for requests")
    
    # Logging configuration
    cloudwatch_log_group: str = Field(..., description="CloudWatch log group for gateway logs")
    enable_xray_tracing: bool = Field(default=True, description="Enable X-Ray distributed tracing")
    log_level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARN, ERROR")
    
    # Federation configuration
    enable_cross_division_access: bool = Field(default=True, description="Enable cross-division access")
    trusted_divisions: List[str] = Field(default_factory=list, description="List of trusted division IDs")
    federation_role_arn: str = Field(..., description="IAM role ARN for federation")
    
    # Monitoring configuration
    enable_metrics: bool = Field(default=True, description="Enable CloudWatch metrics")
    enable_alarms: bool = Field(default=True, description="Enable CloudWatch alarms")
    alarm_notification_topic: Optional[str] = Field(None, description="SNS topic ARN for alarm notifications")
    
    # Security configuration
    encryption_key_id: Optional[str] = Field(None, description="KMS key ID for encryption")
    enable_waf: bool = Field(default=True, description="Enable AWS WAF protection")
    
    # Permissions
    permissions: DivisionPermissions = Field(..., description="Division permissions configuration")
    
    # Metadata
    tags: Dict[str, str] = Field(default_factory=dict, description="Division tags")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Status
    is_active: bool = Field(default=True, description="Whether division is active")
    maintenance_mode: bool = Field(default=False, description="Whether division is in maintenance mode")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DivisionStatus(BaseModel):
    """Division status model"""
    division_id: str = Field(..., description="Division identifier")
    status: str = Field(..., description="Division status: active, inactive, maintenance, error")
    health_score: float = Field(..., description="Health score from 0.0 to 1.0")
    
    # Metrics
    active_agents: int = Field(default=0, description="Number of active agents")
    total_requests: int = Field(default=0, description="Total requests in last hour")
    error_rate: float = Field(default=0.0, description="Error rate percentage")
    average_response_time_ms: float = Field(default=0.0, description="Average response time in milliseconds")
    
    # Resource usage
    cpu_utilization: float = Field(default=0.0, description="CPU utilization percentage")
    memory_utilization: float = Field(default=0.0, description="Memory utilization percentage")
    
    # Timestamps
    last_health_check: datetime = Field(default_factory=datetime.utcnow, description="Last health check timestamp")
    uptime_seconds: int = Field(default=0, description="Uptime in seconds")
    
    # Issues
    active_alarms: List[str] = Field(default_factory=list, description="List of active alarm names")
    warnings: List[str] = Field(default_factory=list, description="List of warning messages")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }