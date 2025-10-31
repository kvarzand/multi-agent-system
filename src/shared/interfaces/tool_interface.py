"""
Tool registry and execution interfaces
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from ..models.tool_models import ToolDefinition, ToolExecution, ToolInvocationRequest, ToolInvocationResponse


class IToolExecutor(ABC):
    """Interface for tool execution implementations"""
    
    @abstractmethod
    async def execute_tool(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool with given parameters
        
        Args:
            tool_id: Tool identifier
            parameters: Tool input parameters
            context: Optional execution context
            
        Returns:
            Tool execution result
        """
        pass
    
    @abstractmethod
    async def validate_parameters(
        self,
        tool_id: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Validate tool input parameters against schema
        
        Args:
            tool_id: Tool identifier
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid
        """
        pass
    
    @abstractmethod
    async def get_execution_status(self, execution_id: str) -> Optional[str]:
        """
        Get the status of a tool execution
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Execution status or None if not found
        """
        pass
    
    @abstractmethod
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running tool execution
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            True if cancellation successful
        """
        pass


class IToolRegistry(ABC):
    """Interface for tool registry implementations"""
    
    @abstractmethod
    async def register_tool(self, tool: ToolDefinition) -> bool:
        """
        Register a tool in the registry
        
        Args:
            tool: Tool definition
            
        Returns:
            True if registration successful
        """
        pass
    
    @abstractmethod
    async def unregister_tool(self, tool_id: str) -> bool:
        """
        Unregister a tool from the registry
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            True if unregistration successful
        """
        pass
    
    @abstractmethod
    async def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        """
        Get tool definition by ID
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Tool definition or None if not found
        """
        pass
    
    @abstractmethod
    async def list_tools(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        division_id: Optional[str] = None
    ) -> List[ToolDefinition]:
        """
        List tools with optional filtering
        
        Args:
            category: Filter by category
            tags: Filter by tags
            division_id: Filter by division access
            
        Returns:
            List of matching tool definitions
        """
        pass
    
    @abstractmethod
    async def search_tools(
        self,
        query: str,
        division_id: Optional[str] = None
    ) -> List[ToolDefinition]:
        """
        Search tools by query
        
        Args:
            query: Search query
            division_id: Division making the request (for permission checks)
            
        Returns:
            List of matching tool definitions
        """
        pass
    
    @abstractmethod
    async def update_tool(self, tool: ToolDefinition) -> bool:
        """
        Update tool definition
        
        Args:
            tool: Updated tool definition
            
        Returns:
            True if update successful
        """
        pass
    
    @abstractmethod
    async def check_tool_permissions(
        self,
        tool_id: str,
        division_id: str
    ) -> bool:
        """
        Check if a division has permission to use a tool
        
        Args:
            tool_id: Tool identifier
            division_id: Division identifier
            
        Returns:
            True if permission granted
        """
        pass


class IToolInvoker(ABC):
    """Interface for tool invocation (combines registry and executor)"""
    
    @abstractmethod
    async def invoke_tool(
        self,
        request: ToolInvocationRequest
    ) -> ToolInvocationResponse:
        """
        Invoke a tool with the given request
        
        Args:
            request: Tool invocation request
            
        Returns:
            Tool invocation response
        """
        pass
    
    @abstractmethod
    async def get_tool_schema(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tool input/output schema
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Tool schema or None if not found
        """
        pass
    
    @abstractmethod
    async def list_available_tools(
        self,
        division_id: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List tools available to a division
        
        Args:
            division_id: Division identifier
            category: Optional category filter
            
        Returns:
            List of available tools with metadata
        """
        pass


class IAsyncToolExecutor(ABC):
    """Interface for asynchronous tool execution"""
    
    @abstractmethod
    async def submit_tool_execution(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        callback_url: Optional[str] = None
    ) -> str:
        """
        Submit a tool for asynchronous execution
        
        Args:
            tool_id: Tool identifier
            parameters: Tool input parameters
            callback_url: Optional callback URL for results
            
        Returns:
            Execution identifier
        """
        pass
    
    @abstractmethod
    async def get_execution_result(
        self,
        execution_id: str
    ) -> Optional[ToolExecution]:
        """
        Get the result of an asynchronous execution
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Tool execution result or None if not found
        """
        pass
    
    @abstractmethod
    async def list_executions(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[ToolExecution]:
        """
        List tool executions with optional filtering
        
        Args:
            agent_id: Filter by requesting agent
            status: Filter by execution status
            limit: Maximum number of results
            
        Returns:
            List of tool executions
        """
        pass