"""
Message routing and handling interfaces
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from ..models.message_models import AgentMessage, MessageDeliveryReceipt


class IMessageHandler(ABC):
    """Interface for message handlers"""
    
    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Handle an incoming message
        
        Args:
            message: Incoming agent message
            
        Returns:
            Message handling result
        """
        pass
    
    @abstractmethod
    def can_handle(self, message: AgentMessage) -> bool:
        """
        Check if this handler can process the message
        
        Args:
            message: Agent message to check
            
        Returns:
            True if handler can process the message
        """
        pass


class IMessageRouter(ABC):
    """Interface for message routing implementations"""
    
    @abstractmethod
    async def send_message(self, message: AgentMessage) -> MessageDeliveryReceipt:
        """
        Send a message to the target agent
        
        Args:
            message: Message to send
            
        Returns:
            Delivery receipt
        """
        pass
    
    @abstractmethod
    async def route_message(self, message: AgentMessage) -> bool:
        """
        Route a message to the appropriate destination
        
        Args:
            message: Message to route
            
        Returns:
            True if routing successful
        """
        pass
    
    @abstractmethod
    async def register_handler(
        self,
        message_type: str,
        handler: IMessageHandler
    ) -> bool:
        """
        Register a message handler for a specific message type
        
        Args:
            message_type: Type of messages to handle
            handler: Message handler implementation
            
        Returns:
            True if registration successful
        """
        pass
    
    @abstractmethod
    async def unregister_handler(
        self,
        message_type: str,
        handler: IMessageHandler
    ) -> bool:
        """
        Unregister a message handler
        
        Args:
            message_type: Type of messages
            handler: Message handler to unregister
            
        Returns:
            True if unregistration successful
        """
        pass
    
    @abstractmethod
    async def get_message_status(self, message_id: str) -> Optional[str]:
        """
        Get the status of a message
        
        Args:
            message_id: Message identifier
            
        Returns:
            Message status or None if not found
        """
        pass
    
    @abstractmethod
    async def retry_failed_messages(self, max_age_hours: int = 24) -> int:
        """
        Retry failed messages within the specified age
        
        Args:
            max_age_hours: Maximum age of messages to retry
            
        Returns:
            Number of messages retried
        """
        pass


class IEventBus(ABC):
    """Interface for event bus implementations"""
    
    @abstractmethod
    async def publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source: str,
        target: Optional[str] = None
    ) -> bool:
        """
        Publish an event to the event bus
        
        Args:
            event_type: Type of event
            payload: Event payload
            source: Event source identifier
            target: Optional target identifier
            
        Returns:
            True if publish successful
        """
        pass
    
    @abstractmethod
    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], None],
        filter_pattern: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Subscribe to events of a specific type
        
        Args:
            event_type: Type of events to subscribe to
            handler: Event handler function
            filter_pattern: Optional filter pattern
            
        Returns:
            Subscription identifier
        """
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events
        
        Args:
            subscription_id: Subscription identifier
            
        Returns:
            True if unsubscription successful
        """
        pass


class IMessageQueue(ABC):
    """Interface for message queue implementations"""
    
    @abstractmethod
    async def enqueue(
        self,
        queue_name: str,
        message: Dict[str, Any],
        delay_seconds: int = 0
    ) -> str:
        """
        Enqueue a message
        
        Args:
            queue_name: Queue name
            message: Message to enqueue
            delay_seconds: Delay before message becomes available
            
        Returns:
            Message identifier
        """
        pass
    
    @abstractmethod
    async def dequeue(
        self,
        queue_name: str,
        max_messages: int = 1,
        wait_time_seconds: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Dequeue messages from a queue
        
        Args:
            queue_name: Queue name
            max_messages: Maximum number of messages to retrieve
            wait_time_seconds: Long polling wait time
            
        Returns:
            List of dequeued messages
        """
        pass
    
    @abstractmethod
    async def delete_message(
        self,
        queue_name: str,
        receipt_handle: str
    ) -> bool:
        """
        Delete a message from the queue
        
        Args:
            queue_name: Queue name
            receipt_handle: Message receipt handle
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def get_queue_attributes(self, queue_name: str) -> Dict[str, Any]:
        """
        Get queue attributes
        
        Args:
            queue_name: Queue name
            
        Returns:
            Queue attributes
        """
        pass