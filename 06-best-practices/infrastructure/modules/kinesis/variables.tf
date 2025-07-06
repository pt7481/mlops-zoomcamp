variable "stream_name" {
  description = "The name of the Kinesis stream"
  type        = string
}

variable "shard_count" {
  description = "The number of shards for the Kinesis stream"
  type        = number
  default     = 1
}

variable "retention_period" {
  description = "The retention period for the Kinesis stream (in hours)"
  type        = number
  default     = 24
}

variable "shard_level_metrics" {
  description = "The shard level metrics for the Kinesis stream"
  type        = list(string)
  default     = [
    "IncomingBytes",
    "IncomingRecords",
    "OutgoingBytes",
    "OutgoingRecords",
    "ReadProvisionedThroughputExceeded",
    "WriteProvisionedThroughputExceeded",
    "IteratorAgeMilliseconds"
  ]
}

variable "tags" {
  description = "The tags to assign to the Kinesis stream"
  type        = map(string)
  default     = {}
}
