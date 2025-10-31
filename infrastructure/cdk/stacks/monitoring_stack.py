"""
Monitoring and Observability Stack
"""
import aws_cdk as cdk
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_logs as logs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets
)
from constructs import Construct


class MonitoringStack(cdk.Stack):
    """Stack for monitoring and observability infrastructure"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # SNS topic for alerts
        self.alert_topic = sns.Topic(
            self, "SystemAlerts",
            topic_name="multi-agent-system-alerts",
            display_name="Multi-Agent System Alerts"
        )
        
        # CloudWatch Log Groups
        self.system_log_group = logs.LogGroup(
            self, "SystemLogs",
            log_group_name="/aws/multi-agent-system/system",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        self.agent_log_group = logs.LogGroup(
            self, "AgentLogs",
            log_group_name="/aws/multi-agent-system/agents",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # Custom metrics namespace
        self.metrics_namespace = "MultiAgentSystem"
        
        # Lambda function for custom metrics collection
        self.metrics_collector = lambda_.Function(
            self, "MetricsCollector",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="metrics_collector.handler",
            code=lambda_.Code.from_asset("../src/shared/monitoring"),
            environment={
                "METRICS_NAMESPACE": self.metrics_namespace,
                "ALERT_TOPIC_ARN": self.alert_topic.topic_arn,
                "LOG_LEVEL": "INFO"
            },
            timeout=cdk.Duration.seconds(60),
            memory_size=512,
            log_retention=logs.RetentionDays.ONE_MONTH
        )
        
        # Grant permissions to metrics collector
        self.metrics_collector.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cloudwatch:PutMetricData",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics"
                ],
                resources=["*"]
            )
        )
        
        self.alert_topic.grant_publish(self.metrics_collector)
        
        # EventBridge rule to trigger metrics collection
        metrics_rule = events.Rule(
            self, "MetricsCollectionRule",
            schedule=events.Schedule.rate(cdk.Duration.minutes(5))
        )
        
        metrics_rule.add_target(
            targets.LambdaFunction(self.metrics_collector)
        )
        
        # CloudWatch Dashboard
        self.dashboard = cloudwatch.Dashboard(
            self, "MultiAgentSystemDashboard",
            dashboard_name="MultiAgentSystem"
        )
        
        # Add widgets to dashboard
        self.create_dashboard_widgets()
        
        # CloudWatch Alarms
        self.create_alarms()
        
        # Lambda function for log analysis
        self.log_analyzer = lambda_.Function(
            self, "LogAnalyzer",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="log_analyzer.handler",
            code=lambda_.Code.from_asset("../src/shared/monitoring"),
            environment={
                "METRICS_NAMESPACE": self.metrics_namespace,
                "ALERT_TOPIC_ARN": self.alert_topic.topic_arn,
                "LOG_LEVEL": "INFO"
            },
            timeout=cdk.Duration.seconds(300),
            memory_size=1024,
            log_retention=logs.RetentionDays.ONE_MONTH
        )
        
        # Grant permissions to log analyzer
        self.log_analyzer.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams",
                    "logs:FilterLogEvents"
                ],
                resources=["*"]
            )
        )
        
        self.log_analyzer.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cloudwatch:PutMetricData"
                ],
                resources=["*"]
            )
        )
        
        self.alert_topic.grant_publish(self.log_analyzer)
        
        # Outputs
        cdk.CfnOutput(
            self, "AlertTopicArn",
            value=self.alert_topic.topic_arn,
            description="SNS topic ARN for system alerts"
        )
        
        cdk.CfnOutput(
            self, "DashboardUrl",
            value=f"https://console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name={self.dashboard.dashboard_name}",
            description="CloudWatch Dashboard URL"
        )
        
        cdk.CfnOutput(
            self, "MetricsNamespace",
            value=self.metrics_namespace,
            description="CloudWatch metrics namespace"
        )
    
    def create_dashboard_widgets(self):
        """Create CloudWatch Dashboard widgets"""
        
        # System overview widget
        system_overview = cloudwatch.GraphWidget(
            title="System Overview",
            left=[
                cloudwatch.Metric(
                    namespace=self.metrics_namespace,
                    metric_name="ActiveAgents",
                    statistic="Average"
                ),
                cloudwatch.Metric(
                    namespace=self.metrics_namespace,
                    metric_name="TotalRequests",
                    statistic="Sum"
                )
            ],
            right=[
                cloudwatch.Metric(
                    namespace=self.metrics_namespace,
                    metric_name="ErrorRate",
                    statistic="Average"
                )
            ]
        )
        
        # Response time widget
        response_time = cloudwatch.GraphWidget(
            title="Response Times",
            left=[
                cloudwatch.Metric(
                    namespace=self.metrics_namespace,
                    metric_name="ResponseTime",
                    statistic="Average"
                ),
                cloudwatch.Metric(
                    namespace=self.metrics_namespace,
                    metric_name="ResponseTime",
                    statistic="p95"
                )
            ]
        )
        
        # Division-specific metrics
        division_metrics = cloudwatch.GraphWidget(
            title="Division Metrics",
            left=[
                cloudwatch.Metric(
                    namespace=self.metrics_namespace,
                    metric_name="DivisionRequests",
                    dimensions_map={"Division": "division-a"},
                    statistic="Sum"
                ),
                cloudwatch.Metric(
                    namespace=self.metrics_namespace,
                    metric_name="DivisionRequests",
                    dimensions_map={"Division": "division-b"},
                    statistic="Sum"
                )
            ]
        )
        
        # Tool execution metrics
        tool_metrics = cloudwatch.GraphWidget(
            title="Tool Execution Metrics",
            left=[
                cloudwatch.Metric(
                    namespace=self.metrics_namespace,
                    metric_name="ToolExecutions",
                    statistic="Sum"
                ),
                cloudwatch.Metric(
                    namespace=self.metrics_namespace,
                    metric_name="ToolExecutionDuration",
                    statistic="Average"
                )
            ]
        )
        
        # Add widgets to dashboard
        self.dashboard.add_widgets(
            system_overview,
            response_time,
            division_metrics,
            tool_metrics
        )
    
    def create_alarms(self):
        """Create CloudWatch Alarms"""
        
        # High error rate alarm
        error_rate_alarm = cloudwatch.Alarm(
            self, "HighErrorRateAlarm",
            alarm_name="MultiAgentSystem-HighErrorRate",
            alarm_description="High error rate detected in multi-agent system",
            metric=cloudwatch.Metric(
                namespace=self.metrics_namespace,
                metric_name="ErrorRate",
                statistic="Average"
            ),
            threshold=5.0,  # 5% error rate
            evaluation_periods=2,
            datapoints_to_alarm=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )
        
        error_rate_alarm.add_alarm_action(
            cloudwatch.SnsAction(self.alert_topic)
        )
        
        # High response time alarm
        response_time_alarm = cloudwatch.Alarm(
            self, "HighResponseTimeAlarm",
            alarm_name="MultiAgentSystem-HighResponseTime",
            alarm_description="High response time detected in multi-agent system",
            metric=cloudwatch.Metric(
                namespace=self.metrics_namespace,
                metric_name="ResponseTime",
                statistic="Average"
            ),
            threshold=5000,  # 5 seconds
            evaluation_periods=3,
            datapoints_to_alarm=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )
        
        response_time_alarm.add_alarm_action(
            cloudwatch.SnsAction(self.alert_topic)
        )
        
        # Low agent availability alarm
        agent_availability_alarm = cloudwatch.Alarm(
            self, "LowAgentAvailabilityAlarm",
            alarm_name="MultiAgentSystem-LowAgentAvailability",
            alarm_description="Low agent availability detected",
            metric=cloudwatch.Metric(
                namespace=self.metrics_namespace,
                metric_name="ActiveAgents",
                statistic="Average"
            ),
            threshold=1,  # Less than 1 active agent
            evaluation_periods=2,
            datapoints_to_alarm=2,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD
        )
        
        agent_availability_alarm.add_alarm_action(
            cloudwatch.SnsAction(self.alert_topic)
        )