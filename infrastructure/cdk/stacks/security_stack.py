"""
Security and Compliance Stack
"""
import aws_cdk as cdk
from aws_cdk import (
    aws_kms as kms,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_wafv2 as wafv2,
    aws_cloudtrail as cloudtrail,
    aws_s3 as s3,
    aws_logs as logs
)
from constructs import Construct


class SecurityStack(cdk.Stack):
    """Stack for security and compliance infrastructure"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # KMS key for encryption
        self.encryption_key = kms.Key(
            self, "MultiAgentSystemKey",
            description="KMS key for Multi-Agent System encryption",
            enable_key_rotation=True,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # KMS key alias
        self.key_alias = kms.Alias(
            self, "MultiAgentSystemKeyAlias",
            alias_name="alias/multi-agent-system",
            target_key=self.encryption_key
        )
        
        # Secrets Manager for sensitive configuration
        self.system_secrets = secretsmanager.Secret(
            self, "SystemSecrets",
            secret_name="multi-agent-system/config",
            description="Sensitive configuration for Multi-Agent System",
            encryption_key=self.encryption_key,
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"api_keys": {}}',
                generate_string_key="master_key",
                exclude_characters=" %+~`#$&*()|[]{}:;<>?!'/\"\\",
                include_space=False,
                password_length=32
            )
        )
        
        # S3 bucket for CloudTrail logs
        self.audit_log_bucket = s3.Bucket(
            self, "AuditLogBucket",
            bucket_name=f"multi-agent-audit-logs-{self.account}",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.encryption_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="audit-log-lifecycle",
                    enabled=True,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=cdk.Duration.days(30)
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=cdk.Duration.days(90)
                        )
                    ],
                    expiration=cdk.Duration.days(2555)  # 7 years retention
                )
            ],
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # CloudTrail for API logging
        self.cloudtrail = cloudtrail.Trail(
            self, "MultiAgentSystemTrail",
            trail_name="multi-agent-system-trail",
            bucket=self.audit_log_bucket,
            encryption_key=self.encryption_key,
            include_global_service_events=True,
            is_multi_region_trail=True,
            enable_file_validation=True,
            send_to_cloud_watch_logs=True,
            cloud_watch_logs_retention=logs.RetentionDays.ONE_YEAR
        )
        
        # WAF Web ACL for API protection
        self.web_acl = wafv2.CfnWebACL(
            self, "MultiAgentSystemWebACL",
            name="multi-agent-system-waf",
            scope="REGIONAL",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(
                allow={}
            ),
            rules=[
                # Rate limiting rule
                wafv2.CfnWebACL.RuleProperty(
                    name="RateLimitRule",
                    priority=1,
                    statement=wafv2.CfnWebACL.StatementProperty(
                        rate_based_statement=wafv2.CfnWebACL.RateBasedStatementProperty(
                            limit=2000,  # 2000 requests per 5 minutes
                            aggregate_key_type="IP"
                        )
                    ),
                    action=wafv2.CfnWebACL.RuleActionProperty(
                        block={}
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="RateLimitRule"
                    )
                ),
                # AWS managed rules for common attacks
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedRulesCommonRuleSet",
                    priority=2,
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(
                        none={}
                    ),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name="AWS",
                            name="AWSManagedRulesCommonRuleSet"
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="CommonRuleSetMetric"
                    )
                ),
                # AWS managed rules for known bad inputs
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedRulesKnownBadInputsRuleSet",
                    priority=3,
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(
                        none={}
                    ),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name="AWS",
                            name="AWSManagedRulesKnownBadInputsRuleSet"
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="KnownBadInputsRuleSetMetric"
                    )
                )
            ],
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True,
                cloud_watch_metrics_enabled=True,
                metric_name="MultiAgentSystemWebACL"
            )
        )
        
        # IAM roles for different components
        self.create_iam_roles()
        
        # Outputs
        cdk.CfnOutput(
            self, "EncryptionKeyId",
            value=self.encryption_key.key_id,
            description="KMS key ID for encryption"
        )
        
        cdk.CfnOutput(
            self, "EncryptionKeyArn",
            value=self.encryption_key.key_arn,
            description="KMS key ARN for encryption"
        )
        
        cdk.CfnOutput(
            self, "SystemSecretsArn",
            value=self.system_secrets.secret_arn,
            description="Secrets Manager ARN for system secrets"
        )
        
        cdk.CfnOutput(
            self, "WebACLArn",
            value=self.web_acl.attr_arn,
            description="WAF Web ACL ARN"
        )
        
        cdk.CfnOutput(
            self, "AuditLogBucket",
            value=self.audit_log_bucket.bucket_name,
            description="S3 bucket for audit logs"
        )
    
    def create_iam_roles(self):
        """Create IAM roles for different system components"""
        
        # Role for agent execution
        self.agent_execution_role = iam.Role(
            self, "AgentExecutionRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("lambda.amazonaws.com"),
                iam.ServicePrincipal("bedrock.amazonaws.com")
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Grant access to KMS key
        self.encryption_key.grant_encrypt_decrypt(self.agent_execution_role)
        
        # Grant access to secrets
        self.system_secrets.grant_read(self.agent_execution_role)
        
        # Role for cross-division communication
        self.cross_division_role = iam.Role(
            self, "CrossDivisionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Grant limited cross-division permissions
        self.cross_division_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeAgent",
                    "events:PutEvents"
                ],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "aws:RequestedRegion": self.region
                    }
                }
            )
        )
        
        # Role for monitoring and observability
        self.monitoring_role = iam.Role(
            self, "MonitoringRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy")
            ]
        )
        
        self.monitoring_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cloudwatch:PutMetricData",
                    "cloudwatch:GetMetricStatistics",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:FilterLogEvents"
                ],
                resources=["*"]
            )
        )
        
        # Role for tool execution with restricted permissions
        self.tool_execution_role = iam.Role(
            self, "ToolExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Grant minimal permissions for tool execution
        self.tool_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "lambda:InvokeFunction"
                ],
                resources=["*"],
                conditions={
                    "StringLike": {
                        "lambda:FunctionName": "tool-*"
                    }
                }
            )
        )
        
        # Output role ARNs
        cdk.CfnOutput(
            self, "AgentExecutionRoleArn",
            value=self.agent_execution_role.role_arn,
            description="IAM role ARN for agent execution"
        )
        
        cdk.CfnOutput(
            self, "CrossDivisionRoleArn",
            value=self.cross_division_role.role_arn,
            description="IAM role ARN for cross-division communication"
        )
        
        cdk.CfnOutput(
            self, "MonitoringRoleArn",
            value=self.monitoring_role.role_arn,
            description="IAM role ARN for monitoring"
        )
        
        cdk.CfnOutput(
            self, "ToolExecutionRoleArn",
            value=self.tool_execution_role.role_arn,
            description="IAM role ARN for tool execution"
        )