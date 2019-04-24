## ===========================================================================
# dynamodb
## ===========================================================================
output "push-dynamodb-arn" {
  value = "${aws_dynamodb_table.push_dynamodb.arn}"
}

## ===========================================================================
# lambda
## ===========================================================================
output "push-lambda-name" {
  value = "${aws_lambda_function.push_lambda.function_name}"
}

output "push-lambda-arn" {
  value = "${aws_lambda_function.push_lambda.arn}"
}

## ===========================================================================
# api gateway
## ===========================================================================

output "region" {
  value = "${aws_api_gateway_integration.im.http_method}"
}

output "api_url" {
  value = "${aws_api_gateway_deployment.push_api.invoke_url}"
}
