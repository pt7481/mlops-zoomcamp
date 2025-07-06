resource "aws_iam_role" "iam_lambda" {
    name = "iam_lambda_stg_${var.project_id}"
    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = "sts:AssumeRole"
                Effect = "Allow"
                Sid = ""
                Principal = {
                    Service = [
                        "lambda.amazonaws.com",
                        "kinesis.amazonaws.com"
                    ]
                }
            }
        ]
    })
}

resource "aws_iam_policy" "allow_kinesis_processing" {
    name       = "allow_kinesis_processing_stg_${var.project_id}"
    policy     = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = [
                    "kinesis:ListShards",
                    "kinesis:ListStreams",
                    "kinesis:*"
                ]
                Effect   = "Allow"
                Resource = "arn:aws:kinesis:*:*:*"
            },
            {
                Action = [
                    "stream:GetRecord",
                    "stream:GetShardIterator",
                    "stream:DescribeStream",
                    "stream:*"
                ]
                Effect   = "Allow"
                Resource = "arn:aws:kinesis:*:*:*"
            }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "kinesis_processing" {
    role       = aws_iam_role.iam_lambda.name
    policy_arn = aws_iam_policy.allow_kinesis_processing.arn
}

resource "aws_iam_role_policy" "inline_lambda_policy" {
    name       = "inline_lambda_policy_stg_${var.project_id}"
    role       = aws_iam_role.iam_lambda.id
    depends_on = [aws_iam_role.iam_lambda]
    policy     = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "kinesis:PutRecord",
                    "kinesis:PutRecords"
                ]
                Resource = "${var.output_stream_arn}"
            }
        ]
    })
}

resource "aws_iam_policy" "allow_logging" {
    name        = "allow_logging_stg_${var.project_id}"
    path        = "/"
    description = "Policy to allow logging for Lambda function in project ${var.project_id}"
    policy     = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ]
                Effect   = "Allow"
                Resource = "arn:aws:logs:*:*:*"
            }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
    role       = aws_iam_role.iam_lambda.name
    policy_arn = aws_iam_policy.allow_logging.arn
}

resource "aws_iam_policy" "lambda_s3_role_policy" {
    name        = "lambda_s3_role_policy_stg_${var.project_id}"
    description = "Policy to allow Lambda function to access S3 bucket"
    policy      = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = [
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketLocation",
                    "s3:*"
                ]
                Effect   = "Allow"
                Resource = "*"
            },
            {
                Action = [
                    "s3:*"
                ]
                Effect   = "Allow"
                Resource = [
                    "arn:aws:s3:::${var.model_bucket_name}",
                    "arn:aws:s3:::${var.model_bucket_name}/*",
                    "arn:aws:s3:::thoughtswork-co/*"
                ]
            },
            {
                Action = [
                    "autoscaling:Describe*",
                    "cloudwatch:*",
                    "logs:*",
                    "sns:*"
                ]
                Effect   = "Allow"
                Resource = "*"
            }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "iam-policy-attach" {
    role       = aws_iam_role.iam_lambda.name
    policy_arn = aws_iam_policy.lambda_s3_role_policy.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_trigger_lambda_function" {
    statement_id  = "AllowExecutionFromCloudWatch"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.kinesis_lambda.function_name
    principal     = "events.amazonaws.com"
    source_arn    = var.source_stream_arn
}