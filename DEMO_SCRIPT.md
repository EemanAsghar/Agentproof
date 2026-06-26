# AgentProof — 5-Minute Demo Script

**Track 3: UiPath Test Cloud.** Read the **quoted** lines aloud; do the **[SHOW]** actions on screen.
Target **5:00**. Tone: a product keynote with a beginning, conflict, and resolution — not a feature tour.
Rule of thumb: every spoken sentence either **builds suspense**, **explains why it matters**, or **lands business value**. Never narrate clicks.

---

## ✅ Pre-flight checklist (before you record)
- Browser at **1080p**, one window, bookmarks bar hidden.
- **Tab 1 — Orchestrator:** signed in, on **Shared → Automations → Jobs**, with a **pre-run Successful `agentproof` job** ready (so the Logs are already there — never wait on a spinner on camera).
- **Tab 2 — the experience:** `agentproof-opal.vercel.app/live` (the cinematic gate + recovery animation) and `/dashboard` open.
- Your **editor / Claude Code** open for a 15-second "built with" clip.
- 🔒 Never show `.env`, a token in plain text, or DevTools.

---

## SCENE 1 — The hook (0:00–0:30)
**[SHOW:** a one-line prompt change, or the `problem-value` graphic.**]**

> "Someone makes an AI support agent a little *friendlier*. One line of text. It still answers every customer — so it ships.
> What nobody sees is that it's quietly stopped following the rules. It's not citing policy. It's pushing simple refunds to a human. And the first person to find out… is a customer."

*(Bridge ↓)*
> "Software teams catch this with tests. AI teams don't have them."

---

## SCENE 2 — The distinction (0:30–0:55)
**[SHOW:** the `system-architecture` diagram — on screen only briefly.**]**

> "That's AgentProof. And here's the one idea to remember: **traditional testing checks your code. AgentProof checks your AI's *behavior* — before it goes live.**
> It runs where your agents already live — as a **UiPath coded agent, on UiPath Automation Cloud.** This isn't a mock-up. So let me show you the real thing."

---

## SCENE 3 — Real, running on UiPath (0:55–2:15) ⭐ *the centerpiece*
**[SHOW:** Orchestrator → start the `agentproof` job (type reads **Agent · python**). Then cut to the **Successful** job → **Logs** tab and scroll slowly.**]**

> "This is UiPath Orchestrator. I'm putting that agent through AgentProof — as a real job, on the platform."

**[Let the logs scroll. Slow down. Let the first lines breathe.]**

> "Watch it work. It talks to the agent the way a real customer would, and it checks every response against what the agent is *supposed* to do.
> The first behaviors look fine…"

**[SHOW:** the first FAIL line appears.**]**

> "…and then they don't. Policy — missing. A simple refund — escalated to a human. One by one, it catches the agent breaking the rules, in its own words, live."

**[SHOW:** the job's **Output** — `FAILED`.**]**

> "These are real runs, on UiPath, right now — and the verdict is clear: **this agent is not safe to ship.**"

---

## SCENE 4 — The gate (the climax) (2:15–2:50)
**[SHOW:** the `/live` page at the deployment-gate moment — the hazard panels **slam shut: DEPLOYMENT BLOCKED.**]**

**[Say nothing for ~3 seconds. Let the animation be the moment.]**

> "Blocked. The broken agent never reaches a single customer."

---

## SCENE 5 — The recovery (2:50–3:50) *the resolution*
**[SHOW:** the fix — revert the one line / switch to the compliant build.**]**

> "So the developer fixes the one line that started all this."

**[SHOW:** re-validation runs — checks turn green, one after another — ending on **SAFE TO DEPLOY**. Let it land.**]**

> "And runs it again. This time, every behavior passes.
> *(beat)* Safe to deploy.
> Caught, fixed, and shipped — with confidence — in under a minute. That's the whole point: the bad version never made it out, and the good one shipped without slowing anyone down."

---

## SCENE 6 — Trust at scale (3:50–4:15)
**[SHOW:** the **dashboard**, then click a run → the **report**.**]**

> "And none of it is taken on faith. Every check is on the record — what was tested, what passed, what failed, and why — so a human makes the final call with the full picture. AgentProof does this for **every agent in your tenant**, automatically."

---

## SCENE 7 — Built with Claude Code (4:15–4:40)
**[SHOW:** a quick clip of Claude Code building part of AgentProof.**]**

> "One last thing. All of this — the agent, the engine, the platform integration — was built with **Claude Code, through UiPath for Coding Agents.** Described in plain English; running in production."

---

## SCENE 8 — Close (4:40–5:00)
**[SHOW:** the tagline and the live URL on screen.**]**

> "Enterprises are shipping AI agents faster than they can trust them. AgentProof is the gate that makes them trustworthy — catching broken behavior before it ever reaches a customer.
> **Every agent, through the gate, before it ships.**"

---

## Pacing map (something visual every ~25s)
| Time | Beat | Emotional note |
|---|---|---|
| 0:00 | The silent regression | tension opens |
| 0:30 | "Tests check code; AgentProof checks behavior" | the core idea |
| 0:55 | Real job on UiPath, logs going green→red | rising tension ⭐ |
| 2:15 | Gate slams: BLOCKED | climax |
| 2:50 | Fix → re-run → SAFE TO DEPLOY | relief / resolution |
| 3:50 | Dashboard + report | trust |
| 4:15 | Built with Claude Code | bonus |
| 4:40 | "Through the gate, before it ships" | confident close |

## Inputs cheat-sheet
| Field | Value |
|---|---|
| Suite Id | `aria_customer_support` |
| Agent Endpoint (FAIL) | `https://agentproof-opal.vercel.app/v2/chat` |
| Agent Endpoint (PASS) | `https://agentproof-opal.vercel.app/v1/chat` |

## Delivery notes
- **Build tension by slowing down**, not speeding up — pauses sell the gate and the recovery.
- During the gate animation and the "SAFE TO DEPLOY" reveal, **stop talking** and let the visuals carry it.
- Say *why*, never *what you clicked*. "It's checking the agent's behavior," not "I'm clicking validate."
- Record in segments and stitch; re-do any fumble.
