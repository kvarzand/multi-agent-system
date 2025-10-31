"""
Message Router Stack for cross-division communication
"""
import aws_cdk as cdk
from aws_cdk import (
    aws_events as events,
    aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
    aws_events_targets as targets
)
from constructs import Construct


class MessageRouterStack(cdk.Stack):
    """Stack for Message Router infrastructure"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # EventBridge custom bus for agent communications
        self.event_bus = events.EventBus(
            self, "AgentCommunicationBus",
            event_bus_name="multi-agent-communication"
        )
        
        # Dead letter queue for failed messages
        self.dlq = sqs.Queue(
            self, "MessageRouterDLQ",
            queue_name="agent-message-dlq",
            retention_period=cdk.Duration.days(14),
            visibility_timeout=cdk.Duration.seconds(300)
        )
        
        # SQS queues for each division (will be created dynamically)
        # This is a template - actual queues created per division
        self.create_division_queues()
        
        # Lambda function for message routing
        self.router_function = lambda_.Function(
            self, "MessageRouterFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="message_router.handler",
            code=lambda_.Code.from_asset("../src/shared/message-router"),
            environment={
                "EVENT_BUS_NAME": self.event_bus.event_bus_name,
                "DLQ_URL": self.dlq.queue_url,
                "LOG_LEVEL": "INFO"
            },
            timeout=cdk.Duration.seconds(60),
            memory_size=512,
            log_retention=logs.RetentionDays.ONE_MONTH,
            dead_letter_queue=self.dlq
        )
        
        # Grant permissions to router function
        self.event_bus.grant_put_events_to(self.router_function)
        self.dlq.grant_send_messages(self.router_function)
        
        # Lambda function for message processing
        self.processor_function = lambda_.Function(
            self, "MessageProcessorFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="message_processor.handler",
            code=lambda_.Code.from_asset("../src/shared/message-router"),
            environment={
                "EVENT_BUS_NAME": self.event_bus.event_bus_name,
                "LOG_LEVEL": "INFO"
            },
            timeout=cdk.Duration.seconds(300),
            memory_size=1024,
            log_retention=logs.RetentionDays.ONE_MONTH,
            dead_letter_queue=self.dlq
        )
        
        # EventBridge rules for message routing
        self.create_routing_rules()
        
        # IAM role for cross-division message routing
        self.router_role = iam.Role(
            self, "MessageRouterRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        self.event_bus.grant_put_events_to(self.router_role)
        
        # Outputs
        cdk.CfnOutput(
            self, "EventBusName",
            value=self.event_bus.event_bus_name,
            description="EventBridge bus name for agent communications"
        )
        
        cdk.CfnOutput(
            self, "EventBusArn",
            value=self.event_bus.event_bus_arn,
            description="EventBridge bus ARN for agent communications"
        )
        
        cdk.CfnOutput(
            self, "MessageRouterRoleArn",
            value=self.router_role.role_arn,
            description="IAM role ARN for message routing"
        )
    
    def create_division_queues(self):
        """Create SQS queues for division message routing"""
        # Template queues - actual implementation would create these dynamically
        divisions = ["division-a", "division-b"]  # This would come from context
        
        self.division_queues = {}
        
        for division_id in divisions:
            # Main queue for division
            queue = sqs.Queue(
                self, f"{division_id.title().replace('-', '')}MessageQueue",
                queue_name=f"{division_id}-messages",
                visibility_timeout=cdk.Duration.seconds(300),
                retention_period=cdk.Duration.days(14),
                dead_letter_queue=sqs.DeadLetterQueue(
                    max_receive_count=3,
                    queue=self.dlq
                )
            )
            
            self.division_queues[division_id] = queue
            
            # Grant permissions to router function
            queue.grant_send_messages(self.router_function)
            queue.grant_consume_messages(self.processor_function)
    
    def create_routing_rules(self):
        """Create EventBridge rules for message routing"""
        # Rule for cross-division messages
        cross_division_rule = events.Rule(
            self, "CrossDivisionMessageRule",
            event_bus=self.event_bus,
            event_pattern=events.EventPattern(
                source=["multi-agent-system"],
                detail_type=["Agent Message"],
                detail={
                    "messageType": ["request", "response"],
                    "targetDivisionId": events.Match.exists()
                }
            )
        )
        
        cross_division_rule.add_target(
            targets.LambdaFunction(self.processor_function)
        )
        
        # Rule for heartbeat messages
        heartbeat_rule = events.Rule(
            self, "HeartbeatMessageRule",
            event_bus=self.event_bus,
            event_pattern=events.EventPattern(
                source=["multi-agent-system"],
                detail_type=["Agent Heartbeat"]
            )
        )
        
        heartbeat_rule.add_target(
            targets.LambdaFunction(self.processor_function)
        )
        
        # Rule for system events
        system_event_rule = events.Rule(
            self, "SystemEventRule",
            event_bus=self.event_bus,
            event_pattern=events.EventPattern(
                source=["multi-agent-system"],
                detail_type=["System Event"]
            )
        )
        
        system_event_rule.add_target(
            targets.LambdaFunction(self.processor_function)
        )