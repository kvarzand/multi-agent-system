"""
Enterprise Agent Registry Stack
"""
import aws_cdk as cdk
from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_logs as logs
)
from constructs import Construct


class EnterpriseRegistryStack(cdk.Stack):
    """Stack for Enterprise Agent Registry infrastructure"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB table for agent registry with global tables support
        self.registry_table = dynamodb.Table(
            self, "EnterpriseAgentRegistry",
            table_name="enterprise-agent-registry",
            partition_key=dynamodb.Attribute(
                name="agent_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=cdk.RemovalPolicy.RETAIN,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )
        
        # Global Secondary Indexes for efficient querying
        self.registry_table.add_global_secondary_index(
            index_name="division-index",
            partition_key=dynamodb.Attribute(
                name="division_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="agent_name",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        self.registry_table.add_global_secondary_index(
            index_name="capability-index",
            partition_key=dynamodb.Attribute(
                name="capability",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="division_id",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        self.registry_table.add_global_secondary_index(
            index_name="shareable-index",
            partition_key=dynamodb.Attribute(
                name="is_shareable",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="status",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Lambda function for agent registry operations
        self.registry_function = lambda_.Function(
            self, "AgentRegistryFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="agent_registry.handler",
            code=lambda_.Code.from_asset("../src/shared/enterprise-registry"),
            environment={
                "REGISTRY_TABLE_NAME": self.registry_table.table_name,
                "LOG_LEVEL": "INFO"
            },
            timeout=cdk.Duration.seconds(30),
            memory_size=512,
            log_retention=logs.RetentionDays.ONE_MONTH
        )
        
        # Grant permissions to Lambda function
        self.registry_table.grant_read_write_data(self.registry_function)
        
        # API Gateway for registry operations
        self.api = apigateway.RestApi(
            self, "AgentRegistryApi",
            rest_api_name="Enterprise Agent Registry API",
            description="API for managing enterprise agent registry",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )
        
        # API Gateway integration
        registry_integration = apigateway.LambdaIntegration(
            self.registry_function,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )
        
        # API routes
        agents_resource = self.api.root.add_resource("agents")
        agents_resource.add_method("GET", registry_integration)  # List agents
        agents_resource.add_method("POST", registry_integration)  # Register agent
        
        agent_resource = agents_resource.add_resource("{agent_id}")
        agent_resource.add_method("GET", registry_integration)  # Get agent
        agent_resource.add_method("PUT", registry_integration)  # Update agent
        agent_resource.add_method("DELETE", registry_integration)  # Unregister agent
        
        # Discovery endpoint
        discover_resource = self.api.root.add_resource("discover")
        discover_resource.add_method("POST", registry_integration)  # Discover agents
        
        # Health check endpoint
        health_resource = agent_resource.add_resource("health")
        health_resource.add_method("POST", registry_integration)  # Update heartbeat
        
        # IAM role for cross-division access
        self.cross_division_role = iam.Role(
            self, "CrossDivisionAccessRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        self.registry_table.grant_read_data(self.cross_division_role)
        
        # Outputs
        cdk.CfnOutput(
            self, "RegistryTableName",
            value=self.registry_table.table_name,
            description="Enterprise Agent Registry table name"
        )
        
        cdk.CfnOutput(
            self, "RegistryApiEndpoint",
            value=self.api.url,
            description="Enterprise Agent Registry API endpoint"
        )
        
        cdk.CfnOutput(
            self, "CrossDivisionRoleArn",
            value=self.cross_division_role.role_arn,
            description="IAM role ARN for cross-division access"
        )