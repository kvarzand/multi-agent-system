"""
Configuration management for Multi-Agent System
"""
import os
from typing import Dict, List, Optional, Any
from pydantic import BaseSettings, Field


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    enterprise_registry_table: str = Field(
        default="enterprise-agent-registry",
        env="ENTERPRISE_REGISTRY_TABLE"
    )
    tool_registry_table: str = Field(
        default="tool-registry",
        env="TOOL_REGISTRY_TABLE"
    )
    tool_execution_table: str = Field(
        default="tool-executions",
        env="TOOL_EXECUTION_TABLE"
    )
    
    class Config:
        env_prefix = "DB_"


class AWSConfig(BaseSettings):
    """AWS service configuration"""
    region: str = Field(default="us-east-1", env="AWS_REGION")
    account_id: Optional[str] = Field(default=None, env="AWS_ACCOUNT_ID")
    
    # EventBridge
    event_bus_name: str = Field(
        default="multi-agent-communication",
        env="EVENT_BUS_NAME"
    )
    
    # S3 Buckets
    tool_artifacts_bucket: Optional[str] = Field(default=None, env="TOOL_ARTIFACTS_BUCKET")
    
    # KMS
    encryption_key_id: Optional[str] = Field(default=None, env="ENCRYPTION_KEY_ID")
    
    # Secrets Manager
    system_secrets_name: str = Field(
        default="multi-agent-system/config",
        env="SYSTEM_SECRETS_NAME"
    )
    
    class Config:
        env_prefix = "AWS_"


class DivisionConfig(BaseSettings):
    """Division-specific configuration"""
    division_id: str = Field(..., env="DIVISION_ID")
    division_name: Optional[str] = Field(default=None, env="DIVISION_NAME")
    
    # Cognito
    user_pool_id: Optional[str] = Field(default=None, env="USER_POOL_ID")
    user_pool_client_id: Optional[str] = Field(default=None, env="USER_POOL_CLIENT_ID")
    
    # Bedrock
    bedrock_region: str = Field(default="us-east-1", env="BEDROCK_REGION")
    default_foundation_model: str = Field(
        default="anthropic.claude-3-sonnet-20240229-v1:0",
        env="DEFAULT_FOUNDATION_MODEL"
    )
    
    # Gateway
    gateway_endpoint: Optional[str] = Field(default=None, env="GATEWAY_ENDPOINT")
    
    # Rate limiting
    requests_per_second: int = Field(default=100, env="REQUESTS_PER_SECOND")
    burst_limit: int = Field(default=200, env="BURST_LIMIT")
    
    class Config:
        env_prefix = "DIVISION_"


class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration"""
    metrics_namespace: str = Field(
        default="MultiAgentSystem",
        env="METRICS_NAMESPACE"
    )
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    enable_xray_tracing: bool = Field(default=True, env="ENABLE_XRAY_TRACING")
    
    # CloudWatch
    log_group_prefix: str = Field(
        default="/aws/multi-agent-system",
        env="LOG_GROUP_PREFIX"
    )
    
    # Alerts
    alert_topic_arn: Optional[str] = Field(default=None, env="ALERT_TOPIC_ARN")
    
    class Config:
        env_prefix = "MONITORING_"


class SecurityConfig(BaseSettings):
    """Security configuration"""
    enable_encryption: bool = Field(default=True, env="ENABLE_ENCRYPTION")
    enable_audit_logging: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")
    
    # JWT
    jwt_secret_key: Optional[str] = Field(default=None, env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["*"],
        env="ALLOWED_ORIGINS"
    )
    
    class Config:
        env_prefix = "SECURITY_"


class SystemConfig(BaseSettings):
    """Main system configuration"""
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Component configurations
    database: DatabaseConfig = DatabaseConfig()
    aws: AWSConfig = AWSConfig()
    division: Optional[DivisionConfig] = None
    monitoring: MonitoringConfig = MonitoringConfig()
    security: SecurityConfig = SecurityConfig()
    
    # Message routing
    message_ttl_seconds: int = Field(default=3600, env="MESSAGE_TTL_SECONDS")
    max_retry_attempts: int = Field(default=3, env="MAX_RETRY_ATTEMPTS")
    
    # Tool execution
    default_tool_timeout: int = Field(default=300, env="DEFAULT_TOOL_TIMEOUT")
    max_concurrent_executions: int = Field(default=100, env="MAX_CONCURRENT_EXECUTIONS")
    
    # Agent discovery
    discovery_cache_ttl: int = Field(default=300, env="DISCOVERY_CACHE_TTL")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize division config if division_id is provided
        if os.getenv("DIVISION_ID"):
            self.division = DivisionConfig()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "json": {
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
                }
            },
            "handlers": {
                "default": {
                    "level": self.monitoring.log_level,
                    "formatter": "json" if self.is_production else "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                }
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": self.monitoring.log_level,
                    "propagate": False
                }
            }
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global configuration instance
config = SystemConfig()