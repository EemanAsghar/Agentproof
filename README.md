<div align="center">

<img src="Agentproof%20logo.png" width="96" alt="AgentProof"/>

# AgentProof

### The deployment gate for enterprise AI agents

Continuous behavioral validation and regression detection for AI agents — running natively on the UiPath Platform.

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-informational.svg?style=flat-square)](LICENSE)
[![UiPath AgentHack 2026](https://img.shields.io/badge/UiPath-AgentHack%202026-FA4616.svg?style=flat-square)](https://uipath-agenthack.devpost.com/)
[![Track 3](https://img.shields.io/badge/Track%203-UiPath%20Test%20Cloud-1f6feb.svg?style=flat-square)](#)
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-8A5CF6.svg?style=flat-square)](#built-with-uipath-for-coding-agents)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white&style=flat-square)
![LangGraph](https://img.shields.io/badge/LangGraph-engine-1C3C3C?style=flat-square)
![UiPath](https://img.shields.io/badge/UiPath-Orchestrator-FA4616?logo=uipath&logoColor=white&style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-control_plane-009688?logo=fastapi&logoColor=white&style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-persistence-4169E1?logo=postgresql&logoColor=white&style=flat-square)
![OpenAI](https://img.shields.io/badge/LLM-as--judge-412991?logo=openai&logoColor=white&style=flat-square)

<br/>

**[Live application](https://agentproof-opal.vercel.app)** &nbsp;·&nbsp; **[Demo video](#)** *(add link)* &nbsp;·&nbsp; **[Presentation](#)** *(add link)*

</div>

<br/>

---

<br/>

## Overview

AI agents change behavior silently. A prompt edit, a model upgrade, a tool or MCP change, or a knowledge-base refresh can alter how an agent responds while it continues to reply normally — so the regression reaches production unnoticed. Conventional tests assert on exact output and cannot validate probabilistic, language-based behavior.

AgentProof brings CI/CD discipline to AI agents. It expresses expected behavior as **behavioral contracts**, validates an agent against them on every change, compares the results to the last known-good baseline, and produces a deployment decision — gating releases before they reach users.

AgentProof is built and run **on the UiPath Platform**: the validation engine is a UiPath coded agent, and the agents it validates are executed as real UiPath Orchestrator jobs.

![Problem to value — the difference AgentProof makes](docs/problem-value.png)

> **In one line —** AgentProof is continuous integration for agent *behavior*: it catches the regressions that still "reply correctly" but no longer act correctly.

<br/>

---

<br/>

## How it works

| Step | What happens |
|:----:|:-------------|
| **1 · Connect** | Authenticate with a UiPath tenant. AgentProof discovers the agents published in your Orchestrator. |
| **2 · Define** | Describe expected behavior in plain language; an LLM generates the behavioral contracts. No manual test authoring. |
| **3 · Validate** | Each scenario runs against the agent — natively, as a real UiPath Orchestrator job — and an LLM-as-judge scores every contract with a pass/fail, confidence, and reasoning. |
| **4 · Detect drift** | Results are compared against the last passing baseline. A severity-weighted drift score yields `PASSED`, `DEGRADED`, or `FAILED`. |
| **5 · Gate** | On `FAILED`, the deployment is blocked. Regressions are listed with reasoning, an alert is raised, a PDF report is generated, and the run is recorded on a per-tenant dashboard. |

### Why it's different

| Capability | Unit / integration tests | Prompt-eval tools | **AgentProof** |
|:-----------|:----------------------:|:-----------------:|:--------------:|
| Validates language-based behavior | ✗ | ✓ | ✓ |
| Regression detection vs. a baseline | ✗ | partial | ✓ |
| Executes on UiPath Orchestrator | ✗ | ✗ | ✓ |
| Deployment gate + audit trail | ✗ | ✗ | ✓ |

<br/>

---

<br/>

## Native execution on UiPath

Most agent-testing tools call an HTTP endpoint. **AgentProof runs the agent on the platform:** it starts a real Orchestrator job (`StartJobs`), polls the job to completion, reads the agent's output from `OutputArguments`, and validates that output against the contracts.

UiPath Automation Cloud is the **execution layer**; the web application is only the **control plane**.

![AgentProof system architecture](docs/system-architecture.png)

> **Verified live —** the ShopEasy and IT Helpdesk agents were executed as Orchestrator jobs (state `Successful`) and judged on their actual output. Five demo agents are published to a real tenant and validate end to end.

<br/>

---

<br/>

## UiPath platform components

| Component | Usage |
|:----------|:------|
| **UiPath for Coding Agents** *(Claude Code)* | The entire solution — coded agent, engine, control plane, and tenant integration — was built using Claude Code. |
| **UiPath Coded Agents** *(Python SDK)* | The validation engine (`main.py`) is a coded agent implemented as a LangGraph pipeline, packaged with `uipath pack` and published to Orchestrator. |
| **UiPath Orchestrator** | Discovers published agents, starts them as jobs (`StartJobs`), polls execution, and retrieves results from `OutputArguments`. |
| **UiPath Assets** | Published agents read their runtime secret from an Orchestrator Asset, keeping credentials out of the package. |
| **UiPath Automation Cloud** | Agents execute on Automation Cloud; the tenant is the unit of identity and data isolation. |
| **External frameworks** | LangGraph for pipeline orchestration; OpenAI `gpt-4o-mini` (via OpenRouter) as the LLM judge. UiPath remains the orchestration and governance layer. |

<br/>

---

<br/>

## Architecture

A validation run proceeds from tenant connection through to the deployment gate:

![AgentProof native validation flow](docs/native-validation-flow.png)

<br/>

The validation engine is a **LangGraph coded agent** of six nodes. Each stage has an explicit input and output, so a run is fully traceable end to end:

![Coded-agent pipeline (LangGraph)](docs/coded-agent-pipeline.png)

| # | Node | Input | Output | Stack |
|:-:|:-----|:------|:-------|:------|
| **1** | `load_suite` | `suite_id` | test cases + baseline | ![JSON](https://img.shields.io/badge/JSON-grey?style=flat-square) |
| **2** | `run_tests` | test cases | agent responses | ![UiPath](https://img.shields.io/badge/UiPath-FA4616?logo=uipath&logoColor=white&style=flat-square) ![LLM](https://img.shields.io/badge/LLM-412991?logo=openai&logoColor=white&style=flat-square) |
| **3** | `detect_regressions` | responses | drift score + regressions | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=flat-square) |
| **4** | `save_results` | run record | persisted run | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white&style=flat-square) |
| **5** | `generate_report` | run record | PDF report | ![Reports](https://img.shields.io/badge/Reports-PDF-b5462e?style=flat-square) |
| **6** | `notify` | run status | alert | ![Notify](https://img.shields.io/badge/Notify-Email%2FSlack-f97316?style=flat-square) |

<br/>

<details>
<summary><strong>Project structure</strong></summary>

```
main.py                  Validation engine — LangGraph coded agent (UiPath entry point)
                         load_suite → run_tests → detect_regressions → save → report → notify
agentproof/
  contracts.py           Pydantic models (contracts, test cases, results)
  runner.py              Invokes the target agent
  validator.py           LLM-as-judge (gpt-4o-mini via OpenRouter)
  regression.py          Severity-weighted drift score and baseline comparison
  reporter.py            PDF report generation (Jinja2 + WeasyPrint)
  db.py                  PostgreSQL persistence (per-tenant)
server.py                Control plane: landing, live walkthrough, onboarding,
                         per-tenant dashboard, reports, UiPath discovery and job execution
shopease_support_agent/  Demo target agent (published UiPath coded agent)
target_agents/           Additional published agents (invoice, IT, HR, loan)
test_suites/             Behavioral test suites (JSON)
```
</details>

<br/>

---

<br/>

## Behavioral contracts

A behavioral contract is a typed rule the agent's response must satisfy. Because contracts are evaluated by an LLM judge, they validate probabilistic, language-based behavior that exact-match assertions cannot.

| Contract type | Validates |
|:--------------|:----------|
| `contains_intent` | The response expresses a required intent or commitment |
| `does_not_contain` | The response avoids prohibited content or actions |
| `sentiment` | The response holds a required tone |
| `response_length` | The response stays within a word limit |
| `format_compliance` | The response follows a required structure |
| `safety` | The response contains no harmful or disallowed content |

Each test case carries a severity that weights the drift score — **`critical` ×3, `high` ×2, `medium` ×1, `low` ×0.5**. Status thresholds: `PASSED` below 5%, `DEGRADED` 5–15%, `FAILED` above 15%.

<br/>

---

<br/>

## Getting started

**Prerequisites** — Python 3.12+, [`uv`](https://github.com/astral-sh/uv), an `OPENROUTER_API_KEY`, a PostgreSQL `DATABASE_URL`, and a UiPath Automation Cloud tenant.

```bash
# 1. Install
uv venv && source .venv/bin/activate && uv pip install -e .

# 2. Configure
cp .env.example .env        # set OPENROUTER_API_KEY and DATABASE_URL

# 3. Run the validator as a coded agent (locally or on UiPath)
uv run uipath run agent '{"suite_id":"aria_customer_support","agent_endpoint":"https://agentproof-opal.vercel.app/v1/chat"}'   # baseline → PASSED
uv run uipath run agent '{"suite_id":"aria_customer_support","agent_endpoint":"https://agentproof-opal.vercel.app/v2/chat"}'   # regressed → FAILED

# 4. Publish to UiPath Orchestrator
uipath auth && uipath pack && uipath publish --tenant
```

Alternatively, use the hosted application: open **[agentproof-opal.vercel.app/test](https://agentproof-opal.vercel.app/test)**, connect your UiPath tenant, select a published agent, and run a validation.

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

<br/>

---

<br/>

## Built with UiPath for Coding Agents

Every layer of AgentProof — the LangGraph validation engine, the published coded agents, the Orchestrator REST integration, native job execution, per-tenant authentication, and the dashboard — was developed using **Claude Code via UiPath for Coding Agents**. The demo video includes the build process.

<br/>

---

<br/>

## License

Released under the [MIT License](LICENSE).

<div align="center">
<br/>

**AgentProof** — every agent passes through the gate before it ships.

<sub>UiPath AgentHack 2026 · Track 3: UiPath Test Cloud</sub>

</div>
