# Mini-Project Sprint: Multi-Agent Travel Planner

A Python multi-agent travel planner that builds a trip around the traveler's choices and preferences. It provides flight, hotel, and activity details, creates a day-by-day itinerary, and estimates the trip budget. A manager coordinates specialist agents and a Reflexion-style critic to review and refine the plan. Run it offline with sample data or in live mode using Groq's `openai/gpt-oss-120b` model, with optional LangSmith tracing.

## Prerequisites

- Python 3.10 or 3.11
- VS Code, JupyterLab, or Jupyter Notebook
- Groq API key only if running `DEMO_MODE=live`
- LangSmith account only if enabling tracing

The default `offline` mode runs without paid APIs using deterministic classroom-safe logic and local sample data.

## Setup

Download or clone this folder, then open a terminal inside the project root.

### Option A: venv

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Option B: conda

```bash
conda create -n travel-planner-agent python=3.11
conda activate travel-planner-agent
pip install -r requirements.txt
```

### Configure environment

```bash
cp .env.sample .env
```

For the first run, keep:

```text
DEMO_MODE=offline
```

For live Groq calls, update `.env`:

```text
DEMO_MODE=live
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=openai/gpt-oss-120b
```

Optional LangSmith tracing:

```text
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=ls__your-key-here
LANGSMITH_PROJECT=BIA_Mini_Project_Sprint_Travel_Planner
```

Keep real credentials in `.env` only. `.gitignore` excludes `.env`, virtual environments, and Python cache files; commit `.env.sample` as the credential-free template instead. Never paste API keys into source files, notebooks, or commits.

## How to run

### Guided teaching notebook

```bash
jupyter notebook notebook.ipynb
```

Run cells from top to bottom. The notebook starts in offline mode unless `.env` says otherwise.

### Command-line demo

```bash
python main.py
```

When run without `--request`, the program prompts you to enter a travel request.

Print the complete manager-worker trace:

```bash
python main.py --show-trace
```

Use a custom request:

```bash
python main.py --request "Plan a 3-day Singapore trip from Mumbai for one person. Focus on food and culture, avoid premium hotels."
```

Force live mode for a run:

```bash
python main.py --demo-mode live
```

## What each file does

- `notebook.ipynb` â€” guided practical walkthrough for live teaching
- `main.py` â€” command-line runner for the complete pipeline
- `agents/manager.py` â€” manager agent that extracts requirements, delegates, synthesises, and refines
- `agents/workers.py` â€” flight, hotel, and activity worker agents
- `agents/critic.py` â€” Reflexion-style critic
- `tools/travel_tools.py` â€” local deterministic search tools over sample data
- `utils.py` â€” environment loading, Groq wrapper, JSON helpers
- `data/sample_flights.json` â€” simulated flight inventory
- `data/sample_hotels.json` â€” simulated hotel inventory
- `data/sample_activities.json` â€” simulated activity inventory
- `data/demo_requests.json` â€” sample classroom prompts
- `prompts/prompt_contracts.md` â€” agent input/output contracts
- `outputs/sample_run_offline.md` â€” expected output shape
- `.env.sample` â€” environment variable template
- `trainer_guide.md` â€” trainer flow, timing, questions, and troubleshooting

## Expected output

A successful run prints:

1. A structured requirement extraction
2. Worker outputs with ReAct-style traces
3. A draft itinerary
4. A critic report
5. A refined final itinerary
6. Changes made after critique

Offline mode gives deterministic results. Live mode may produce different wording and ranking explanations while staying grounded in local data.

## Estimated API cost

Offline mode costs â‚¹0.

Live mode uses approximately 5â€“7 compact Groq calls over small local data. With `openai/gpt-oss-120b`, a full demo run is designed to remain well below the session target cost. Keep sample data small during class to avoid unnecessary token usage.

## Troubleshooting

### `GROQ_API_KEY is missing`

Either add a valid key to `.env` or set:

```text
DEMO_MODE=offline
```

### `ModuleNotFoundError`

Confirm the virtual environment is activated and dependencies are installed:

```bash
pip install -r requirements.txt
```

### No matching flights or hotels

The local dataset is intentionally small. Use one of the included demo requests or add new records to the JSON files.

### LangSmith traces not appearing

Check that:

```text
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=...
```

Then run in `DEMO_MODE=live`.

## Further reading

- Groq Python SDK documentation: https://github.com/groq/groq-python
- LangSmith tracing documentation: https://docs.smith.langchain.com/
- ReAct prompting paper: https://arxiv.org/abs/2210.03629
- Reflexion paper: https://arxiv.org/abs/2303.11366
- Expedia in ChatGPT product page: https://www.expedia.com/product/expedia-in-chatgpt/
- Booking.com and OpenAI case study: https://openai.com/index/booking-com/

