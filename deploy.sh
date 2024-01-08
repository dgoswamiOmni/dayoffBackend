#!/bin/bash

# Set the AWS SAM CLI command
sam_cli="sam"

# Set the path to the CloudFormation template file
template_file="dayoff-api.yaml"

# Set the name of the stack
stack_name="DayOffAPI"

# Set the region
region="us-east-1"

# Build the Lambda functions
$sam_cli build

# Deploy the stack
$sam_cli deploy \
  --template-file $template_file \
  --stack-name $stack_name \
  --region $region \
  --capabilities CAPABILITY_NAMED_IAM
