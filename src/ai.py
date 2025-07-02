import base64
import json
from openai import OpenAI



# Initialize OpenAI client
client = OpenAI()

# Path to the image frame to analyze
image_path = "output/frame_013.jpg"

# Function to read and encode the image as base64
def encode_image(image_path_ai):
    with open(image_path_ai, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function to be called if a bare spot is confidently detected
def report_bare_spot(location: str, confidence: float):
    print(f"✅ Found a bare spot at {location} with confidence {confidence:.2f}")

# Encode the image for API transmission
base64_image = encode_image(image_path)

# Send the image and analysis instruction to the OpenAI model
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Analyze this frame of the field and identify any bare spots. "
                        "A bare spot is defined as a **large, clearly visible patch of exposed soil** with **no visible crop growth**, "
                        "not just a small gap between plants. These areas often appear as dark, compacted zones, paths, or spots, "
                        "possibly caused by machinery, drought, or compaction. "
                        "**Only call the `report_bare_spot` function if the bare soil area is large and clearly distinct from healthy crop rows.** "
                        "Respond in one short sentence."
                    )
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                    }
                },
            ]
        }
    ],
    # Define the tool the model can call if it detects a bare spot
    tools=[
        {
            "type": "function",
            "function": {
                "name": "report_bare_spot",
                "description": "Report a bare spot in the field if one is clearly visible.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Estimated location of the bare spot in the frame (e.g. 'top left', 'center', etc.)"
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level from 0 to 1 indicating how certain the model is about the bare spot."
                        }
                    },
                    "required": ["location", "confidence"]
                }
            }
        }
    ],
    tool_choice="auto",  # Let the model decide when to call the tool
    max_tokens=100
)

# Print the model's textual response (if any)
print(response.choices[0].message)
print("---")

# Extract any tool calls (i.e., function call suggestions from the model)
tool_calls = response.choices[0].message.tool_calls

# If the model triggered any tool calls:
if tool_calls:
    for tool_call in tool_calls:
        if tool_call.function.name == "report_bare_spot":
            # Parse the function arguments as a Python dictionary from JSON
            args = json.loads(tool_call.function.arguments)

            # 🔍 Confidence Threshold Check:
            # Only execute the report function if the model's confidence is high (e.g. >= 85%)
            if args["confidence"] >= 0.85:
                report_bare_spot(**args)
            else:
                print(f"⚠️ Skipped tool call — confidence too low ({args['confidence']:.2f})")

