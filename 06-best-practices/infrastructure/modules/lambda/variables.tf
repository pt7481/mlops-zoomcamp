variable "lambda_function_name" {
  
}

variable "lambda_image_uri" {

}

variable "output_stream_name" {

}

variable "model_bucket_name" {
    description = "The name of the S3 bucket for storing ML models"
    type        = string
}

variable "project_id" {
  description = "The project ID for the infrastructure"
  type        = string
  default     = "mlops-zoomcamp"
}

variable "output_stream_arn" {
  description = "The ARN of the output Kinesis stream"
  type        = string
}

variable "source_stream_arn" {
  description = "The ARN of the source Kinesis stream"
  type        = string
}

variable "mlflow_experiment_id" {
  description = "The MLflow experiment ID"
  type        = string
}
