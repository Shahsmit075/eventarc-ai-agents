import os
import json
import uuid
from google.adk.agents.llm_agent import Agent
from google.adk.apps.app import App
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.cloud.eventarc_publishing_v1 import PublisherClient
from google.cloud.eventarc_publishing_v1.types import CloudEvent, PublishRequest

# Configuration
BUS_NAME = os.getenv("EVENTARC_BUS_NAME")
SERVICE_NAME = "customer_chat"

# Define the instruction for the agent
INSTRUCTION = """
You are a polite and helpful customer service assistant responsible for
processing customer orders.

Your primary goal is to gather all necessary information from the user,
generate an order, and submit it to the backend fulfillment system.

### REQUIRED INFORMATION
A valid order MUST contain all of the following:
1. At least one item with a clear product name.
2. The specific quantity for every requested item.
3. A complete shipping address.

### OPTIONAL INFORMATION
- User Note: If the user provides any special instructions, comments, or
  extra notes, capture them exactly as written.

### CONVERSATION FLOW
- GATHER: If the user requests an order but is missing any of the REQUIRED
  INFORMATION, politely ask them to provide the missing details in plain text.
  Do not proceed until you have everything.
- GENERATE: Once all information is gathered, invent a random 6-character
  alphanumeric string to use as the Order ID (e.g., "ORD-8X2P9A"). Do NOT
  write code or use tools to do this; just make it up.
- EXECUTE: Use the system's tool-calling feature to trigger
  `emit_business_event`. Never type the call as text or Python code in your
  chat response. Do NOT wrap the tool call in `print()` or any other function.
    - Set `type` to exactly: "order.created"
    - Set `data` to the JSON payload specified below.
- CONFIRM: After successfully calling the tool, politely inform the user that
  their order has been submitted, provide them with their new Order ID, and
  confirm the shipping address.

### STRICT JSON SCHEMA FOR TOOL DATA
When calling `emit_business_event`, the `data` parameter MUST strictly follow this exact JSON structure:
{
  "order_id": "<generated_order_id>",
  "shipping_address": "<user_provided_address>",
  "user_note": "<insert_any_extra_notes_here_or_leave_blank>",
  "items": [
    {
      "item_name": "<product_name>",
      "quantity": <integer>
    }
  ]
}
"""

# Tool to emit the event
def emit_business_event(type: str, data: dict) -> str:
    """Publishes a business event to Eventarc."""
    print(f"Emitting event {type} with data: {json.dumps(data)}")
    # Initialize the Eventarc publisher client
    client = PublisherClient()

    # Construct the CloudEvent conforming to the CloudEvents spec
    event = CloudEvent(
        id=str(uuid.uuid4()),
        source=SERVICE_NAME,
        spec_version="1.0",
        type_=type,
        text_data=json.dumps(data),
        # Set the content type to application/json
        attributes={"datacontenttype": CloudEvent.CloudEventAttributeValue(ce_string="application/json")}
    )

    # Create the publish request targeting the specific message bus
    request = PublishRequest(
        message_bus=BUS_NAME,
        proto_message=event
    )

    # Publish the event to the bus
    client.publish(request=request)
    return f"Success: Event {type} emitted."

# Create the agent
agent = Agent(
    model='gemini-2.5-flash',
    name=SERVICE_NAME,
    description="Handles customer chat and takes orders.",
    instruction=INSTRUCTION,
    tools=[emit_business_event]
)

# Wrap the agent in an App and add LoggingPlugin
app = App(
    name=SERVICE_NAME,
    root_agent=agent,
    plugins=[LoggingPlugin()]
)