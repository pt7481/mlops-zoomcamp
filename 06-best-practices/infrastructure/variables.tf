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