# AgentProof

**Behavioral testing framework for AI agents — built on UiPath Test Cloud.**

> *If you can't prove it works, don't ship it.*

AgentProof catches AI agent regressions automatically. Define what correct behavior looks like as **behavioral contracts**. AgentProof tests your agent on every deployment, computes a drift score against the last known-good baseline, blocks bad deployments, and generates a compliance-ready PDF report.

Built for the **UiPath AgentHack 2026** — Track 3: UiPath Test Cloud.

---

## Quick Start

### 1. Install dependencies

```bash
pip install uv
uv venv && source .venv/bin/activate
uv pip install -e .
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — add OPENROUTER_API_KEY and DATABASE_URL
```

### 3. Set up Neon database

In the [Neon dashboard](https://neon.tech) SQL editor, run:

```sql
CREATE TABLE test_runs (
    id          TEXT PRIMARY KEY,
    suite_id    TEXT NOT NULL,
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    overall_status TEXT NOT NULL,
    drift_score NUMERIC NOT NULL,
    regressions JSONB,
    results     JSONB
);

CREATE INDEX idx_test_runs_suite_status
ON test_runs (suite_id, overall_status, timestamp DESC);
```

### 4. Start the demo agent

```bash
uvicorn demo_agent.main:app --host 0.0.0.0 --port 8000
```

### 5. Run AgentProof

```bash
# Run 1 — establish baseline (v1 passes all contracts)
python main.py aria_customer_support http://localhost:8000/v1/chat
# Expected: status=PASSED, drift_score=0.0

# Run 2 — detect regressions (v2 breaks 3 contracts)
python main.py aria_customer_support http://localhost:8000/v2/chat
# Expected: status=FAILED, drift_score=~0.31, regressions_count=3
```

---

## Project Structure

```
agentproof/
├── main.py                          # LangGraph graph + UiPath entry point
├── agentproof/
│   ├── contracts.py                 # Pydantic models
│   ├── runner.py                    # HTTP client
│   ├── validator.py                 # LLM-as-judge (Claude via OpenRouter)
│   ├── regression.py                # Drift score calculation
│   ├── reporter.py                  # PDF report generator
│   └── db.py                        # Neon PostgreSQL client
├── demo_agent/
│   └── main.py                      # Aria FastAPI app (v1=good, v2=regressed)
├── test_suites/
│   └── aria_customer_support.json   # Pre-seeded test suite
├── templates/
│   └── report.html                  # Jinja2 PDF report template
└── pyproject.toml
```

---

## Behavioral Contracts

A behavioral contract is a typed specification of what correct agent behavior looks like, evaluated by an LLM-as-judge. Unlike `assertEqual`, contracts work on probabilistic LLM output.

| Contract Type | What It Checks |
|---|---|
| `contains_intent` | Response expresses the specified intent or meaning |
| `does_not_contain` | Response does not contain the specified content |
| `sentiment` | Response has the specified emotional tone |
| `response_length` | Response word count is under the specified number |
| `format_compliance` | Response follows the specified format |
| `safety` | Response contains no harmful content |

---

## How the Drift Score Works

- Each test case has a **severity weight** (critical=3, high=2, medium=1, low=0.5)
- A **regression** = a test that was PASS in the baseline but is FAIL now
- **Drift score** = sum of regressed weights / sum of total weights
- **PASSED** = drift < 5% | **DEGRADED** = 5–15% | **FAILED** = >15%

---

## Deploy to UiPath

```bash
uipath auth
uipath init
uipath pack
uipath publish
```

Then in UiPath Test Manager: New Project → New Test Case → link to the `agentproof` process → Run.

---

## Environment Variables

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM calls |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `DEMO_AGENT_BASE_URL` | Base URL of the demo agent (default: `http://localhost:8000`) |
| `TELEGRAM_BOT_TOKEN` | (Optional) Telegram bot token for failure alerts |
| `TELEGRAM_CHAT_ID` | (Optional) Telegram chat ID for failure alerts |

---

*Built at UiPath AgentHack 2026 by Eeman Asghar*
