# AgentProof

**The deployment gate for enterprise AI agents.**
*Continuous behavioral validation & regression detection for agents — built on the UiPath Platform.*

> **UiPath AgentHack 2026 — Track 3: UiPath Test Cloud**
> *Agentic software testing for AI-driven automations.*

🔗 **Live app:** https://agentproof-opal.vercel.app
🎥 **Demo video:** _(add YouTube/Vimeo link)_
📊 **Deck:** _(add link)_

---

## The problem

Software teams have CI, unit tests, and deployment gates. **AI agent teams have a prompt and hope.**

A one-line change to a system prompt, a model upgrade, an MCP/tool update, or a knowledge-base refresh can *silently* change an agent's behavior. The agent still replies — so nothing looks broken — but it may have stopped citing policy, started leaking data, or begun escalating things it should resolve. There is no "test suite" that catches behavioral regressions before they reach a customer.

**AgentProof is the missing quality layer:** it validates an agent against behavioral contracts on every change, detects regressions against the last known-good baseline, and produces a deployment recommendation — so a UiPath agent can be gated *before* it ships.

---

## What it does

1. **Connect** — Sign in with your UiPath tenant. AgentProof discovers the agents published in your Orchestrator.
2. **Describe** — Say what an agent *should* do in plain English. An LLM authors **behavioral contracts** (no JSON, no config).
3. **Validate** — AgentProof runs each test scenario against the agent — **natively as a real UiPath Orchestrator job**, or against an HTTP endpoint — and uses an **LLM-as-judge** to score every contract (pass/fail + confidence + reasoning).
4. **Detect drift** — Results are compared to the last passing baseline. A **severity-weighted drift score** (critical ×3, high ×2, medium ×1, low ×0.5) produces a status: `PASSED` / `DEGRADED` / `FAILED`.
5. **Gate the deployment** — `FAILED` ⇒ deployment blocked, regressions listed with LLM reasoning, alert fired, PDF report generated, results persisted to a per-tenant dashboard.

The result is a single sentence every enterprise wants to be true:
**"Every agent passes through AgentProof before it ships."**

---

## How it runs on the UiPath Platform

UiPath is the **execution and orchestration layer**; the web app is the control panel.

```
Developer / Orchestrator trigger
        │
        ▼
┌──────────────────────────────────────────────┐
│  AgentProof — UiPath coded agent (published)  │   ← runs on UiPath Automation Cloud
│  LangGraph pipeline (main.py):                │
│   load_suite → run_tests → detect_regressions │
│   → save_results → generate_report → notify   │
└──────────────────────────────────────────────┘
        │ discovers / targets
        ▼
   Agents published in your UiPath Orchestrator
   (ShopEasy Support, Invoice, IT Helpdesk, HR, Loan …)
        │ verdicts + drift
        ▼
   Per-tenant dashboard + PDF report + alert
```

### UiPath components used
| Component | How AgentProof uses it |
|---|---|
| **UiPath for Coding Agents (Claude Code)** | The entire solution — agent, engine, UI, integration — was built using Claude Code as the coding agent. *(Bonus-point criterion.)* |
| **UiPath Coded Agents (Python SDK)** | AgentProof's validation engine (`main.py`) is a coded agent built with the UiPath Python SDK + LangGraph, packaged with `uipath pack` and published to Orchestrator. |
| **UiPath Orchestrator** | Agents are published as packages/releases; AgentProof authenticates to the tenant, **discovers published agents**, and **executes them as real Orchestrator jobs** — it starts a job (`StartJobs`), polls it to completion, and reads the agent's output from `OutputArguments` to validate it. Sign-in identity = the UiPath tenant. |
| **UiPath Assets** | Published agents read their runtime secret (`OPENROUTER_API_KEY`) from a UiPath Orchestrator **Asset**, so jobs run on Automation Cloud without secrets in the package. |
| **UiPath Automation Cloud** | The coded agent runs on Automation Cloud; the tenant is the unit of identity and isolation. |
| **External frameworks (encouraged)** | LangGraph (pipeline orchestration), OpenAI/OpenRouter (LLM-as-judge: `gpt-4o-mini`). UiPath remains the orchestration/governance layer. |

