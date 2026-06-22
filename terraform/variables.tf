variable "project_id" {
  type        = string
  description = "The Google Cloud Project ID."
}

variable "region" {
  type        = string
  description = "The Google Cloud region to deploy Eventarc resources."
  default     = "us-central1"
}

variable "bus_name" {
  type        = string
  description = "The name of the Eventarc Message Bus."
  default     = "my-bus"
}

variable "fulfillment_agent_url" {
  type        = string
  description = "The HTTP target URI of the deployed fulfillment planning agent."
}
