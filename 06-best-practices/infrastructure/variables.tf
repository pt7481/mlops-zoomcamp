variable "aws_region" {
    description = "The AWS region to deploy resources in"
    type        = string
    default     = "us-east-2"
}

variable "project_id" {
    description = "The project ID for the infrastructure"
    type        = string
    default     = "mlops-zoomcamp"
}

variable "source_stream_name" {
    description = "The name of the source Kinesis stream"
    type        = string
}

variable "output_stream_name" {
    description = "The name of the output Kinesis stream"
    type        = string
}

variable "model_bucket" {
    description = "The name of the S3 bucket"
    type        = string
}

variable "ecr_repo_name" {
    description = "The name of the ECR repository"
    type        = string
}

variable "lambda_function_local_path" {
    description = "The local path to the Lambda function code"
    type        = string
}

variable "docker_image_local_path" {
    description = "The local path to the Dockerfile for the ECR image"
    type        = string
}

variable "lambda_function_name" {
    description = "The name of the Lambda function"
    type        = string
}
