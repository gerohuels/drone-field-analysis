from __future__ import annotations

"""Analyzers used by :mod:`data_processing`.

This module implements a small strategy/factory setup for describing
objects that can be detected in a frame. Each analyzer exposes the
schema for the OpenAI function calling API and knows how to interpret the
model's response. The design follows the Strategy pattern where each
concrete analyzer encapsulates the behaviour for a single object type.
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def report_bare_spot(report: str, confidence: float, box_parameter: str) -> str:
    """Return a short description of a detected bare spot."""
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


@dataclass
class Analyzer(ABC):
    """Base class for all analyzers."""

    object_type: str

    @property
    @abstractmethod
    def function_name(self) -> str:
        """Name used in the OpenAI tool definition."""

    @property
    @abstractmethod
    def tool(self) -> Dict[str, Any]:
        """Return the tool schema for the OpenAI API."""

    @property
    @abstractmethod
    def prompt(self) -> str:
        """Prompt segment describing this object type."""

    @abstractmethod
    def parse(self, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert tool call arguments into a result dictionary."""


class BareSpotAnalyzer(Analyzer):
    object_type = "bare spot"
    function_name = "report_bare_spot"
    tool = {
        "type": "function",
        "function": {
            "name": function_name,
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
    prompt = (
        "- **Bare spots**: Bare spots: Large, clearly visible patches of exposed soil with no "
        "signs of crop growth. These areas appear as uncovered earth — typically light brown or "
        "tan — with no green vegetation, leaves, or canopy overhead. A valid bare spot must be at "
        "least 5x5 cm in real-world size, fully free from crops, shadow, debris, or partial "
        "coverage. The soil surface should be unobstructed and distinctly visible from above."
    )

    def parse(self, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if args.get("confidence", 0) < 0.85:
            return None
        return {
            "object_type": self.object_type,
            "report": args["report"],
            "confidence": args["confidence"],
            "box_parameter": args.get("box_parameter"),
            "description": report_bare_spot(
                args["report"], args["confidence"], str(args.get("box_parameter"))
            ),
        }


class AnimalAnalyzer(Analyzer):
    object_type = "animal"
    function_name = "report_animal"
    tool = {
        "type": "function",
        "function": {
            "name": function_name,
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
    prompt = "- **Animals**: clearly visible animals like deer, birds, or rabbits."

    def parse(self, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if args.get("confidence", 0) < 0.85:
            return None
        return {
            "object_type": self.object_type,
            "species": args["species"],
            "description": args["description"],
            "confidence": args["confidence"],
            "box_parameter": args.get("box_parameter"),
        }


class WeedAnalyzer(Analyzer):
    object_type = "weed"
    function_name = "report_weed"
    tool = {
        "type": "function",
        "function": {
            "name": function_name,
            "description": "Function to report weeds in the field",
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
    prompt = (
        "- **Weeds**: Detect the presence of weeds in this image. Weeds are characterized by small "
        "or clustered patches of green vegetation that visually contrast with the golden or beige "
        "wheat crop. Focus on: Green plant patches that are structurally or color-wise different "
        "from the wheat Vegetation in areas of exposed soil or near crop gaps Ignore: Dark soil "
        "patches without green coloration Shadows or flattened wheat that may appear darker but "
        "match wheat color/texture Dry/dead plant matter with no distinct green tones"
    )

    def parse(self, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if args.get("confidence", 0) < 0.85:
            return None
        return {
            "object_type": self.object_type,
            "report": args["report"],
            "confidence": args["confidence"],
            "box_parameter": args.get("box_parameter"),
            "description": report_weed(
                args["report"], args["confidence"], str(args.get("box_parameter"))
            ),
        }


class AnalyzerFactory:
    """Factory for creating analyzers based on the ``look_for`` value."""

    _registry = {
        "bare": BareSpotAnalyzer,
        "animal": AnimalAnalyzer,
        "weed": WeedAnalyzer,
    }

    @classmethod
    def create(cls, look_for: str) -> List[Analyzer]:
        """Return analyzers matching the ``look_for`` string."""
        look_for = look_for.lower()
        analyzers: List[Analyzer] = []
        for key, analyzer_cls in cls._registry.items():
            if key in look_for:
                analyzers.append(analyzer_cls())
        return analyzers
