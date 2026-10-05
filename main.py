"""Command-line runner for the multi-agent travel planner sprint."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict

from agents.manager import TravelPlannerManager
from tools.travel_tools import load_travel_data
from utils import LLMClient, load_project_env, pretty_json


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser.

    Returns:
        Configured argparse parser.
    """
    parser = argparse.ArgumentParser(description="Run the multi-agent travel planner demo.")
    parser.add_argument(
        "--request",
        default=None,
        help="Natural-language travel request. If omitted, the program will prompt for one.",
    )
    parser.add_argument(
        "--demo-mode",
        choices=["offline", "live"],
        default=None,
        help="offline uses deterministic logic; live uses Groq calls.",
    )
    parser.add_argument("--show-trace", action="store_true", help="Print the full state trace.")
    return parser


def run_pipeline(user_request: str, demo_mode: str | None = None) -> Dict[str, Any]:
    """Run the travel-planner pipeline.

    Args:
        user_request: Natural-language request.
        demo_mode: Optional override for DEMO_MODE.

    Returns:
        Full pipeline result.
    """
    settings = load_project_env()
    if demo_mode:
        os.environ["DEMO_MODE"] = demo_mode
        settings["demo_mode"] = demo_mode

    try:
        temperature = float(settings["temperature"])
    except ValueError:
        temperature = 0.2

    llm = LLMClient(
        demo_mode=settings["demo_mode"],
        model_name=settings["model_name"],
        temperature=temperature,
    )
    travel_data = load_travel_data()
    manager = TravelPlannerManager(llm=llm, travel_data=travel_data)
    return manager.run(user_request)


def main() -> None:
    """Run the command-line demo."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    user_request = args.request
    if user_request is None:
        user_request = input("Enter your travel request: ").strip()
    if not user_request:
        parser.error("Travel request cannot be empty.")

    result = run_pipeline(user_request, args.demo_mode)

    print("\n=== Final Travel Plan ===")
    print(pretty_json(result["final_output"]))

    if args.show_trace:
        print("\n=== Full Manager-Worker Trace ===")
        print(pretty_json(result))


if __name__ == "__main__":
    main()

