## ===========================================================================
# dynamodb
## ===========================================================================
resource "aws_dynamodb_table" "push_dynamodb" {
  name                   = "${var.db_table_name}"
  billing_mode           = "PAY_PER_REQUEST"
  hash_key               = "${var.db_hash_key}"
  attribute              = [{
                            name = "${var.db_hash_key}"
                            type = "S"
                            }]
 
  tags = "${merge(var.db_tags, map(
    "Name", "push-table"
  ))}"
}

## ===========================================================================
# lambda
## ===========================================================================

data "template_file" "push_lambda_file" {
  template = "${file("${path.module}/function/${var.lambda_python_file}")}"

  vars = {
    push_secretkey  = "${var.lambda_push_secretkey}"
    im_ewc_corpid = "${var.lambda_im_ewc_corpid}"
    im_ewc_corpsecret = "${var.lambda_im_ewc_corpsecret}"
    db_table_name = "${var.db_table_name}"
    db_hash_key = "${var.db_hash_key}"
    db_region = "${data.aws_region.current.name}"
  }
}

data "archive_file" "push_lambda" {
  type        = "zip"
  source {
    content  = "${data.template_file.push_lambda_file.rendered}"
    filename = "${var.lambda_python_file}"
  }
  output_path = "${path.module}/function/push.zip"
}

data "aws_iam_policy_document" "push_lambda" {
  statement {
    effect = "Allow"
    actions = [
        "sts:AssumeRole",
    ]
    
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "push_lambda_dynamodb_log" {
  statement {
    effect = "Allow"
    actions = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
    ]

    resources = [
      "*",
    ]
  }
  
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:DescribeTable",
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
    ]

    resources = [
      "${aws_dynamodb_table.push_dynamodb.arn}",
    ]
  }
}
resource "aws_iam_policy" "push_lambda_dynamodb_log" {
  name    = "${var.lambda_function_name}_dynamodb_log"
  path    = "/"
  policy  = "${ data.aws_iam_policy_document.push_lambda_dynamodb_log.json }"
}


resource "aws_iam_role_policy_attachment" "push_lambda_dynamodb_log" {
  role = "${aws_iam_role.push_lambda.name}"
  policy_arn = "${aws_iam_policy.push_lambda_dynamodb_log.arn}"
}

resource "aws_iam_role" "push_lambda" {
  name               = "${var.lambda_function_name}"
  assume_role_policy = "${data.aws_iam_policy_document.push_lambda.json}"
}

resource "aws_lambda_function" "push_lambda" {
  filename         = "${data.archive_file.push_lambda.output_path}"
  function_name    = "${var.lambda_function_name}"
  role             = "${aws_iam_role.push_lambda.arn}"
  handler          = "push.lambda_handler"
  runtime          = "python3.6"
  source_code_hash = "${data.archive_file.push_lambda.output_base64sha256}"
  timeout          = "${var.lambda_timeout}"
}

## ===========================================================================
# api gateway
## ===========================================================================
resource "aws_api_gateway_rest_api" "push_api" {
  name        = "${var.lambda_function_name}"
  description = "wechat push api"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "push" {
  rest_api_id = "${aws_api_gateway_rest_api.push_api.id}"
  parent_id   = "${aws_api_gateway_rest_api.push_api.root_resource_id}"
  path_part   = "${var.api_root_path}"
}

resource "aws_api_gateway_resource" "im" {
  rest_api_id = "${aws_api_gateway_rest_api.push_api.id}"
  parent_id   = "${aws_api_gateway_resource.push.id}"
  path_part   = "{${var.api_im_path}}"
}


resource "aws_api_gateway_method" "im" {
  rest_api_id   = "${aws_api_gateway_rest_api.push_api.id}"
  resource_id   = "${aws_api_gateway_resource.im.id}"
  http_method   = "POST"
  authorization = "NONE"
}

data "aws_region" "current" {}

resource "aws_api_gateway_integration" "im" {
  rest_api_id = "${aws_api_gateway_rest_api.push_api.id}"
  resource_id = "${aws_api_gateway_method.im.resource_id}"
  http_method = "${aws_api_gateway_method.im.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.push_lambda.invoke_arn}"
}

resource "aws_api_gateway_deployment" "push_api" {
  depends_on = [
    "aws_api_gateway_integration.im"
  ]

  rest_api_id = "${aws_api_gateway_rest_api.push_api.id}"
  stage_name  = "default"
}

resource "aws_lambda_permission" "push_api_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.push_lambda.arn}"
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.push_api.execution_arn}/*/${aws_api_gateway_method.im.http_method}/${var.api_root_path}/*"
}