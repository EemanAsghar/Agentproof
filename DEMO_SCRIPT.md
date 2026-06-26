# AgentProof — 5-Minute Demo Script

**Track 3: UiPath Test Cloud.** Read the **quoted** lines aloud; do the **[SHOW]** actions on screen.
Target: **5:00 max.** Speak with energy in the first 15 seconds.

---

## ✅ Pre-flight checklist (before you hit record)
- Browser at **1080p**, one window, bookmarks bar hidden, only the tabs you need.
- **Tab 1:** `https://agentproof-opal.vercel.app`
- **Tab 2:** UiPath Orchestrator, signed in, on **Shared → Automations → Jobs**.
- **A fresh UiPath token** copied, ready to paste into `/test`.
- **Pre-run one `agentproof` job** with `/v2/chat` so you already have a green **Successful** job with logs to show (jobs take ~45s — don't wait live on camera).
- Your **editor / Claude Code** open for the 20-second "built with" clip.
- 🔒 Never show `.env`, the token in plain text, or DevTools with a bearer token.
- Use the **live URL** `agentproof-opal.vercel.app` everywhere.

---

## SCENE 1 — The problem (0:00–0:35)
**[SHOW:** the landing page hero, or the `problem-value` diagram, or a one-line prompt diff.**]**

> "This is a one-line change to an AI agent's prompt — someone made it 'friendlier.' The agent still answers every customer, so nothing looks broken. But it has quietly stopped citing policy, started escalating simple refunds to a human, and gone off-script. In production, nobody notices — until a customer does.
> Software teams have CI and tests to catch regressions. AI agent teams have a prompt, and hope. **That's the gap AgentProof closes.**"

---

## SCENE 2 — What it is + architecture (0:35–1:10)
**[SHOW:** the `system-architecture` diagram.**]**

> "AgentProof is the deployment gate for enterprise AI agents — continuous behavioral validation, built on the UiPath Platform.
> AgentProof is itself a **UiPath coded agent**. It discovers the agents published in your Orchestrator, runs each one **natively — as a real UiPath job** — and scores its behavior against contracts using an LLM as a judge. If the behavior regressed, it **blocks the deployment**. UiPath is the execution layer; everything runs on Automation Cloud."

---

## SCENE 3 — It runs ON UiPath (1:10–2:15) — ⭐ THE MONEY SHOT
**[SHOW:** Orchestrator → **Start Job** dialog for `agentproof` (type shows "Agent - python").**]**

> "Let me prove it. This is UiPath Orchestrator. I'm starting **AgentProof itself** as a job. I give it a test suite, and the agent I want to validate."

**[SHOW:** set **Agent Endpoint** = `https://agentproof-opal.vercel.app/v2/chat`, click **Start**. Cut to your pre-run Successful job → open the **Logs** tab and scroll slowly.**]**

> "Inside the job, AgentProof reads its API key from a **UiPath Asset**, calls the agent under test, and runs each response through the LLM judge. Watch the logs — *policy citation: fail… no-escalation: fail… professional tone: pass.* It's evaluating behavioral contracts **live, on the platform**, and UiPath is tracing every step."

**[SHOW:** the job's **Output** tab.**]**

> "And the verdict: **FAILED. Drift fifty-eight percent. Two critical regressions.** The orchestrator and the agent under test both ran on UiPath."

---

## SCENE 4 — Zero-config experience + catch a regression (2:15–3:25)
**[SHOW:** `agentproof-opal.vercel.app/test` → **Connect UiPath tenant** → paste token → **Connect & discover**.**]**

> "That's the engine. Here's the experience. I connect my UiPath tenant — and AgentProof **discovers every agent published in my Orchestrator.**"

**[SHOW:** the dropdown with the 6 agents; pick **ShopEasy Support Agent**; the description auto-fills.**]**

> "I pick the ShopEasy support agent, describe what it *should* do in plain English, and **AI writes the behavioral contracts** — no test code, no JSON."

**[SHOW:** click **Generate contracts** → tick **⚡ Run natively as a UiPath job** → **Validate**. Timeline streams jobs Running → Successful, contracts fail with reasoning.**]**

> "I validate it — again, running it as a **real Orchestrator job** — and AgentProof catches three critical failures, each with the judge's reasoning. **Deployment: blocked.**"

---

## SCENE 5 — Human-in-the-loop, dashboard, report (3:25–4:05)
**[SHOW:** flip the toggle to **Compliant build** (or endpoint `/v1/chat`) → **Validate** → all green → **Safe to deploy**.**]**

> "The developer fixes the prompt, re-validates — all green. **Safe to deploy.** The gate keeps a human in control: AgentProof recommends, a person approves."

**[SHOW:** the **Dashboard** — per-tenant runs, drift history, the agent endpoint column. Click into a run → the **report page**.**]**

> "Every run is recorded on a **per-tenant dashboard**, and each opens a full report — every contract, pass or fail, with the LLM's reasoning and the agent's actual response. That's your audit trail before anything ships."

---

## SCENE 6 — Built with Claude Code (bonus) (4:05–4:35)
**[SHOW:** a quick clip of Claude Code / your editor building part of AgentProof.**]**

> "One more thing. **Every layer of AgentProof** — the coded agent, the validation engine, the UiPath integration, the dashboard — was built using **Claude Code, through UiPath for Coding Agents.** Natural language to a production agentic system."

---

## SCENE 7 — Close (4:35–5:00)
**[SHOW:** landing page / tagline / the live URL on screen.**]**

> "AgentProof brings CI/CD to enterprise AI — validate behavior before deployment, catch regressions automatically, and stop broken agents from ever reaching production. **Every agent passes through the gate before it ships.** Thanks for watching."

---

## Recording tips
- **Record in segments**, not one take — re-do any fumble and stitch later.
- Narrate the **why**, not the clicks ("AgentProof is now executing the agent inside Orchestrator"), not ("I click validate").
- For Scene 3, the **Logs tab with PASS/FAIL lines** is the most convincing 30 seconds in the whole video — linger there.
- If a live job is slow, cut to the pre-run Successful job. Never wait on a spinner on camera.
- End on the live URL so judges can try it.

## Inputs cheat-sheet
| Field | Value |
|---|---|
| Suite Id | `aria_customer_support` |
| Agent Endpoint (FAIL) | `https://agentproof-opal.vercel.app/v2/chat` |
| Agent Endpoint (PASS) | `https://agentproof-opal.vercel.app/v1/chat` |
