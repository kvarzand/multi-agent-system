"""
Common interfaces for the Multi-Agent System
"""
from .agent_interface import IAgent, IAgentRegistry
from .message_interface import IMessageRouter, IMessageHandler
from .tool_interface import IToolRegistry, IToolExecutor
from .gateway_interface import IDivisionGateway

__all__ = [
    "IAgent",
    "IAgentRegistry", 
    "IMessageRouter",
    "IMessageHandler",
    "IToolRegistry",
    "IToolExecutor",
    "IDivisionGateway"
]