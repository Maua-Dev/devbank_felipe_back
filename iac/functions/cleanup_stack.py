import os
import boto3
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
cloudformation = boto3.client('cloudformation')
logs_client = boto3.client('logs')


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function to delete CloudFormation stack and associated CloudWatch log groups.
    
    This function is triggered by EventBridge Scheduler 90 days after the last stack deployment.
    It will:
    1. Delete all CloudWatch log groups associated with the stack
    2. Delete the CloudFormation stack itself
    
    Environment Variables:
        STACK_NAME: Name of the CloudFormation stack to delete
        AWS_REGION: AWS region where the stack is deployed
    
    Returns:
        Dict with status and message
    """
    stack_name = os.environ.get('STACK_NAME')
    region = os.environ.get('AWS_REGION')
    
    if not stack_name:
        error_msg = "STACK_NAME environment variable is not set"
        logger.error(error_msg)
        return {
            'statusCode': 500,
            'body': error_msg
        }
    
    logger.info(f"Starting cleanup process for stack: {stack_name} in region: {region}")
    
    try:
        # Step 1: Delete CloudWatch log groups associated with the stack
        delete_cloudwatch_logs(stack_name)
        
        # Step 2: Delete the CloudFormation stack
        delete_stack(stack_name)
        
        success_msg = f"Successfully initiated deletion of stack {stack_name} and its CloudWatch logs"
        logger.info(success_msg)
        
        return {
            'statusCode': 200,
            'body': success_msg
        }
        
    except Exception as e:
        error_msg = f"Error during cleanup: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            'statusCode': 500,
            'body': error_msg
        }


def delete_cloudwatch_logs(stack_name: str) -> None:
    """
    Delete all CloudWatch log groups associated with the stack.
    
    This function searches for log groups that contain the stack name and deletes them.
    Common patterns:
    - /aws/lambda/<stack_name>*
    - /aws/lambda/*<function_name>* (where function is part of the stack)
    
    Args:
        stack_name: Name of the CloudFormation stack
    """
    try:
        logger.info(f"Searching for CloudWatch log groups to delete for stack: {stack_name}")
        
        # Get all log groups (we'll filter by stack name)
        paginator = logs_client.get_paginator('describe_log_groups')
        deleted_count = 0
        
        for page in paginator.paginate():
            for log_group in page.get('logGroups', []):
                log_group_name = log_group['logGroupName']
                
                # Delete ONLY log groups that contain the stack name
                # CloudFormation creates log groups with patterns like:
                # /aws/lambda/{StackName}-{ResourceName}-{RandomSuffix}
                # We check if the stack name appears anywhere in the log group name
                if stack_name in log_group_name:
                    try:
                        logger.info(f"Deleting log group: {log_group_name}")
                        logs_client.delete_log_group(logGroupName=log_group_name)
                        deleted_count += 1
                    except logs_client.exceptions.ResourceNotFoundException:
                        logger.warning(f"Log group {log_group_name} not found, skipping")
                    except Exception as e:
                        logger.warning(f"Failed to delete log group {log_group_name}: {str(e)}")
        
        logger.info(f"Deleted {deleted_count} CloudWatch log groups for stack {stack_name}")
        
    except Exception as e:
        logger.error(f"Error deleting CloudWatch logs: {str(e)}")
        # Don't raise - we want to continue with stack deletion even if log deletion fails
        

def delete_stack(stack_name: str) -> None:
    """
    Delete the CloudFormation stack.
    
    Args:
        stack_name: Name of the CloudFormation stack to delete
        
    Raises:
        Exception: If stack deletion fails
    """
    try:
        # Check if stack exists first
        try:
            cloudformation.describe_stacks(StackName=stack_name)
        except cloudformation.exceptions.ClientError as e:
            if 'does not exist' in str(e):
                logger.info(f"Stack {stack_name} does not exist, nothing to delete")
                return
            raise
        
        # Initiate stack deletion
        logger.info(f"Initiating deletion of stack: {stack_name}")
        cloudformation.delete_stack(StackName=stack_name)
        logger.info(f"Stack deletion initiated successfully for {stack_name}")
        
    except Exception as e:
        error_msg = f"Failed to delete stack {stack_name}: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
