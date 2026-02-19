"""Agent-based interface for object detection using OpenAI's Agents SDK.

This module demonstrates how to structure detection into multiple Agents.
A ``DelegatingAgent`` owns specialized Agents for each object type (bare
spots, animals and weeds). The main agent delegates an image to the
appropriate sub-agent which performs the actual analysis via the OpenAI
Agents API.
"""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from typing import Dict, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI()


def _encode_image(path: str) -> str:
    """Return a base64 encoded string for ``path``."""
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode("utf-8")


@dataclass
class DetectionAgent:
    """Simple wrapper holding instructions for a specialised agent."""

    name: str
    instructions: str
    assistant_id: Optional[str] = None

    def ensure_assistant(self) -> str:
        """Create the Assistant on demand and return its id."""
        if not self.assistant_id:
            assistant = client.beta.assistants.create(
                name=self.name,
                instructions=self.instructions,
                model="gpt-4o",
            )
            self.assistant_id = assistant.id
        return self.assistant_id

    def analyze(self, image_path: str) -> str:
        """Analyze ``image_path`` and return the assistant's response text."""
        assist_id = self.ensure_assistant()
        image = _encode_image(image_path)
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.instructions},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ]
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assist_id
        )
        client.beta.threads.runs.wait(thread_id=thread.id, run_id=run.id)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        if messages.data:
            return messages.data[0].content[0].text.value
        return ""


class DelegatingAgent:
    """Main agent that delegates to object specific agents."""

    def __init__(self) -> None:
        self.agents: Dict[str, DetectionAgent] = {
            "bare spot": DetectionAgent(
                "Bare Spot Agent", "Detect bare soil patches in the image."
            ),
            "animal": DetectionAgent(
                "Animal Agent", "Detect animals such as deer or birds."
            ),
            "weed": DetectionAgent("Weed Agent", "Detect the presence of weeds."),
        }

    def analyze(self, image_path: str, look_for: str) -> str:
        """Delegate analysis of ``image_path`` based on ``look_for``."""
        key = look_for.strip().lower()
        agent = self.agents.get(key)
        if not agent:
            raise ValueError(f"Unsupported object type: {look_for}")
        logger.debug("Delegating '%s' detection to %s", look_for, agent.name)
        return agent.analyze(image_path)
