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
from .analyzers import AnalyzerFactory


logger = logging.getLogger(__name__)
client = OpenAI()


def encode_image(image_path: str) -> str:
    """Return a base64 encoded string for the given image.

    The OpenAI API expects image content to be provided as a base64 string,
    so this helper reads the file and performs the conversion before
    returning it to the caller.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


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

    analyzers = AnalyzerFactory.create(look_for)
    if not analyzers:
        return None

    tools = [analyzer.tool for analyzer in analyzers]
    prompt_parts = [
        "Analyze this frame and identify any of the following objects:",
    ]
    prompt_parts.extend(analyzer.prompt for analyzer in analyzers)
    prompt_parts.append(
        "Return results by calling the appropriate function and always include "
        "the bounding box as [x1, y1, x2, y2]. Ensure the entire object is fully "
        "contained within the box. If multiple objects of the same type are "
        "present, draw a single box that tightly encloses all of them. Do not "
        "include any unrelated areas or background in the bounding box."
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
        analyzers_by_name = {a.function_name: a for a in analyzers}
        for tool_call in tool_calls:
            analyzer = analyzers_by_name.get(tool_call.function.name)
            if not analyzer:
                continue
            args = json.loads(tool_call.function.arguments)
            parsed = analyzer.parse(args)
            if parsed:
                results.append(parsed)

    return results if results else None


if __name__ == "__main__":
    # Simple manual test when running this file directly
    sample_path = os.path.join(OUTPUT_DIR, "frame_013.jpg")
    analyze_frame(sample_path)
