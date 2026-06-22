terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Create the Eventarc Message Bus
resource "google_eventarc_message_bus" "my_bus" {
  location       = var.region
  message_bus_id = var.bus_name

  logging_config {
    log_severity = "DEBUG"
  }
}

# 2. Create the Eventarc Pipeline to forward and translate messages
resource "google_eventarc_pipeline" "order_to_fulfillment" {
  location    = var.region
  pipeline_id = "order-to-fulfillment"

  # Define the HTTP endpoint destination and the A2A payload conversion
  destinations {
    http_endpoint {
      uri = var.fulfillment_agent_url
      
      message_binding_template = <<-EOT
      {
        "headers": headers.merge({
          "Content-Type": "application/json",
          "A2A-Version": "1.0",
          "x-envoy-upstream-rq-timeout-ms": "600000"
        }),
        "body": {
          "jsonrpc": "2.0",
          "id": message.id,
          "method": "message/send",
          "params": {
            "message": {
              "role": "user",
              "messageId": message.id,
              "parts": [
                {
                  "text": "\nCreate a fulfillment plan for the following order:\n------------------\nOrder ID: " + message.data.order_id + "\nAddress: " + message.data.shipping_address + "\nItems: " + message.data.items.toJsonString() + "\nNotes: " + message.data.user_note + "\n"
                }
              ]
            },
            "configuration": {
              "blocking": true
            }
          }
        }
      }
      EOT
    }
  }

  logging_config {
    log_severity = "DEBUG"
  }
}

# 3. Create the Eventarc Enrollment to bind the trigger matching 'order.created'
resource "google_eventarc_enrollment" "match_orders" {
  location      = var.region
  enrollment_id = "match-orders"
  message_bus   = google_eventarc_message_bus.my_bus.id
  destination   = google_eventarc_pipeline.order_to_fulfillment.id
  cel_match     = "message.type == 'order.created'"
}
