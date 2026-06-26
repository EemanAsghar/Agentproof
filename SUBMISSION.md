# AgentProof — Submission Pack

> Copy/paste content for the Devpost project page, a 5-minute demo script, and a deck outline.
> **Track 3: UiPath Test Cloud.** Live app: https://agentproof-opal.vercel.app

---

## 1) Devpost project page

### Title
**AgentProof — The Deployment Gate for Enterprise AI Agents**

### Tagline
Continuous behavioral validation & regression detection for AI agents, built on the UiPath Platform.

### Track
Track 3 — UiPath Test Cloud (agentic software testing for AI-driven automations).

### Inspiration
Every software team has CI, tests, and deployment gates. AI agent teams have a prompt and hope. We kept seeing the same failure: someone tweaks a system prompt to be "friendlier," the agent still answers, nothing looks broken — and in production it has quietly stopped citing policy, started leaking data, or begun escalating things it should resolve. There is no test suite for *behavior*. We built the missing quality layer so a UiPath agent can be gated before it ships.

### What it does
AgentProof validates an AI agent against **behavioral contracts** on every change and blocks unsafe deployments:
- **Connect** your UiPath tenant — AgentProof discovers the agents published in your Orchestrator.
- **Describe** what an agent should do in plain English — an LLM authors the behavioral contracts (no JSON, no config).
- **Validate** — every test scenario runs against the agent, and an LLM-as-judge scores each contract with a pass/fail, a confidence, and natural-language reasoning.
- **Detect regressions** — results are diffed against the last passing baseline; a severity-weighted **drift score** yields PASSED / DEGRADED / FAILED.
- **Gate the deployment** — on FAILED, AgentProof blocks the release, lists the regressions with reasoning, fires an alert, generates a PDF report, and records the run on a per-tenant dashboard.

### How we built it
- **AgentProof's engine is a UiPath coded agent** (`main.py`) — a LangGraph pipeline (load suite → run tests → detect regressions → save → report → notify), built with the UiPath Python SDK and published to Orchestrator with `uipath pack` / `uipath publish`.
- **UiPath Orchestrator integration** — AgentProof signs the user in with their UiPath tenant (token verified against Orchestrator), then discovers their published agents via the Orchestrator OData API. We also published five demo target agents to a real tenant to show discovery end to end.
- **LLM-as-judge** — OpenAI `gpt-4o-mini` via OpenRouter scores each contract.
- **Control panel** — a FastAPI app (landing, a cinematic `/live` walkthrough, a zero-config `/test` onboarding flow, a per-tenant dashboard, and PDF reports). Persistence is PostgreSQL (Neon), scoped per tenant.
- **Built with UiPath for Coding Agents (Claude Code)** — the entire solution, from the coded agent and engine to the tenant integration and UI, was built using Claude Code.

### UiPath components used
UiPath for Coding Agents (Claude Code) · UiPath Coded Agents (Python SDK) · UiPath Orchestrator (publish + discover) · UiPath Automation Cloud.
External frameworks (encouraged): LangGraph, OpenAI/OpenRouter. UiPath is the orchestration & governance layer.

### Challenges we ran into
- UiPath access tokens are short-lived; we made tenant connect resilient (clear 401 messaging, folder-scope fallbacks) and published packages via the Orchestrator REST API.
- Validating probabilistic agents needed an LLM-as-judge with severity weighting and baseline comparison rather than brittle string asserts.
- Making the "good" agent reliably pass meant tightening prompts so the agent obeys its own rules.

### Accomplishments we're proud of
- A working end-to-end gate: connect a real tenant → discover real agents → AI-author contracts → validate live → deployment recommendation, with per-tenant auth and isolation.
- "Sign in with UiPath tenant" — identity derived from a verified Orchestrator token, no passwords.
- A demo that shows a regression being caught and the deployment blocked, then fixed and shipped safely.

### What we learned
Behavioral regressions are invisible to humans but obvious to a judge with explicit contracts. Treating an agent release like a software release — baseline, diff, gate — is the missing primitive for enterprise AI.

### What's next
- Deeper **Test Cloud / Test Manager** integration (sync contracts as test cases, push results).
- Enforced deployment gates in CI and Maestro flows; multi-model judge consensus.
- Scheduled / triggered validation on every new package version.

