from datetime import timezone
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    CfnOutput, 
    aws_iam as iam,
    SecretValue,
    aws_scheduler as scheduler
)
from constructs import Construct
from aws_cdk.aws_cloudwatch import ComparisonOperator
from aws_cdk.aws_sns import Topic

from aws_cdk.aws_cloudwatch_actions import SnsAction


class IacStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.project_name = os.environ.get("PROJECT_NAME")
        self.aws_account_id = os.environ.get("AWS_ACCOUNT_ID")

        lambda_fn = _lambda.Function(
            self,
            "SimpleFastAPILambda",
            runtime=_lambda.Runtime.PYTHON_3_13,
            code=_lambda.Code.from_asset("../src"),
            environment={"STAGE":"TEST"},
            handler="app.main.handler",
            timeout=Duration.seconds(15),
        )

        lambda_url = lambda_fn.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE,
            cors=_lambda.FunctionUrlCorsOptions(
            allowed_origins=["*"],
            allowed_headers=["*"],
            exposed_headers=["*"],
            allowed_methods=[_lambda.HttpMethod.ALL],
            max_age=Duration.seconds(5),
            ),
        )

        password = self.stack_name + "UserPassword7@"

        user = iam.User(self, self.stack_name + "User",
                        user_name=self.stack_name + "User",
                        password_reset_required=True,
                        password=SecretValue.unsafe_plain_text(password)
                        )

        policy = iam.Policy(self, "Policy", statements=[
            iam.PolicyStatement(
                actions=["lambda:*"],
                resources=[lambda_fn.function_arn]
            )
        ])

        policy.add_statements(
            iam.PolicyStatement(
                actions=["logs:*"],
                resources=[
                    f"arn:aws:logs:{self.region}:{self.aws_account_id}:log-group:/aws/lambda/{lambda_fn.function_name}:*"
                ],
            )
        )

        policy.attach_to_user(user)

        user.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("IAMUserChangePassword")
        )

        
        alarm = lambda_fn.metric_invocations(
            period=Duration.hours(6),
        ).create_alarm(
            self, self.stack_name +"LambdaAlarm",
            threshold=5000,
            evaluation_periods=1,
            comparison_operator=ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        ) 
        topic = Topic.from_topic_arn(self, self.stack_name + "Topic", f"arn:aws:sns:{self.region}:{self.aws_account_id}:sns-simplefastapi")
        sns_action = SnsAction(topic)

        alarm.add_alarm_action(sns_action)

        # ========================================
        # Auto-Deletion System (90 days)
        # ========================================
        
        # Lambda function for stack cleanup
        cleanup_lambda_role = iam.Role(
            self,
            "CleanupLambdaRole-" + self.stack_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Role for cleanup Lambda to delete stack and CloudWatch logs"
        )
        
        # Grant permissions to delete CloudFormation stack
        cleanup_lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "cloudformation:DeleteStack",
                    "cloudformation:DescribeStacks"
                ],
                resources=[self.stack_id]
            )
        )
        
        # Grant permissions to delete CloudWatch log groups
        cleanup_lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:DeleteLogGroup",
                    "logs:DescribeLogGroups"
                ],
                resources=[f"arn:aws:logs:{self.region}:{self.aws_account_id}:log-group:*"]
            )
        )
        
        # Grant permissions for Lambda to write its own logs
        cleanup_lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[f"arn:aws:logs:{self.region}:{self.aws_account_id}:log-group:/aws/lambda/*"]
            )
        )
        
        # Create cleanup Lambda function
        cleanup_lambda = _lambda.Function(
            self,
            "CleanupStackLambda-" + self.stack_name,
            runtime=_lambda.Runtime.PYTHON_3_13,
            code=_lambda.Code.from_asset("functions"),
            handler="cleanup_stack.handler",
            timeout=Duration.minutes(5),
            environment={"STAGE":"TEST", "STACK_NAME": self.stack_name},
            role=cleanup_lambda_role,
            description=f"Cleanup Lambda for stack {self.stack_name} - auto-deletes after 90 days"
        )
        
        # IAM role for EventBridge Scheduler to invoke Lambda
        scheduler_role = iam.Role(
            self,
            "SchedulerRole-" + self.stack_name,
            assumed_by=iam.ServicePrincipal("scheduler.amazonaws.com"),
            description=f"Role for EventBridge Scheduler to invoke cleanup Lambda for stack {self.stack_name}"
        )
        
        # Grant Scheduler permission to invoke the cleanup Lambda
        cleanup_lambda.grant_invoke(scheduler_role)
        
        # Calculate the deletion time (90 days from now)
        deletion_time = datetime.now(tz=timezone.utc) + timedelta(days=90)
        # Convert to GMT-3
        deletion_time_gmt3 = deletion_time.astimezone(ZoneInfo("America/Sao_Paulo"))
        # Format as ISO 8601: yyyy-MM-ddTHH:mm:ss
        deletion_time_str = deletion_time_gmt3.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Create EventBridge Scheduler to trigger cleanup after 90 days
        cleanup_schedule = scheduler.CfnSchedule(
            self,
            "CleanupSchedule-" + self.stack_name,
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF"
            ),
            schedule_expression=f"at({deletion_time_str})",
            schedule_expression_timezone="America/Sao_Paulo",
            target=scheduler.CfnSchedule.TargetProperty(
                arn=cleanup_lambda.function_arn,
                role_arn=scheduler_role.role_arn
            ),
            description=f"Auto-delete stack {self.stack_name} 90 days after last deployment"
        )

        CfnOutput(self, self.stack_name + "Url",
                  value=lambda_url.url,
                  export_name= self.stack_name + 'UrlValue')    

        CfnOutput(self, self.stack_name + "UserOutput",
                  value=user.user_name,
                  export_name= self.stack_name + 'UserValue'
                  )

        CfnOutput(self, self.stack_name + "FirstTimeUserPassword",
                  value=password,
                  export_name= self.stack_name + 'FirstTimeUserPasswordValue'
                  )    
        
        CfnOutput(self, self.stack_name + "LambdaConsole",
                    value="https://" + self.region + ".console.aws.amazon.com/lambda/home?region=" + self.region + "#/functions/" + lambda_fn.function_name + "?tab=code",
                    export_name= self.stack_name + 'LambdaConsoleValue'
                    )
        
        CfnOutput(self, self.stack_name + "DeletionScheduledFor",
                    value=deletion_time_str,
                    export_name= self.stack_name + 'DeletionScheduledForValue',
                    description="Stack will be automatically deleted at this time (UTC)"
                    )
        

