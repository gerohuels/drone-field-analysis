"""Image analysis helpers using a local LLM via LangChain.

This module provides utilities for detecting bare soil areas, animals and weeds
in drone footage.  It communicates with a locally running language model (for
example an Ollama instance using the ``llava`` model) through the LangChain
library.  The previous OpenAI based implementation has been replaced so that no
external API key is required.
"""

import base64
import json
import logging
import os
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage

from ..config.settings import OUTPUT_DIR


logger = logging.getLogger(__name__)
chat_model = ChatOllama(model="llava")


def encode_image(image_path: str) -> str:
    """Return a base64 encoded string for the given image.

    The local LLM expects the image content to be provided as a base64 string,
    so this helper reads the file and performs the conversion before returning
    it to the caller.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def report_bare_spot(report: str, confidence: float, box_parameter: str) -> str:
    """Return a short description of a detected bare spot.

    This function mirrors the schema expected by the LangChain tool calling
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
    """Analyze a frame using a local LLM via LangChain.

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
        "Analyze this frame and identify any of the following objects:",
    ]

    if "bare spot" in look_for.lower():
        prompt_parts.append(
            "- **Bare spots**: clearly visible patches of exposed soil with no crop growth."
        )

    if "animal" in look_for.lower():
        prompt_parts.append(
            "- **Animals**: clearly visible animals like deer, birds or rabbits."
        )

    if "weed" in look_for.lower():
        prompt_parts.append(
            "- **Weeds**: green vegetation that stands out from the crop."
        )

    prompt_parts.append(
        "Respond with a JSON array. Each item must contain object_type, description, confidence and box_parameter (as [x1, y1, x2, y2]). Return an empty list when nothing is found."
    )

    prompt_text = "\n".join(prompt_parts)

    messages = [
        HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"},
            ]
        )
    ]

    response = chat_model.invoke(messages)

    try:
        results = json.loads(response.content)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to parse LLM response: %s", exc)
        logger.debug("Response text: %s", response.content)
        return None

    # ``None`` signals that the model did not detect anything of interest
    return results if results else None


if __name__ == "__main__":
    # Simple manual test when running this file directly
    sample_path = os.path.join(OUTPUT_DIR, "frame_013.jpg")
    analyze_frame(sample_path)
