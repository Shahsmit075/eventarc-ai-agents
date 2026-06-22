output "message_bus_id" {
  value       = google_eventarc_message_bus.my_bus.id
  description = "The ID of the created Eventarc Message Bus."
}

output "pipeline_id" {
  value       = google_eventarc_pipeline.order_to_fulfillment.id
  description = "The ID of the created Eventarc Pipeline."
}

output "enrollment_id" {
  value       = google_eventarc_enrollment.match_orders.id
  description = "The ID of the created Eventarc Enrollment."
}
