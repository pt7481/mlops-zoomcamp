terraform {
    required_version = ">= 1.8"
    backend "s3" {
        bucket = "tw-tf-state-mlops-zoomcamp"
        key     = "mlops-zoomcamp.tfstate"
        region  = "us-east-2"
        encrypt = true
    }
}

provider "aws" {
    region = var.aws_region
}

data "aws_caller_identity" "current_identity" {}

locals {
    account_id = data.aws_caller_identity.current_identity.account_id
}

# ride_events
module "source_kinesis_stream" {
    source = "./modules/kinesis"
    stream_name = "${var.source_stream_name}_${var.project_id}"
    shard_count = 2
    retention_period = 48
    tags = {
        CreatedBy = var.project_id
        Environment = "dev"
        AccountID = local.account_id
    }
}

# ride_predictions
module "output_kinesis_stream" {
    source = "./modules/kinesis"
    stream_name = "${var.output_stream_name}_${var.project_id}"
    shard_count = 2
    retention_period = 48
    tags = {
        CreatedBy = var.project_id
        Environment = "dev"
        AccountID = local.account_id
    }
}

# model bucket
module "s3_bucket" {
    source = "./modules/s3"
    bucket_name = "tw-${var.model_bucket}-${var.project_id}"
}

module "ecr_image" {
    source = "./modules/ecr"
    ecr_repo_name = "tw-${var.ecr_repo_name}-${var.project_id}"
    account_id = local.account_id
    lambda_function_local_path = var.lambda_function_local_path
    docker_image_local_path = var.docker_image_local_path
}

module "lambda_function" {
    source = "./modules/lambda"
    lambda_function_name = "${var.lambda_function_name}_${var.project_id}"
    lambda_image_uri = module.ecr_image.image_uri
    output_stream_name = "${var.output_stream_name}_${var.project_id}"
    #source_stream_name = "${var.source_stream_name}_${var.project_id}"
    model_bucket_name = module.s3_bucket.name
    project_id = var.project_id
    output_stream_arn = module.output_kinesis_stream.stream_arn
    source_stream_arn = module.source_kinesis_stream.stream_arn
    mlflow_experiment_id = var.mlflow_experiment_id
}