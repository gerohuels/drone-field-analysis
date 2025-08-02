"""Image analysis helpers using a local language model via LangChain.

This module provides utilities for detecting bare soil areas and animals in
drone footage.  The :func:`analyze_frame` function builds prompts for a local
LLM served through ``ollama`` and accessed with LangChain.
"""

import base64
import json
import logging
import os
from langchain_community.chat_models import ChatOllama

from ..config.settings import OUTPUT_DIR


logger = logging.getLogger(__name__)
llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3"))


def encode_image(image_path: str) -> str:
    """Return a base64 encoded string for the given image.

    The language model expects image content to be provided as a base64 string,
    so this helper reads the file and performs the conversion before returning
    it to the caller.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def report_bare_spot(report: str, confidence: float, box_parameter: str) -> str:
    """Return a short description of a detected bare spot.

    This function mirrors the schema expected by the language model's
    structured output. It is invoked when a bare spot is found with
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


def report_weed(report: str, confidence: float, box_parameter: str) -> str:
    """Return a short description of detected weeds."""

    message = (
        f"Report: {report} \n"
        f"Detection confidence is {confidence:.2f}. \n"
        f"Box coordinates: {box_parameter}."
    )
    logger.info("\N{herb} %s", message)
    return message


def analyze_frame(image_path: str, look_for: str = "bare spot"):
    """Analyze a frame using a local LLM served by Ollama.

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

    prompt_parts = [
        "You are an expert drone image analyst.",
        "Identify the requested objects in the image provided as base64.",
    ]

    if "bare spot" in look_for.lower():
        prompt_parts.append(
            "- **Bare spots**: Large, clearly visible patches of exposed soil with no signs of crop growth."
        )

    if "animal" in look_for.lower():
        prompt_parts.append(
            "- **Animals**: clearly visible animals like deer, birds, or rabbits."
        )

    if "weed" in look_for.lower():
        prompt_parts.append(
            "- **Weeds**: patches of green vegetation that stand out from the surrounding crop."
        )

    prompt_parts.append(
        "Return JSON with a 'detections' list. Each item must contain 'object_type', 'report' or 'species' as appropriate, 'description', 'confidence', and 'box_parameter' as [x1, y1, x2, y2]. Only include detections with confidence >= 0.85. If none are present, return an empty list."
    )

    prompt_text = "\n".join(prompt_parts) + f"\nImage data: {base64_image}"

    response = llm.invoke(prompt_text)

    try:
        data = json.loads(response.content)
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.error("Failed to parse LLM response: %s", exc)
        return None

    results = []
    for item in data.get("detections", []):
        obj_type = item.get("object_type", "").lower()
        confidence = item.get("confidence", 0)
        box = item.get("box_parameter")
        if confidence < 0.85:
            continue

        if obj_type == "bare spot":
            report = item.get("report", "")
            results.append(
                {
                    "object_type": "bare spot",
                    "report": report,
                    "confidence": confidence,
                    "box_parameter": box,
                    "description": report_bare_spot(report, confidence, str(box)),
                }
            )
        elif obj_type == "animal":
            results.append(
                {
                    "object_type": "animal",
                    "species": item.get("species", ""),
                    "description": item.get("description", ""),
                    "confidence": confidence,
                    "box_parameter": box,
                }
            )
        elif obj_type == "weed":
            report = item.get("report", "")
            results.append(
                {
                    "object_type": "weed",
                    "report": report,
                    "confidence": confidence,
                    "box_parameter": box,
                    "description": report_weed(report, confidence, str(box)),
                }
            )

    return results or None

if __name__ == "__main__":
    # Simple manual test when running this file directly
    sample_path = os.path.join(OUTPUT_DIR, "frame_013.jpg")
    analyze_frame(sample_path)
