"""Utility helpers for the multi-agent travel planner sprint.

The package defaults to offline mode so the architecture can be demonstrated
without API credentials. Set DEMO_MODE=live and provide GROQ_API_KEY for
live LLM calls.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:  # pragma: no cover - handled with a clear runtime message
    Groq = None  # type: ignore

try:
    from langsmith import traceable
except ImportError:  # pragma: no cover - LangSmith is optional at runtime
    def traceable(*args: Any, **kwargs: Any):
        """Leave a function unchanged when LangSmith is not installed."""
        def decorator(function):
            return function
        return decorator


PROJECT_ROOT = Path(__file__).resolve().parent


def load_project_env() -> Dict[str, str]:
    """Load .env values and return the main runtime settings.

    Returns:
        Dictionary containing demo mode, model name, temperature, and tracing flags.
    """
    load_dotenv(PROJECT_ROOT / ".env")
    return {
        "demo_mode": os.getenv("DEMO_MODE", "offline").strip().lower(),
        "model_name": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip(),
        "temperature": os.getenv("GROQ_TEMPERATURE", "1").strip(),
        "langsmith_tracing": os.getenv("LANGSMITH_TRACING", "false").strip().lower(),
    }


def load_json_file(path: Path) -> Any:
    """Read a JSON file from disk.

    Args:
        path: Absolute or relative path to a JSON file.

    Returns:
        Parsed JSON content.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains invalid JSON.
    """
    if not path.exists():
        raise FileNotFoundError(f"Could not find data file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path.name}: {exc}") from exc


def parse_json_safely(raw_text: str, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Parse a JSON object from model output with a friendly fallback.

    Args:
        raw_text: Text expected to contain a JSON object.
        fallback: Value to return if parsing fails.

    Returns:
        Parsed dictionary, or fallback when provided.
    """
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    return fallback or {"error": "Model returned malformed JSON", "raw_text": raw_text}


def pretty_json(data: Any) -> str:
    """Format Python data as readable JSON text.

    Args:
        data: Any JSON-serialisable value.

    Returns:
        Pretty JSON string.
    """
    return json.dumps(data, indent=2, ensure_ascii=False)


class LLMClient:
    """Small wrapper around Groq JSON-mode calls with optional LangSmith tracing."""

    def __init__(self, demo_mode: str = "offline", model_name: str = "openai/gpt-oss-120b", temperature: float = 1.0):
        """Create a client.

        Args:
            demo_mode: "offline" for deterministic classroom mode, "live" for Groq calls.
            model_name: Groq model ID.
            temperature: Sampling temperature for live calls.
        """
        self.demo_mode = demo_mode
        self.model_name = model_name
        self.temperature = temperature
        self._client = None

        if self.demo_mode == "live":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "GROQ_API_KEY is missing. Add it to .env or set DEMO_MODE=offline "
                    "to run the classroom-safe deterministic version."
                )
            if Groq is None:
                raise RuntimeError("The groq package is not installed. Run: pip install -r requirements.txt")
            self._client = Groq(api_key=api_key)

    @traceable(name="Groq JSON completion", run_type="llm")
    def complete_json(self, system_prompt: str, user_payload: Dict[str, Any], purpose: str) -> Dict[str, Any]:
        """Call the model and ask for a JSON object.

        Args:
            system_prompt: Instruction prompt for the agent.
            user_payload: JSON-serialisable payload passed to the model.
            purpose: Human-readable purpose shown in error messages.

        Returns:
            Parsed JSON object.

        Raises:
            RuntimeError: If live mode call fails.
        """
        if self.demo_mode != "live":
            raise RuntimeError("LLMClient.complete_json should only be called in live mode.")

        # Each call is intentionally small and grounded in the local sample data.
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                temperature=self.temperature,
                response_format={"type": "json_object"},
                max_completion_tokens=2048,
                top_p=1,
                reasoning_effort="medium",
                stream=True,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": json.dumps(user_payload, ensure_ascii=False, indent=2),
                    },
                ],
            )
        except Exception as exc:  # pragma: no cover - depends on live API/network
            raise RuntimeError(f"Live LLM call failed while handling {purpose}: {exc}") from exc

        content = "".join(
            chunk.choices[0].delta.content or ""
            for chunk in response
            if chunk.choices
        ) or "{}"
        parsed = parse_json_safely(content)
        if "error" in parsed:
            parsed["purpose"] = purpose
        return parsed

