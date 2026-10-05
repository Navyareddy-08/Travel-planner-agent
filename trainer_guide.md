# Trainer Guide: Multi-Agent Travel Planner Sprint

## Demo goal

By the end of the practical, the class should see a complete manager-worker travel planner that:

1. Extracts requirements from a natural-language request
2. Delegates to specialist workers
3. Uses local travel tools instead of fragile live APIs
4. Produces worker reports with ReAct-style traces
5. Synthesises a draft itinerary
6. Runs a Reflexion-style critique
7. Revises the final itinerary using the critique

## Recommended teaching flow

### 0â€“10 min: Reset the problem

Start with the failure mode: one giant prompt can produce a nice-looking itinerary, but it hides assumptions, ignores hard constraints, and is hard to debug.

Prompt to ask the class:

> If the plan is wrong, where did the failure happen: flight choice, hotel choice, activity pacing, or final synthesis?

Use this question to motivate decomposition.

### 10â€“20 min: Show the folder structure

Open the project tree:

```text
agents/
tools/
data/
main.py
notebook.ipynb
```

Explain that this is a small version of a production agent architecture:
- `data/` simulates external APIs
- `tools/` are deterministic capabilities
- `agents/` decide how to use those capabilities
- `main.py` runs the system
- the notebook teaches the system step by step

### 20â€“35 min: Run the baseline demo

Run:

```bash
python main.py --show-trace
```

Pause at each major section:
- requirements
- worker outputs
- draft itinerary
- critique
- final output

Do not explain every line of code yet. First show the system working.

### 35â€“55 min: Walk through local tools

Open `tools/travel_tools.py`.

Teaching points:
- Tools are boring on purpose: they filter, rank, and calculate.
- Agents should not invent inventory.
- Deterministic tools make LLM behaviour easier to debug.

Ask:

> What would change if this were connected to a live flight API?

Expected answer:
Only the tool adapter should change. The worker contract and manager orchestration can remain mostly stable.

### 55â€“80 min: Walk through worker agents

Open `agents/workers.py`.

Focus on one worker first, then generalise:
- Thought: understand task
- Action: call deterministic tool
- Observation: summarise result
- Decision: choose recommendation

Teaching point:
ReAct is not just a prompt style. It is a debugging format.

### 80â€“105 min: Walk through manager orchestration

Open `agents/manager.py`.

Explain the managerâ€™s job:
- parse request
- delegate
- combine outputs
- preserve assumptions
- respond after critique

Ask:

> Why should the manager not directly invent flights or hotels?

Expected answer:
Because inventory belongs to tools. The manager coordinates, it does not hallucinate facts.

### 105â€“125 min: Add Reflexion

Open `agents/critic.py`.

Show how the critic checks:
- hard constraints
- hotel budget
- number of day blocks
- visible preference coverage

Teaching point:
A useful critic produces fixes, not vague comments.

### 125â€“145 min: Notebook exercises

Use the exercises at the end of `notebook.ipynb`.

Suggested order:
1. Modify the request and compare output.
2. Add one activity to `sample_activities.json`.
3. Add one new critic rule.

### 145â€“160 min: Wrap-up

Connect back to the theory deck:
- Manager-worker pattern creates inspectability.
- ReAct makes worker behaviour auditable.
- Reflexion improves the final answer.
- Local tools reduce classroom friction.
- This same project can later be refactored with deeper agent frameworks.

## Likely questions and ideal answers

### Why use local data instead of live travel APIs?

Because this session teaches orchestration, not API onboarding. Live APIs add authentication, rate limits, and changing schemas. Local tools keep the learning focused. In production, each local tool can be replaced by an API adapter.

### Is every worker an LLM agent?

Not necessarily. In this package, workers combine deterministic tools with optional LLM ranking/explanation. Production systems often use this hybrid pattern because it is cheaper and easier to control.

### Why not use LangGraph here?

LangGraph is introduced later in the course. This sprint should keep the architecture visible in plain Python first. That makes the later framework refactor more meaningful.

### What is the difference between ReAct and Reflexion here?

ReAct is used inside workers: reason, act, observe, decide. Reflexion is used after the first full itinerary: critique, identify issues, revise.

### Why does the critic sometimes say the plan is okay?

That is valid. Reflexion is not only for fixing bad outputs; it also confirms when a result is good enough and asks for clearer assumptions.

### Can this be converted into a web app?

Yes. The cleanest path is to wrap `run_pipeline()` in a FastAPI endpoint or Streamlit UI. Keep the same manager-worker internals.

## Common errors and fixes

### Missing API key in live mode

Set `DEMO_MODE=offline` for classroom-safe execution, or add `GROQ_API_KEY` to `.env`.

### Notebook cannot import local modules

Confirm the notebook is opened from the project root. If using VS Code, select the virtual environment created for this project.

### Empty search results

Use a request matching the local dataset, such as Mumbai to Singapore or Mumbai to Dubai. Alternatively, add matching JSON records.

### Unexpected live-mode wording

Live mode gives the LLM freedom to explain and rank. The output should still be grounded in provided options. If it invents facts, tighten the system prompt or switch to offline mode for the teaching walkthrough.

## Demo timing if running short

Essential:
- Run `python main.py --show-trace`
- Explain folder structure
- Walk through one worker
- Walk through manager orchestration
- Show critic and final refinement

Skip if short:
- Full notebook exercises
- Live mode
- Custom dataset editing
- LangSmith tracing

## Extension ideas

1. Add a restaurant worker.
2. Add a budget guardrail before final output.
3. Add an airport transfer tool.
4. Convert the CLI into a Streamlit app.
5. Add a second critic for safety and user constraints.
6. Replace local hotel data with a real API adapter.

