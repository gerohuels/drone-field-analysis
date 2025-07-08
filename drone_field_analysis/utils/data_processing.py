"""Image analysis helpers using the OpenAI API.

This module provides utilities for detecting bare soil areas and animals in
drone footage.  The :func:`analyze_frame` function dynamically builds the prompt
and tool definitions based on what the user wants to look for.
"""

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


def report_bare_spot(report: str, confidence: float, box_parameter: str) -> str:
    """Return a short description of a detected bare spot.

    This function mirrors the schema expected by the OpenAI function calling
    API. It is invoked by the language model when a bare spot is found with
    sufficient confidence.
    """
    message = (
        f"Report: {report} \n"
        f"Detection confidence is {confidence:.2f}. \n"
        f"Box coordinates: {box_parameter}."
    )
    logger.info("\N{microscope} %s", message)
    return message


def report_animal(
    species: str, description: str, confidence: float, box_parameter: str
) -> str:
    """Return a short description of a detected animal."""
    message = (
        f"Species: {species} \n"
        f"Description: {description} \n"
        f"Detection confidence is {confidence:.2f}. \n"
        f"Box coordinates: {box_parameter}."
    )
    logger.info("\N{dog} %s", message)
    return message


def analyze_frame(image_path: str, look_for: str = "bare spot"):
    """Analyze a frame using the OpenAI API.

    Parameters
    ----------
    image_path: str
        Path to the frame image.

    Returns
    -------
    dict | None
        List with dictionaries describing any detected objects. Each dictionary
        contains ``object_type``, ``description``, ``confidence`` and
        ``box_parameter`` keys. ``None`` is returned when nothing is found.
    """
    base64_image = encode_image(image_path)

    tools = []
    prompt_parts = ["Analyze this frame and identify any of the following objects:"]

    if "bare spot" in look_for.lower():
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": "report_bare_spot",
                    "description": "Function to report bare spots in the field",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report": {"type": "string"},
                            "confidence": {"type": "number"},
                            "box_parameter": {"type": "array", "items": {"type": "integer"}},
                        },
                        "required": ["report", "confidence", "box_parameter"],
                    },
                },
            }
        )
        prompt_parts.append(
            "- **Bare spots**: clearly visible large patches of exposed soil with no visible crop growth."
        )

    if "animal" in look_for.lower():
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": "report_animal",
                    "description": "Function to report detected animals in the field",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "species": {"type": "string"},
                            "description": {"type": "string"},
                            "confidence": {"type": "number"},
                            "box_parameter": {"type": "array", "items": {"type": "integer"}},
                        },
                        "required": ["species", "description", "confidence", "box_parameter"],
                    },
                },
            }
        )
        prompt_parts.append(
            "- **Animals**: clearly visible animals like deer, birds, or rabbits."
        )

    prompt_parts.append(
        "Return results using the appropriate function and include bounding box [x1, y1, x2, y2] using 1920x1080 coordinates."
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
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"},
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
            args = json.loads(tool_call.function.arguments)
            if tool_call.function.name == "report_bare_spot" and args.get("confidence", 0) >= 0.85:
                results.append(
                    {
                        "object_type": "bare spot",
                        "report": args["report"],
                        "confidence": args["confidence"],
                        "box_parameter": args.get("box_parameter"),
                        "description": report_bare_spot(
                            args["report"], args["confidence"], str(args.get("box_parameter"))
                        ),
                    }
                )
            elif tool_call.function.name == "report_animal" and args.get("confidence", 0) >= 0.85:
                results.append(
                    {
                        "object_type": "animal",
                        "species": args["species"],
                        "description": args["description"],
                        "confidence": args["confidence"],
                        "box_parameter": args.get("box_parameter"),
                    }
                )

    return results if results else None


if __name__ == "__main__":
    # Simple manual test when running this file directly
    sample_path = os.path.join(OUTPUT_DIR, "frame_013.jpg")
    analyze_frame(sample_path)
