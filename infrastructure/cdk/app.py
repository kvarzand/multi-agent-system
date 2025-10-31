#!/usr/bin/env python3
"""
AWS CDK App for Multi-Agent System Infrastructure
"""
import aws_cdk as cdk
from constructs import Construct

from stacks.enterprise_registry_stack import EnterpriseRegistryStack
from stacks.division_gateway_stack import DivisionGatewayStack
from stacks.message_router_stack import MessageRouterStack
from stacks.tool_registry_stack import ToolRegistryStack
from stacks.monitoring_stack import MonitoringStack
from stacks.security_stack import SecurityStack


class MultiAgentSystemApp(cdk.App):
    def __init__(self):
        super().__init__()
        
        # Environment configuration
        env = cdk.Environment(
            account=self.node.try_get_context("account"),
            region=self.node.try_get_context("region") or "us-east-1"
        )
        
        # Security stack (foundational)
        security_stack = SecurityStack(
            self, "MultiAgentSystemSecurity",
            env=env,
            description="Security and IAM resources for Multi-Agent System"
        )
        
        # Enterprise Registry stack
        enterprise_registry_stack = EnterpriseRegistryStack(
            self, "MultiAgentSystemEnterpriseRegistry",
            env=env,
            description="Enterprise Agent Registry for Multi-Agent System"
        )
        
        # Message Router stack
        message_router_stack = MessageRouterStack(
            self, "MultiAgentSystemMessageRouter",
            env=env,
            description="Message routing infrastructure for Multi-Agent System"
        )
        
        # Tool Registry stack
        tool_registry_stack = ToolRegistryStack(
            self, "MultiAgentSystemToolRegistry",
            env=env,
            description="Tool registry and execution infrastructure"
        )
        
        # Monitoring stack
        monitoring_stack = MonitoringStack(
            self, "MultiAgentSystemMonitoring",
            env=env,
            description="Monitoring and observability for Multi-Agent System"
        )
        
        # Division Gateway stacks (can be deployed per division)
        divisions = self.node.try_get_context("divisions") or ["division-a", "division-b"]
        
        for division_id in divisions:
            DivisionGatewayStack(
                self, f"MultiAgentSystem{division_id.title().replace('-', '')}Gateway",
                division_id=division_id,
                enterprise_registry_table=enterprise_registry_stack.registry_table,
                message_router_bus=message_router_stack.event_bus,
                env=env,
                description=f"Division Gateway for {division_id}"
            )


if __name__ == "__main__":
    app = MultiAgentSystemApp()
    app.synth()