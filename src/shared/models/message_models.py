"""
Message-related data models for agent communication
"""
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field
import uuid


class MessageType(str, Enum):
    """Message type enumeration"""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    HEARTBEAT = "heartbeat"


class MessageStatus(str, Enum):
    """Message status enumeration"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"


class AgentMessage(BaseModel):
    """Agent message model for cross-division communication"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message identifier")
    source_agent_id: str = Field(..., description="Source agent identifier")
    source_division_id: str = Field(..., description="Source division identifier")
    target_agent_id: str = Field(..., description="Target agent identifier")
    target_division_id: str = Field(..., description="Target division identifier")
    
    message_type: MessageType = Field(..., description="Message type")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    
    # Correlation and tracing
    correlation_id: Optional[str] = Field(None, description="Correlation identifier for request-response pairs")
    trace_id: Optional[str] = Field(None, description="Distributed tracing identifier")
    parent_message_id: Optional[str] = Field(None, description="Parent message identifier for responses")
    
    # Timing and TTL
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message creation timestamp")
    ttl: int = Field(default=3600, description="Time to live in seconds")
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="Message expiration timestamp")
    
    # Delivery tracking
    status: MessageStatus = Field(default=MessageStatus.PENDING, description="Message delivery status")
    retry_count: int = Field(default=0, description="Number of delivery attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    # Metadata
    priority: int = Field(default=5, description="Message priority (1-10, higher is more urgent)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional message metadata")

    def __post_init__(self):
        """Set expires_at based on timestamp and ttl"""
        if self.expires_at == datetime.utcnow():
            self.expires_at = datetime.fromtimestamp(self.timestamp.timestamp() + self.ttl)

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessageDeliveryReceipt(BaseModel):
    """Message delivery receipt"""
    message_id: str = Field(..., description="Original message identifier")
    status: MessageStatus = Field(..., description="Delivery status")
    delivered_at: datetime = Field(default_factory=datetime.utcnow, description="Delivery timestamp")
    error_message: Optional[str] = Field(None, description="Error message if delivery failed")
    retry_count: int = Field(default=0, description="Number of delivery attempts")

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CrossDivisionRequest(BaseModel):
    """Cross-division agent invocation request"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    source_division_id: str = Field(..., description="Source division identifier")
    target_division_id: str = Field(..., description="Target division identifier")
    target_agent_id: str = Field(..., description="Target agent identifier")
    
    # Request details
    action: str = Field(..., description="Action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    context: Dict[str, Any] = Field(default_factory=dict, description="Request context")
    
    # Authentication and authorization
    requester_id: str = Field(..., description="Requesting user or agent identifier")
    permissions: List[str] = Field(default_factory=list, description="Required permissions")
    
    # Timing
    timeout: int = Field(default=300, description="Request timeout in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CrossDivisionResponse(BaseModel):
    """Cross-division agent invocation response"""
    request_id: str = Field(..., description="Original request identifier")
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique response identifier")
    
    # Response details
    success: bool = Field(..., description="Whether the request was successful")
    result: Optional[Dict[str, Any]] = Field(None, description="Response result data")
    error_code: Optional[str] = Field(None, description="Error code if request failed")
    error_message: Optional[str] = Field(None, description="Error message if request failed")
    
    # Timing
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }