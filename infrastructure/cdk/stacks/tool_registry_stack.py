"""
Tool Registry Stack
"""
import aws_cdk as cdk
from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_logs as logs,
    aws_s3 as s3
)
from constructs import Construct


class ToolRegistryStack(cdk.Stack):
    """Stack for Tool Registry infrastructure"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB table for tool registry
        self.tool_registry_table = dynamodb.Table(
            self, "ToolRegistry",
            table_name="tool-registry",
            partition_key=dynamodb.Attribute(
                name="tool_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # GSI for category-based queries
        self.tool_registry_table.add_global_secondary_index(
            index_name="category-index",
            partition_key=dynamodb.Attribute(
                name="category",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="name",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # GSI for permission-based queries
        self.tool_registry_table.add_global_secondary_index(
            index_name="permission-index",
            partition_key=dynamodb.Attribute(
                name="division_permission",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="is_active",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # DynamoDB table for tool executions
        self.tool_execution_table = dynamodb.Table(
            self, "ToolExecutions",
            table_name="tool-executions",
            partition_key=dynamodb.Attribute(
                name="execution_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=cdk.RemovalPolicy.RETAIN,
            time_to_live_attribute="ttl"
        )
        
        # GSI for agent-based execution queries
        self.tool_execution_table.add_global_secondary_index(
            index_name="agent-index",
            partition_key=dynamodb.Attribute(
                name="requesting_agent_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="started_at",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # S3 bucket for tool schemas and artifacts
        self.tool_artifacts_bucket = s3.Bucket(
            self, "ToolArtifactsBucket",
            bucket_name=f"tool-artifacts-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # Lambda function for tool registry operations
        self.registry_function = lambda_.Function(
            self, "ToolRegistryFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="tool_registry.handler",
            code=lambda_.Code.from_asset("../src/tools/registry"),
            environment={
                "TOOL_REGISTRY_TABLE": self.tool_registry_table.table_name,
                "TOOL_EXECUTION_TABLE": self.tool_execution_table.table_name,
                "TOOL_ARTIFACTS_BUCKET": self.tool_artifacts_bucket.bucket_name,
                "LOG_LEVEL": "INFO"
            },
            timeout=cdk.Duration.seconds(30),
            memory_size=512,
            log_retention=logs.RetentionDays.ONE_MONTH
        )
        
        # Lambda function for tool execution
        self.executor_function = lambda_.Function(
            self, "ToolExecutorFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="tool_executor.handler",
            code=lambda_.Code.from_asset("../src/tools/executors"),
            environment={
                "TOOL_REGISTRY_TABLE": self.tool_registry_table.table_name,
                "TOOL_EXECUTION_TABLE": self.tool_execution_table.table_name,
                "TOOL_ARTIFACTS_BUCKET": self.tool_artifacts_bucket.bucket_name,
                "LOG_LEVEL": "INFO"
            },
            timeout=cdk.Duration.seconds(300),
            memory_size=1024,
            log_retention=logs.RetentionDays.ONE_MONTH
        )
        
        # Grant permissions
        self.tool_registry_table.grant_read_write_data(self.registry_function)
        self.tool_registry_table.grant_read_data(self.executor_function)
        self.tool_execution_table.grant_read_write_data(self.registry_function)
        self.tool_execution_table.grant_read_write_data(self.executor_function)
        self.tool_artifacts_bucket.grant_read_write(self.registry_function)
        self.tool_artifacts_bucket.grant_read(self.executor_function)
        
        # Grant executor function permission to invoke other Lambda functions
        self.executor_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["lambda:InvokeFunction"],
                resources=["*"]  # This would be more restrictive in production
            )
        )
        
        # API Gateway for tool registry
        self.api = apigateway.RestApi(
            self, "ToolRegistryApi",
            rest_api_name="Tool Registry API",
            description="API for managing tool registry and execution",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )
        
        # API Gateway integrations
        registry_integration = apigateway.LambdaIntegration(self.registry_function)
        executor_integration = apigateway.LambdaIntegration(self.executor_function)
        
        # API routes for tool registry
        tools_resource = self.api.root.add_resource("tools")
        tools_resource.add_method("GET", registry_integration)  # List tools
        tools_resource.add_method("POST", registry_integration)  # Register tool
        
        tool_resource = tools_resource.add_resource("{tool_id}")
        tool_resource.add_method("GET", registry_integration)  # Get tool
        tool_resource.add_method("PUT", registry_integration)  # Update tool
        tool_resource.add_method("DELETE", registry_integration)  # Unregister tool
        
        # API routes for tool execution
        execute_resource = tool_resource.add_resource("execute")
        execute_resource.add_method("POST", executor_integration)  # Execute tool
        
        executions_resource = self.api.root.add_resource("executions")
        executions_resource.add_method("GET", executor_integration)  # List executions
        
        execution_resource = executions_resource.add_resource("{execution_id}")
        execution_resource.add_method("GET", executor_integration)  # Get execution
        execution_resource.add_method("DELETE", executor_integration)  # Cancel execution
        
        # Search endpoint
        search_resource = self.api.root.add_resource("search")
        search_resource.add_method("POST", registry_integration)  # Search tools
        
        # IAM role for tool execution
        self.tool_execution_role = iam.Role(
            self, "ToolExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        self.tool_registry_table.grant_read_data(self.tool_execution_role)
        self.tool_execution_table.grant_read_write_data(self.tool_execution_role)
        
        # Outputs
        cdk.CfnOutput(
            self, "ToolRegistryTableName",
            value=self.tool_registry_table.table_name,
            description="Tool Registry table name"
        )
        
        cdk.CfnOutput(
            self, "ToolExecutionTableName",
            value=self.tool_execution_table.table_name,
            description="Tool Execution table name"
        )
        
        cdk.CfnOutput(
            self, "ToolRegistryApiEndpoint",
            value=self.api.url,
            description="Tool Registry API endpoint"
        )
        
        cdk.CfnOutput(
            self, "ToolArtifactsBucket",
            value=self.tool_artifacts_bucket.bucket_name,
            description="S3 bucket for tool artifacts"
        )
        
        cdk.CfnOutput(
            self, "ToolExecutionRoleArn",
            value=self.tool_execution_role.role_arn,
            description="IAM role ARN for tool execution"
        )