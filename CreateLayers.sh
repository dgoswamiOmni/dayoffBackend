#!/bin/bash

## Inputs
REQUIREMENTS_TXT_PATH="/Users/devarshigoswami/Desktop/work/day_off/DayOffBackend/requriements.txt"
#
#pip freeze > "${REQUIREMENTS_TXT_PATH}"

pip install -t dependancies -r "${REQUIREMENTS_TXT_PATH}"

(cd dependancies; zip ../aws_lambda_artifact.zip -r .)

zip aws_lambda_artifact.zip -ru Classes
zip aws_lambda_artifact.zip -ru Utils
zip aws_lambda_artifact.zip -u main.py

##!/bin/bash
#
## AWS Lambda function details
#FUNCTION_NAME="dayoff"
#REGION="eu-west-1"
#ZIP_FILE="aws_lambda_artifact.zip"
#
## AWS S3 details
#S3_BUCKET="dayoff-backend"
#S3_KEY="lambda/${ZIP_FILE}"
#
## Upload Lambda function code to S3
#aws s3 cp "${ZIP_FILE}" "s3://${S3_BUCKET}/${S3_KEY}" --region "${REGION}"

# Deploy Lambda function

#lambda_result=$(aws lambda update-function-code \
#    --function-name "${FUNCTION_NAME}" \
##    --runtime "python3.9" \
##    --role "arn:aws:iam::436791640204:role/service-role/DayOff_FastAPI-role-eb143dq2"  \
##    --handler "main.app"  \
#    --code "S3Bucket=${S3_BUCKET},S3Key=${S3_KEY}" \
#    --region "${REGION}" \
#    --output json)


#aws lambda update-function-code \
#    --function-name "${FUNCTION_NAME}" \
#    --s3-bucket "${S3_BUCKET}" \
#    --s3-key "lambda/${ZIP_FILE}" \
#    --region "${REGION}"
#
#
## Extract Lambda function URL from the result
#lambda_function_url=$(echo "$lambda_result" | jq -r '.FunctionArn')
#
## Print the Lambda function URL
#echo "Lambda function URL: ${lambda_function_url}"
#
