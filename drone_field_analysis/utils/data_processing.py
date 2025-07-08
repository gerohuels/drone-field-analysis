"""Object detection routines using the OpenAI API."""

import base64
import json
import logging
import os
from openai import OpenAI

from ..config.settings import OUTPUT_DIR


logger = logging.getLogger(__name__)
client = OpenAI()


def encode_image(image_path: str) -> str:
    """Return a base64 encoded string for the given image.

    The OpenAI API expects image content to be provided as a base64 string,
    so this helper reads the file and performs the conversion.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def detect_object(
    object_type: str, report: str, confidence: float, box_parameter: str
) -> dict:
    """Return a standardized result description for a detected object."""

    message = (
        f"Object: {object_type} \n"
        f"Report: {report} \n"
        f"Detection confidence is {confidence:.2f}. \n"
        f"Box coordinates: {box_parameter}."
    )
    logger.info("\N{satellite} %s", message)
    return {
        "object_type": object_type,
        "report": report,
        "confidence": confidence,
        "box_parameter": box_parameter,
        "description": message,
    }


def _build_result(args: dict) -> dict | None:
    """Return a standardized result dictionary for a tool call."""

    if args.get("confidence", 0) < 0.85:
        return None

    return detect_object(
        args.get("object_type", "unknown"),
        args.get("report", ""),
        args["confidence"],
        str(args.get("box_parameter")),
    )


def analyze_frame(image_path: str, look_for: str) -> dict | None:
    """Analyze a frame using the OpenAI API for the selected objects.

    Parameters
    ----------
    image_path: str
        Path to the frame image.
    look_for: str
        Text describing the objects to search for (e.g. "bare spot", "animal").

    Returns
    -------
    dict | None
        Dictionary describing a detected object if one is found with high
        confidence. The dictionary contains ``object_type``, ``report``,
        ``description``, ``confidence`` and ``box_parameter`` keys. ``None`` is
        returned if no relevant object is detected.
    """
    base64_image = encode_image(image_path)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "detect_object",
                "description": "Function to report detected objects",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "object_type": {"type": "string"},
                        "report": {"type": "string"},
                        "confidence": {"type": "number"},
                        "box_parameter": {
                            "type": "array",
                            "items": {"type": "integer"},
                        },
                    },
                    "required": ["object_type", "report", "confidence", "box_parameter"],
                },
            },
        }
    ]

    prompt_parts = ["Analyze this frame and identify any of the following objects:"]

    if "bare spot" in look_for.lower():
        prompt_parts.append(
            "- **Bare spots**: Analyze this frame of the field and identify any bare spots. "
            "A bare spot is defined as a **large, clearly visible patch of exposed soil** "
            "with **no visible crop growth**, not just a small gap between plants. "
            "These areas often appear as dark, compacted zones, paths, or spots, "
            "possibly caused by machinery, drought, or compaction. "
            "**Only call the `detect_object` function if the bare soil area "
            "is large and clearly distinct from healthy crop rows.** "
            "Describe the bare spot in 1 sentence (e.g. are there cracks in the soil, "
            "is there a water deficit). "
            "Return the box coordinates of the spot as [x1, y1, x2, y2] for a 1920x1080 image."
        )

    if "animal" in look_for.lower():
        prompt_parts.append(
            "- **Animals**: clearly visible animals like deer, birds, or rabbits, and nests of egg-laying animals."
        )

    prompt_parts.append(
        "Return results using the `detect_object` function and include bounding box [x1, y1, x2, y2] using 1920x1080 coordinates."
    )

    prompt_text = "\n".join(prompt_parts)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
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
        tools=tools,
        tool_choice="auto",
        max_tokens=200,
    )

    results = []
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call.function.name != "detect_object":
                continue
            args = json.loads(tool_call.function.arguments)
            result = _build_result(args)
            if result:
                results.append(result)

    return results[0] if results else None


if __name__ == "__main__":
    # Simple manual test when running this file directly
    sample_path = os.path.join(OUTPUT_DIR, "frame_013.jpg")
    analyze_frame(sample_path, "bare spot")
