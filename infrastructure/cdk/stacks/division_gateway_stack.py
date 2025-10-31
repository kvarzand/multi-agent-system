"""
Division Gateway Stack using Amazon Bedrock Gateway
"""
import aws_cdk as cdk
from aws_cdk import (
    aws_bedrock as bedrock,
    aws_cognito as cognito,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_events as events
)
from constructs import Construct


class DivisionGatewayStack(cdk.Stack):
    """Stack for Division Gateway using Amazon Bedrock Gateway"""
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str,
        division_id: str,
        enterprise_registry_table: dynamodb.Table,
        message_router_bus: events.EventBus,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.division_id = division_id
        
        # Cognito User Pool for authentication
        self.user_pool = cognito.UserPool(
            self, f"{division_id}UserPool",
            user_pool_name=f"{division_id}-agent-pool",
            sign_in_aliases=cognito.SignInAliases(
                username=True,
                email=True
            ),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # User Pool Client
        self.user_pool_client = self.user_pool.add_client(
            f"{division_id}UserPoolClient",
            user_pool_client_name=f"{division_id}-gateway-client",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
                admin_user_password=True
            ),
            generate_secret=True
        )
        
        # S3 bucket for agent artifacts and knowledge bases
        self.artifacts_bucket = s3.Bucket(
            self, f"{division_id}ArtifactsBucket",
            bucket_name=f"{division_id}-agent-artifacts-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # DynamoDB table for division-specific agent registry
        self.division_registry_table = dynamodb.Table(
            self, f"{division_id}AgentRegistry",
            table_name=f"{division_id}-agent-registry",
            partition_key=dynamodb.Attribute(
                name="agent_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # IAM role for Bedrock Gateway
        self.gateway_role = iam.Role(
            self, f"{division_id}GatewayRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("bedrock.amazonaws.com"),
                iam.ServicePrincipal("lambda.amazonaws.com")
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Grant permissions for Bedrock operations
        self.gateway_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeAgent",
                    "bedrock:InvokeModel",
                    "bedrock:GetAgent",
                    "bedrock:ListAgents",
                    "bedrock:GetKnowledgeBase",
                    "bedrock:ListKnowledgeBases"
                ],
                resources=["*"]
            )
        )
        
        # Grant access to S3 bucket
        self.artifacts_bucket.grant_read_write(self.gateway_role)
        
        # Grant access to registries
        enterprise_registry_table.grant_read_data(self.gateway_role)
        self.division_registry_table.grant_read_write_data(self.gateway_role)
        
        # Grant access to message router
        message_router_bus.grant_put_events_to(self.gateway_role)
        
        # Lambda function for gateway operations
        self.gateway_function = lambda_.Function(
            self, f"{division_id}GatewayFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="division_gateway.handler",
            code=lambda_.Code.from_asset("../src/division-gateways"),
            environment={
                "DIVISION_ID": division_id,
                "USER_POOL_ID": self.user_pool.user_pool_id,
                "USER_POOL_CLIENT_ID": self.user_pool_client.user_pool_client_id,
                "ARTIFACTS_BUCKET": self.artifacts_bucket.bucket_name,
                "DIVISION_REGISTRY_TABLE": self.division_registry_table.table_name,
                "ENTERPRISE_REGISTRY_TABLE": enterprise_registry_table.table_name,
                "MESSAGE_ROUTER_BUS": message_router_bus.event_bus_name,
                "LOG_LEVEL": "INFO"
            },
            role=self.gateway_role,
            timeout=cdk.Duration.seconds(300),
            memory_size=1024,
            log_retention=logs.RetentionDays.ONE_MONTH
        )
        
        # Lambda function for cross-division communication
        self.federation_function = lambda_.Function(
            self, f"{division_id}FederationFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="federation.handler",
            code=lambda_.Code.from_asset("../src/division-gateways/federation"),
            environment={
                "DIVISION_ID": division_id,
                "ENTERPRISE_REGISTRY_TABLE": enterprise_registry_table.table_name,
                "MESSAGE_ROUTER_BUS": message_router_bus.event_bus_name,
                "LOG_LEVEL": "INFO"
            },
            role=self.gateway_role,
            timeout=cdk.Duration.seconds(60),
            memory_size=512,
            log_retention=logs.RetentionDays.ONE_MONTH
        )
        
        # Note: Bedrock Gateway configuration would be done through AWS Console or CLI
        # as CDK doesn't yet have full support for Bedrock Gateway constructs
        
        # CloudWatch Log Group for Bedrock Gateway logs
        self.gateway_log_group = logs.LogGroup(
            self, f"{division_id}GatewayLogs",
            log_group_name=f"/aws/bedrock/gateway/{division_id}",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # Outputs
        cdk.CfnOutput(
            self, f"{division_id}UserPoolId",
            value=self.user_pool.user_pool_id,
            description=f"Cognito User Pool ID for {division_id}"
        )
        
        cdk.CfnOutput(
            self, f"{division_id}UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            description=f"Cognito User Pool Client ID for {division_id}"
        )
        
        cdk.CfnOutput(
            self, f"{division_id}ArtifactsBucket",
            value=self.artifacts_bucket.bucket_name,
            description=f"S3 bucket for {division_id} agent artifacts"
        )
        
        cdk.CfnOutput(
            self, f"{division_id}GatewayRoleArn",
            value=self.gateway_role.role_arn,
            description=f"IAM role ARN for {division_id} gateway"
        )
        
        cdk.CfnOutput(
            self, f"{division_id}DivisionRegistryTable",
            value=self.division_registry_table.table_name,
            description=f"Division registry table for {division_id}"
        )