*(Native Orchestrator **job-invocation** is already built: AgentProof validates a discovered agent by running it as a real UiPath job and judging its output.)*

### Built with
Python · LangGraph · UiPath Python SDK · UiPath Orchestrator · FastAPI · PostgreSQL (Neon) · OpenAI/OpenRouter · Claude Code (UiPath for Coding Agents)

---

## 2) Demo video script (≤ 5 minutes)

**Goal:** show it *running on UiPath*, catch a real regression, and show Claude Code building it. Record real screen, talk over it.

**0:00–0:30 — The problem (hook).**
"Every software team has CI and deployment gates. AI agent teams have a prompt and hope. Watch what happens when someone makes an agent 'friendlier.'" Show the one-line prompt diff.

**0:30–1:10 — AgentProof runs on UiPath.**
Show the **AgentProof coded agent published in Orchestrator** and trigger a validation run (Orchestrator job, or `uipath run agent '{...}'`). Narrate: "AgentProof is a UiPath coded agent — a LangGraph pipeline. UiPath is the execution layer." Show the console output: tests running, drift score, FAILED.

**1:10–2:10 — Native tenant discovery (the platform story).**
On `/test`, **Connect UiPath tenant** → the dropdown fills with the agents published in the tenant (ShopEasy, Invoice, IT Helpdesk, HR, Loan). "AgentProof discovers every agent in your Orchestrator. Sign-in identity is your UiPath tenant."

**2:10–3:30 — Validate natively, as a real UiPath job (the platform moment).**
Pick **ShopEasy Support Agent** → description auto-fills → **Generate contracts** (AI writes them) → tick **"⚡ Run natively as a UiPath Orchestrator job"** → **Validate**. The timeline shows **real job IDs going Running → Successful** — AgentProof is *executing the agent in Orchestrator* and judging its actual output. Then show a regression caught (toggle to the regressed build / HTTP mode for speed) → **Deployment blocked** → fix → **Safe to deploy**. "Same agent, two builds — and we validated it by actually running it on UiPath."

**3:30–4:10 — Dashboard + governance.**
Open the **per-tenant dashboard**: runs scoped to your tenant, drift history, the agent endpoint, click into a report with per-contract reasoning + confidence. Mention PDF report + alert.

**4:10–4:50 — Built with UiPath for Coding Agents (bonus).**
Show a short clip of **Claude Code** building part of AgentProof (e.g., adding the tenant integration or an endpoint). "We built the entire solution — the coded agent, the engine, the UiPath integration — with Claude Code via UiPath for Coding Agents."

**4:50–5:00 — Close.**
"AgentProof: every UiPath agent passes through the gate before it ships." Show the live URL.

---

## 3) Deck outline (use the provided template)

1. **Title** — AgentProof · Track 3: UiPath Test Cloud · live URL.
2. **Problem** — CI exists for code, not for agent behavior; silent regressions reach production.
3. **Solution** — the deployment gate: contracts → judge → drift → gate.
4. **Demo screenshot** — regression caught / deployment blocked.
5. **Architecture** — AgentProof coded agent on UiPath Orchestrator; discovery; control panel; LLM judge.
6. **UiPath platform usage** — coded agent, Orchestrator discovery, Automation Cloud, built with Claude Code (bonus).
7. **Why it matters (business impact)** — ship agents with confidence; governance & audit trail; scales across every published agent.
8. **What's next** — native job-invocation, Test Manager sync, CI/Maestro enforcement.
9. **Team + ask.**

---

## 4) Pre-submission checklist
- [ ] Devpost page filled (title, Track 3, description above, screenshots).
- [ ] Demo video ≤ 5 min on YouTube/Vimeo, link in submission (shows it running on UiPath + Claude Code clip).
- [ ] Public GitHub repo with this README + **MIT LICENSE** (done).
- [ ] Solution runs on UiPath Automation Cloud (coded agent published; discovery live).
- [ ] Presentation deck uploaded, link shared with view access.
- [ ] Submission lists UiPath components + states it was built with coding agents.
- [ ] Use the **live URL** `agentproof-opal.vercel.app` everywhere (not the stale alias).
- [ ] (Optional) Product-feedback survey for the $1,500 award.
