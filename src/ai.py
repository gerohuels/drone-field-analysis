import base64
import json
from openai import OpenAI


client = OpenAI()


def encode_image(image_path: str) -> str:
    """Return a base64 encoded string for the given image."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def report_bare_spot(location: str, confidence: float) -> str:
    """Print and return a short report about a detected bare spot."""
    message = f"✅ Found a bare spot at {location} with confidence {confidence:.2f}"
    print(message)
    return message


def analyze_frame(image_path: str):
    """Analyze a frame for bare spots using the OpenAI API.

    Parameters
    ----------
    image_path: str
        Path to the frame image.

    Returns
    -------
    dict | None
        Dictionary with location, confidence and report message if a bare
        spot was detected with high confidence, otherwise ``None``.
    """
    base64_image = encode_image(image_path)
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
                            "A bare spot is defined as a **large, clearly visible patch of exposed soil** "
                            "with **no visible crop growth**, not just a small gap between plants. "
                            "These areas often appear as dark, compacted zones, paths, or spots, "
                            "possibly caused by machinery, drought, or compaction. "
                            "**Only call the `report_bare_spot` function if the bare soil area "
                            "is large and clearly distinct from healthy crop rows.** "
                            "Respond in one short sentence."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
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
                                "description": "Estimated location of the bare spot in the frame",
                            },
                            "confidence": {
                                "type": "number",
                                "description": "Confidence level from 0 to 1",
                            },
                        },
                        "required": ["location", "confidence"],
                    },
                },
            }
        ],
        tool_choice="auto",
        max_tokens=100,
    )

    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call.function.name == "report_bare_spot":
                args = json.loads(tool_call.function.arguments)
                if args.get("confidence", 0) >= 0.85:
                    report = report_bare_spot(args["location"], args["confidence"])
                    return {
                        "location": args["location"],
                        "confidence": args["confidence"],
                        "report": report,
                    }
    return None


if __name__ == "__main__":
    # Simple manual test when running this file directly
    sample_path = "output/frame_013.jpg"
    analyze_frame(sample_path)
