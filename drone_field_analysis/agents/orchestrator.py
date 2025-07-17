"""Agent orchestration for field analysis."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Dict, Iterable

from openai import OpenAI

from ..utils.data_processing import analyze_frame

logger = logging.getLogger(__name__)
client = OpenAI()


def _weed_agent(image_path: str):
    """Analyze ``image_path`` for weeds."""
    return analyze_frame(image_path, "weed")


def _animal_agent(image_path: str):
    """Analyze ``image_path`` for animals."""
    return analyze_frame(image_path, "animal")


def _bare_spot_agent(image_path: str):
    """Analyze ``image_path`` for bare spots."""
    return analyze_frame(image_path, "bare spot")


@dataclass
class DetectionAgent:
    """Simple wrapper around a callable detection function."""

    name: str
    func: Callable[[str], Iterable[dict] | None]

    def run(self, image_path: str):
        return self.func(image_path)


class OrchestratorAgent:
    """Decide which specialized detection agent to invoke."""

    def __init__(self) -> None:
        self.agents: Dict[str, DetectionAgent] = {
            "weed": DetectionAgent("weed", _weed_agent),
            "animal": DetectionAgent("animal", _animal_agent),
            "bare spot": DetectionAgent("bare spot", _bare_spot_agent),
        }

    def choose_agent(self, request: str) -> DetectionAgent:
        """Select an agent using the OpenAI Agents SDK."""
        prompt = (
            "You are an orchestrator. Based on the user request, decide whether the"
            " weed detection, animal detection or bare spot detection agent should"
            " run. Answer with exactly one of: weed, animal, bare spot.\n"
            f"User request: {request}"
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1,
        )
        choice = (response.choices[0].message.content or "").lower()
        logger.debug("Orchestrator choice: %s", choice)
        for key in self.agents:
            if key in choice:
                return self.agents[key]
        return self.agents["bare spot"]

    def run(self, image_path: str, request: str):
        """Run the chosen detection agent."""
        agent = self.choose_agent(request)
        logger.info("Running %s agent", agent.name)
        return agent.run(image_path)
