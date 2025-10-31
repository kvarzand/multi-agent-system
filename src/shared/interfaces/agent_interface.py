"""
Agent-related interfaces
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from ..models.agent_models import AgentRegistration, AgentHealthCheck
from ..models.message_models import AgentMessage, CrossDivisionRequest, CrossDivisionResponse


class IAgent(ABC):
    """Interface for agent implementations"""
    
    @abstractmethod
    async def invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the agent with a request
        
        Args:
            request: Agent invocation request
            
        Returns:
            Agent response
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> AgentHealthCheck:
        """
        Perform agent health check
        
        Returns:
            Agent health status
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get agent capabilities
        
        Returns:
            List of capability names
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get agent metadata
        
        Returns:
            Agent metadata dictionary
        """
        pass


class IAgentRegistry(ABC):
    """Interface for agent registry implementations"""
    
    @abstractmethod
    async def register_agent(self, agent: AgentRegistration) -> bool:
        """
        Register an agent in the registry
        
        Args:
            agent: Agent registration information
            
        Returns:
            True if registration successful
        """
        pass
    
    @abstractmethod
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if unregistration successful
        """
        pass
    
    @abstractmethod
    async def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        """
        Get agent registration by ID
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent registration or None if not found
        """
        pass
    
    @abstractmethod
    async def list_agents(
        self, 
        division_id: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        is_shareable: Optional[bool] = None
    ) -> List[AgentRegistration]:
        """
        List agents with optional filtering
        
        Args:
            division_id: Filter by division ID
            capabilities: Filter by capabilities
            is_shareable: Filter by shareability
            
        Returns:
            List of matching agent registrations
        """
        pass
    
    @abstractmethod
    async def update_agent_status(self, agent_id: str, status: str) -> bool:
        """
        Update agent status
        
        Args:
            agent_id: Agent identifier
            status: New status
            
        Returns:
            True if update successful
        """
        pass
    
    @abstractmethod
    async def update_heartbeat(self, agent_id: str) -> bool:
        """
        Update agent heartbeat timestamp
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if update successful
        """
        pass
    
    @abstractmethod
    async def discover_agents(
        self,
        query: str,
        division_id: Optional[str] = None,
        requesting_division_id: Optional[str] = None
    ) -> List[AgentRegistration]:
        """
        Discover agents based on query
        
        Args:
            query: Search query
            division_id: Filter by division ID
            requesting_division_id: Division making the request (for permission checks)
            
        Returns:
            List of matching agent registrations
        """
        pass


class ICrossDivisionAgent(ABC):
    """Interface for cross-division agent communication"""
    
    @abstractmethod
    async def invoke_cross_division_agent(
        self,
        request: CrossDivisionRequest
    ) -> CrossDivisionResponse:
        """
        Invoke an agent in another division
        
        Args:
            request: Cross-division invocation request
            
        Returns:
            Cross-division response
        """
        pass
    
    @abstractmethod
    async def handle_cross_division_request(
        self,
        request: CrossDivisionRequest
    ) -> CrossDivisionResponse:
        """
        Handle a cross-division request from another division
        
        Args:
            request: Cross-division request
            
        Returns:
            Cross-division response
        """
        pass