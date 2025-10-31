"""
Tool-related data models
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import uuid


class ToolExecutionStatus(str, Enum):
    """Tool execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ToolDefinition(BaseModel):
    """Tool definition model for Tool Registry"""
    tool_id: str = Field(..., description="Unique tool identifier")
    name: str = Field(..., description="Human-readable tool name")
    description: str = Field(..., description="Tool description")
    version: str = Field(default="1.0.0", description="Tool version")
    
    # Runtime configuration
    runtime: str = Field(..., description="Runtime environment: lambda, ecs, external")
    function_arn: Optional[str] = Field(None, description="Lambda function ARN for lambda runtime")
    endpoint: Optional[str] = Field(None, description="HTTP endpoint for external runtime")
    
    # Schema definitions
    input_schema: Dict[str, Any] = Field(..., description="JSON schema for tool input")
    output_schema: Dict[str, Any] = Field(..., description="JSON schema for tool output")
    
    # Execution configuration
    timeout: int = Field(default=300, description="Execution timeout in seconds")
    memory_limit: Optional[int] = Field(None, description="Memory limit in MB for lambda runtime")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    
    # Access control
    permissions: List[str] = Field(default_factory=list, description="Divisions with access permission")
    is_public: bool = Field(default=False, description="Whether tool is publicly accessible")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tool tags for categorization")
    category: str = Field(default="general", description="Tool category")
    author: str = Field(..., description="Tool author")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    
    # Status
    is_active: bool = Field(default=True, description="Whether tool is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ToolExecution(BaseModel):
    """Tool execution model"""
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique execution identifier")
    tool_id: str = Field(..., description="Tool identifier")
    requesting_agent_id: str = Field(..., description="Requesting agent identifier")
    requesting_division_id: str = Field(..., description="Requesting division identifier")
    
    # Execution details
    input_parameters: Dict[str, Any] = Field(..., description="Tool input parameters")
    status: ToolExecutionStatus = Field(default=ToolExecutionStatus.PENDING, description="Execution status")
    
    # Results
    result: Optional[Dict[str, Any]] = Field(None, description="Tool execution result")
    error_code: Optional[str] = Field(None, description="Error code if execution failed")
    error_message: Optional[str] = Field(None, description="Error message if execution failed")
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Execution start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Execution completion timestamp")
    duration_ms: Optional[int] = Field(None, description="Execution duration in milliseconds")
    
    # Tracing
    trace_id: Optional[str] = Field(None, description="Distributed tracing identifier")
    correlation_id: Optional[str] = Field(None, description="Correlation identifier")
    
    # Resource usage
    memory_used_mb: Optional[int] = Field(None, description="Memory used in MB")
    cpu_time_ms: Optional[int] = Field(None, description="CPU time in milliseconds")
    
    # Retry handling
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ToolInvocationRequest(BaseModel):
    """Tool invocation request"""
    tool_id: str = Field(..., description="Tool identifier")
    parameters: Dict[str, Any] = Field(..., description="Tool input parameters")
    requesting_agent_id: str = Field(..., description="Requesting agent identifier")
    requesting_division_id: str = Field(..., description="Requesting division identifier")
    
    # Optional execution configuration
    timeout: Optional[int] = Field(None, description="Override default timeout")
    trace_id: Optional[str] = Field(None, description="Distributed tracing identifier")
    correlation_id: Optional[str] = Field(None, description="Correlation identifier")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional request metadata")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ToolInvocationResponse(BaseModel):
    """Tool invocation response"""
    execution_id: str = Field(..., description="Execution identifier")
    tool_id: str = Field(..., description="Tool identifier")
    
    # Response details
    success: bool = Field(..., description="Whether execution was successful")
    result: Optional[Dict[str, Any]] = Field(None, description="Tool execution result")
    error_code: Optional[str] = Field(None, description="Error code if execution failed")
    error_message: Optional[str] = Field(None, description="Error message if execution failed")
    
    # Timing
    duration_ms: int = Field(..., description="Execution duration in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }