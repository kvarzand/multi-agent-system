"""
Agent-related data models
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class AgentCapability(BaseModel):
    """Agent capability definition"""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    version: str = Field(default="1.0.0", description="Capability version")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Capability parameters")


class AgentRegistration(BaseModel):
    """Agent registration model for Enterprise Agent Registry"""
    agent_id: str = Field(..., description="Unique agent identifier")
    division_id: str = Field(..., description="Division identifier")
    agent_name: str = Field(..., description="Human-readable agent name")
    agent_type: str = Field(..., description="Agent type: bedrock, lambda, custom")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    endpoint: str = Field(..., description="Agent endpoint URL")
    
    # Bedrock-specific fields
    bedrock_agent_id: Optional[str] = Field(None, description="Bedrock Agent ID")
    bedrock_agent_alias_id: Optional[str] = Field(None, description="Bedrock Agent Alias ID")
    foundation_model: Optional[str] = Field(None, description="Foundation model ARN")
    knowledge_bases: List[str] = Field(default_factory=list, description="Knowledge base IDs")
    action_groups: List[str] = Field(default_factory=list, description="Action group names")
    
    # Sharing and permissions
    is_shareable: bool = Field(default=False, description="Whether agent can be shared across divisions")
    permissions: List[str] = Field(default_factory=list, description="Divisions with access permission")
    
    # Status and health
    status: AgentStatus = Field(default=AgentStatus.ACTIVE, description="Agent status")
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow, description="Last heartbeat timestamp")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional agent metadata")
    version: str = Field(default="1.0.0", description="Agent version")
    runtime: str = Field(..., description="Runtime environment")
    timeout: int = Field(default=300, description="Request timeout in seconds")
    conversation_memory: bool = Field(default=False, description="Whether agent supports conversation memory")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentHealthCheck(BaseModel):
    """Agent health check response"""
    agent_id: str = Field(..., description="Agent identifier")
    status: AgentStatus = Field(..., description="Current agent status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional health metadata")

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }