"""
Division Gateway interface
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from ..models.agent_models import AgentRegistration
from ..models.message_models import CrossDivisionRequest, CrossDivisionResponse
from ..models.division_models import DivisionConfig, DivisionStatus


class IDivisionGateway(ABC):
    """Interface for Division Gateway implementations"""
    
    @abstractmethod
    async def invoke_agent(
        self,
        agent_id: str,
        request: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke an agent within this division
        
        Args:
            agent_id: Agent identifier
            request: Agent invocation request
            session_id: Optional session identifier for conversation continuity
            
        Returns:
            Agent response
        """
        pass
    
    @abstractmethod
    async def start_session(
        self,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a conversation session with an agent
        
        Args:
            agent_id: Agent identifier
            context: Optional session context
            
        Returns:
            Session identifier
        """
        pass
    
    @abstractmethod
    async def end_session(self, session_id: str) -> bool:
        """
        End a conversation session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session ended successfully
        """
        pass
    
    @abstractmethod
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session status and metadata
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session status or None if not found
        """
        pass
    
    @abstractmethod
    async def list_division_agents(self) -> List[AgentRegistration]:
        """
        List all agents in this division
        
        Returns:
            List of agent registrations
        """
        pass
    
    @abstractmethod
    async def discover_agents(
        self,
        query: str,
        include_cross_division: bool = True
    ) -> List[AgentRegistration]:
        """
        Discover agents based on query
        
        Args:
            query: Search query
            include_cross_division: Include agents from other divisions
            
        Returns:
            List of matching agent registrations
        """
        pass
    
    @abstractmethod
    async def handle_cross_division_request(
        self,
        request: CrossDivisionRequest
    ) -> CrossDivisionResponse:
        """
        Handle a request from another division
        
        Args:
            request: Cross-division request
            
        Returns:
            Cross-division response
        """
        pass
    
    @abstractmethod
    async def send_cross_division_request(
        self,
        request: CrossDivisionRequest
    ) -> CrossDivisionResponse:
        """
        Send a request to another division
        
        Args:
            request: Cross-division request
            
        Returns:
            Cross-division response
        """
        pass
    
    @abstractmethod
    async def get_division_status(self) -> DivisionStatus:
        """
        Get the status of this division
        
        Returns:
            Division status
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform gateway health check
        
        Returns:
            Health check results
        """
        pass


class IGatewayFederation(ABC):
    """Interface for gateway federation capabilities"""
    
    @abstractmethod
    async def register_trusted_division(
        self,
        division_id: str,
        gateway_endpoint: str,
        permissions: List[str]
    ) -> bool:
        """
        Register a trusted division for federation
        
        Args:
            division_id: Division identifier
            gateway_endpoint: Gateway endpoint URL
            permissions: List of permissions granted
            
        Returns:
            True if registration successful
        """
        pass
    
    @abstractmethod
    async def unregister_trusted_division(self, division_id: str) -> bool:
        """
        Unregister a trusted division
        
        Args:
            division_id: Division identifier
            
        Returns:
            True if unregistration successful
        """
        pass
    
    @abstractmethod
    async def get_trusted_divisions(self) -> List[Dict[str, Any]]:
        """
        Get list of trusted divisions
        
        Returns:
            List of trusted division configurations
        """
        pass
    
    @abstractmethod
    async def validate_cross_division_access(
        self,
        source_division_id: str,
        target_agent_id: str,
        action: str
    ) -> bool:
        """
        Validate cross-division access permissions
        
        Args:
            source_division_id: Source division identifier
            target_agent_id: Target agent identifier
            action: Action being performed
            
        Returns:
            True if access is allowed
        """
        pass


class IGatewayAuth(ABC):
    """Interface for gateway authentication and authorization"""
    
    @abstractmethod
    async def authenticate_request(
        self,
        token: str,
        request_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate an incoming request
        
        Args:
            token: Authentication token
            request_context: Request context
            
        Returns:
            User/agent identity or None if authentication failed
        """
        pass
    
    @abstractmethod
    async def authorize_action(
        self,
        identity: Dict[str, Any],
        action: str,
        resource: str
    ) -> bool:
        """
        Authorize an action for an authenticated identity
        
        Args:
            identity: Authenticated identity
            action: Action to authorize
            resource: Resource being accessed
            
        Returns:
            True if action is authorized
        """
        pass
    
    @abstractmethod
    async def generate_token(
        self,
        identity: Dict[str, Any],
        expires_in: int = 3600
    ) -> str:
        """
        Generate an authentication token
        
        Args:
            identity: Identity to generate token for
            expires_in: Token expiration time in seconds
            
        Returns:
            Authentication token
        """
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate an authentication token
        
        Args:
            token: Token to validate
            
        Returns:
            Token payload or None if invalid
        """
        pass