### Built with coding agents
This project was built **with Claude Code via UiPath for Coding Agents** — from the LangGraph engine and the published coded agents to the live dashboard, the tenant integration, and per-tenant auth. The demo video shows Claude Code building parts of the solution (Platform-Usage bonus).

---

## Quick start

### Prerequisites
- Python 3.12+ and [`uv`](https://github.com/astral-sh/uv) (or pip)
- An OpenRouter API key (LLM judge) — `OPENROUTER_API_KEY`
- A Neon (or any) PostgreSQL database — `DATABASE_URL`
- A UiPath Automation Cloud tenant (to publish/discover agents)

### 1. Install
```bash
uv venv && source .venv/bin/activate
uv pip install -e .
```

### 2. Configure
```bash
cp .env.example .env
# set OPENROUTER_API_KEY and DATABASE_URL
```

### 3. Create the runs table
```sql
CREATE TABLE test_runs (
    id             TEXT PRIMARY KEY,
    suite_id       TEXT NOT NULL,
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    overall_status TEXT NOT NULL,
    drift_score    NUMERIC NOT NULL,
    regressions    JSONB,
    results        JSONB,
    agent_endpoint TEXT,
    tenant_id      TEXT
);
CREATE INDEX idx_test_runs_tenant ON test_runs (tenant_id, timestamp DESC);
```

### 4. Run the validator as a coded agent (locally or on UiPath)
```bash
# Establish a baseline (passing build)
uv run uipath run agent '{"suite_id":"aria_customer_support","agent_endpoint":"https://agentproof-opal.vercel.app/v1/chat"}'
# Detect regressions (regressed build)
uv run uipath run agent '{"suite_id":"aria_customer_support","agent_endpoint":"https://agentproof-opal.vercel.app/v2/chat"}'
```

### 5. Publish to UiPath Orchestrator
```bash
uipath auth
uipath pack
uipath publish --tenant
```

### 6. Control panel
Open the "Test your agent" flow at `https://agentproof-opal.vercel.app/test`, **Connect UiPath tenant**, and validate any discovered agent.

---

## Behavioral contracts

A behavioral contract is a typed rule the agent's response must satisfy — evaluated by an LLM-as-judge, so it works on probabilistic output (unlike `assertEqual`).

| Type | Checks |
|---|---|
| `contains_intent` | Response expresses the specified intent |
| `does_not_contain` | Response avoids the specified content |
| `sentiment` | Response has the specified tone |
| `response_length` | Word count under the limit |
| `format_compliance` | Response follows the specified format |
| `safety` | No harmful / disallowed content |

Each test case has a severity (critical / high / medium / low) that weights the drift score.

---

## Repository structure
```
main.py                     # AgentProof coded agent — LangGraph pipeline (UiPath entry point)
agentproof/
  contracts.py              # Pydantic models (contracts, test cases, results)
  runner.py                 # Calls the target agent
  validator.py              # LLM-as-judge (OpenAI gpt-4o-mini via OpenRouter)
  regression.py             # Severity-weighted drift score + baseline comparison
  reporter.py               # PDF report (Jinja2 + WeasyPrint)
  db.py                     # PostgreSQL persistence (per-tenant)
server.py                   # Control panel: landing, /live demo, /test onboarding,
                            #   per-tenant dashboard, reports, agent endpoints, UiPath REST integration
shopease_support_agent/     # Demo target agent — published UiPath coded agent
target_agents/              # 4 more published UiPath coded agents (invoice, IT, HR, loan)
test_suites/                # Behavioral test suites (JSON)
templates/report.html       # PDF report template
```

---

## License
MIT — see [LICENSE](LICENSE).

*Built with Claude Code via UiPath for Coding Agents · UiPath AgentHack 2026 · Track 3: UiPath Test Cloud · by Eeman Asghar*
