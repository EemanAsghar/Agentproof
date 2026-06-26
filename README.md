<div align="center">

<img src="Agentproof%20logo.png" width="110" alt="AgentProof logo"/>

# AgentProof

### The deployment gate for enterprise AI agents.

**Your agent still replies after a prompt change — but does it still *behave*?**
AgentProof validates AI agents against behavioral contracts, catches regressions, and blocks unsafe deployments — running natively on the UiPath Platform.

[![Live App](https://img.shields.io/badge/▶_Live_App-agentproof--opal.vercel.app-f97316?style=for-the-badge)](https://agentproof-opal.vercel.app)

`UiPath AgentHack 2026` · `Track 3 — UiPath Test Cloud` · `License: MIT` · `Built with Claude Code 🤖`

🔗 **[Live app](https://agentproof-opal.vercel.app)**  ·  🎥 **[Demo video](#)** _(add link)_  ·  📊 **[Deck](#)** _(add link)_

</div>

---

## ⚡ The 30-second story

> A developer makes the support agent "friendlier." **It still answers every question** — so nothing looks broken. In production, it has quietly stopped citing policy, started redirecting simple refunds to a human, and begun running long.
>
> **AgentProof catches it before it ships.** It runs the agent as a real UiPath job, scores its behavior against contracts, sees 3 critical regressions, and **blocks the deployment.** The developer reverts one line, re-validates → green → ships safely.

That's the whole product: **CI for agent behavior.**

---

## 🔥 The problem

Software teams have CI, unit tests, and deployment gates. **AI agent teams have a prompt and hope.**

A one-line prompt edit, a model upgrade, a tool/MCP change, or a knowledge-base refresh can *silently* change what an agent does. The agent keeps replying, so humans don't notice — until a customer does. There is no test suite for **behavior**.

---

## ✅ What it does

| | |
|---|---|
| **1. Connect** | Sign in with your UiPath tenant. AgentProof discovers the agents published in your Orchestrator. |
| **2. Describe** | Say what an agent *should* do in plain English — an LLM writes the **behavioral contracts**. No JSON, no config. |
| **3. Validate** | Run each scenario against the agent — **natively, as a real UiPath Orchestrator job** — and an **LLM-as-judge** scores every contract (pass / fail + confidence + reasoning). |
| **4. Detect drift** | Diff against the last passing baseline. A **severity-weighted drift score** → `PASSED` / `DEGRADED` / `FAILED`. |
| **5. Gate** | On `FAILED`: deployment blocked, regressions listed with reasoning, alert fired, PDF report generated, run saved to your per-tenant dashboard. |

---

## 🟠 What makes it *native* to UiPath

Most "agent testing" tools call an HTTP endpoint. **AgentProof actually runs your agent on the platform:**

<img width="1600" height="1050" alt="image" src="https://github.com/user-attachments/assets/010be6c5-3fc2-44f5-b5be-4e1bec7a310f" />


> ✅ **Verified live:** ShopEasy & IT Helpdesk agents ran as Orchestrator jobs (`Successful`) and were judged on their actual output. Five demo agents are published to a real tenant and validate end to end.

---

## 🧩 UiPath platform usage

| Component | How AgentProof uses it |
|---|---|
| **UiPath for Coding Agents (Claude Code)** | The **entire** solution — coded agent, engine, UI, tenant integration — was built with Claude Code. *(Bonus criterion.)* |
| **UiPath Coded Agents (Python SDK)** | The validation engine (`main.py`) is a coded agent (LangGraph pipeline), packed with `uipath pack` and published to Orchestrator. |
| **UiPath Orchestrator** | Discovers published agents, **starts agents as jobs (`StartJobs`)**, polls them, and reads output from `OutputArguments`. |
| **UiPath Assets** | Agents read their runtime secret from an Orchestrator **Asset** — no secrets in the package. |
| **UiPath Automation Cloud** | Agents execute on Automation Cloud; the **tenant is the unit of identity & isolation** (sign-in = your UiPath tenant). |
| **External frameworks** *(encouraged)* | LangGraph (pipeline), OpenAI `gpt-4o-mini` via OpenRouter (LLM judge). UiPath stays the orchestration & governance layer. |

---

## 🤖 Built with UiPath for Coding Agents

Every layer of AgentProof — the LangGraph engine, the five published coded agents, the Orchestrator REST integration, native job execution, per-tenant auth, and the dashboard — was built using **Claude Code via UiPath for Coding Agents**. The demo video shows it in action.

---

## 🚀 Quick start

**Prerequisites:** Python 3.12+, `uv`, an `OPENROUTER_API_KEY`, a PostgreSQL `DATABASE_URL`, and a UiPath Automation Cloud tenant.

```bash
# 1. Install
uv venv && source .venv/bin/activate && uv pip install -e .

# 2. Configure
cp .env.example .env        # set OPENROUTER_API_KEY and DATABASE_URL

# 3. Run the validator as a coded agent (locally or on UiPath)
uv run uipath run agent '{"suite_id":"aria_customer_support","agent_endpoint":"https://agentproof-opal.vercel.app/v1/chat"}'   # baseline → PASSED
uv run uipath run agent '{"suite_id":"aria_customer_support","agent_endpoint":"https://agentproof-opal.vercel.app/v2/chat"}'   # regressed → FAILED

# 4. Publish to Orchestrator
uipath auth && uipath pack && uipath publish --tenant
```

**Or just open the live app** → [agentproof-opal.vercel.app/test](https://agentproof-opal.vercel.app/test) → **Connect UiPath tenant** → pick an agent → **Validate**.

<details>
<summary><strong>Database schema</strong></summary>

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
</details>

---

## 📜 Behavioral contracts

A contract is a typed rule the agent's response must satisfy — judged by an LLM, so it works on probabilistic output (unlike `assertEqual`).

`contains_intent` · `does_not_contain` · `sentiment` · `response_length` · `format_compliance` · `safety`

Each test case carries a severity (**critical ×3 · high ×2 · medium ×1 · low ×0.5**) that weights the drift score: `PASSED` < 5% · `DEGRADED` 5–15% · `FAILED` > 15%.

---

## 🗂️ Architecture

```
main.py                  AgentProof coded agent — LangGraph pipeline (UiPath entry point)
                         load_suite → run_tests → detect_regressions → save → report → notify
agentproof/
  contracts.py           Pydantic models (contracts, cases, results)
  runner.py              Calls the target agent
  validator.py           LLM-as-judge (gpt-4o-mini via OpenRouter)
  regression.py          Severity-weighted drift + baseline comparison
  reporter.py            PDF report (Jinja2 + WeasyPrint)
  db.py                  PostgreSQL persistence (per-tenant)
server.py                Control panel: landing, /live cinematic demo, /test onboarding,
                         per-tenant dashboard, reports, UiPath discovery + native job execution
shopease_support_agent/  Demo target agent — published UiPath coded agent
target_agents/           4 more published agents (invoice, IT, HR, loan)
test_suites/             Behavioral test suites (JSON)
```

---

<div align="center">

**AgentProof** — *every agent passes through the gate before it ships.*

MIT licensed · Built with Claude Code via UiPath for Coding Agents · UiPath AgentHack 2026 · Track 3: UiPath Test Cloud

</div>
