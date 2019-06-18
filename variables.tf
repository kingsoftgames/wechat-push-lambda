## ===========================================================================
# dynamodb
## ===========================================================================
variable "db_table_name" {
  description = "Dynamodb table name"
  type        = string
  default     = "push.access_token"
}

variable "db_hash_key" {
  description = "Dynamodb table name"
  type        = string
  default     = "im"
}

variable "db_tags" {
  type        = map(string)
  description = "Tags to apply to Dynamodb"
  default     = {}
}

## ===========================================================================
# lambda
## ===========================================================================
variable "lambda_function_name" {
  description = "Lambda function name"
  type        = string
}

variable "lambda_python_file" {
  description = "Lambda python file"
  type        = string
  default     = "push.py"
}

variable "lambda_timeout" {
  description = "The amount of time your Lambda Function has to run in seconds"
  type        = string
  default     = "30"
}

variable "lambda_push_secretkey" {
  description = "Wechat push secretkey for call lambda"
  type        = string
}

variable "lambda_im_ewc_corpid" {
  description = "Wechat corpid"
  type        = string
}

variable "lambda_im_ewc_corpsecret" {
  description = "Wechat corpsecret"
  type        = string
}

## ===========================================================================
# api gateway
## ===========================================================================
variable "api_root_path" {
  description = "Api root path"
  type        = string
  default     = "push"
}

variable "api_im_path" {
  description = "Api root path. Change when lambda parse change"
  type        = string
  default     = "im"
}

