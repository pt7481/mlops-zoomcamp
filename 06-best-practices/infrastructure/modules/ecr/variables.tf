variable "ecr_repo_name" {
    description = "The name of the ECR repository"
    type        = string
}

variable "ecr_image_tag" {
    description = "The tag of the ECR image"
    type        = string
    default     = "latest"
}

variable "aws_region" {
    description = "The AWS region where the ECR repository will be created"
    type        = string
    default     = "us-east-2"
}

variable "lambda_function_local_path" {
    description = "The local path to the Lambda function code"
    type        = string
}

variable "docker_image_local_path" {
    description = "The local path to the Dockerfile for the ECR image"
    type        = string
}

variable "account_id" {
    description = "The AWS account ID"
    type        = string
}