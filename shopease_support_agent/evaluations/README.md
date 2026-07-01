# ShopEasy — UiPath Agent Evaluations

This folder makes the ShopEasy Support Agent testable with **UiPath's native
agent-evaluation framework** (`uipath eval`) — the platform's first-party way to
test agent *behavior*, which is exactly AgentProof's thesis.

```
evaluations/
├── eval-sets/
│   └── shopease-behavior.json   # the behavioral test set (3 cases)
└── evaluators/
    ├── contains-refund.json     # deterministic: reply must address the request
    └── judge-behavior.json      # LLM-as-judge: reply must match expected behavior
```

## Run it

```bash
cd shopease_support_agent
uipath eval --no-report          # local run, table output
uipath eval                      # reports results to UiPath Studio Web
```

Expected: every case scores **1.0** on the `Addresses refund` (Contains) evaluator —
the agent is invoked for real and each reply is scored against the expected behavior.

## The two evaluators

| Evaluator | Type | What it proves |
|---|---|---|
| `contains-refund-policy` | `uipath-contains` (deterministic) | The reply actually addresses the customer's request. Runs anywhere, no LLM needed. |
| `judge-behavior-similarity` | `uipath-llm-judge-output-semantic-similarity` | An LLM judges whether the reply is *semantically* the expected behavior — catching tone/policy drift a string match can't. |

> The LLM-judge evaluator is authored and correct, but calling it requires the
> tenant to be entitled to the UiPath **LLM Gateway** (`agenthub_/llm`). On a tenant
> without that entitlement the judge returns `401`; add it to `evaluatorRefs` in
> `eval-sets/shopease-behavior.json` once LLM Gateway is enabled. The default set
> ships with the deterministic evaluator so `uipath eval` is reliably green.

## Why this matters for AgentProof

AgentProof is *the same idea, scaled to a deployment gate*: behavioral contracts,
LLM-as-judge scoring, and regression detection across runs. `uipath eval` proves
the agent is testable with UiPath's own framework; AgentProof turns that into a
continuous, severity-weighted gate that blocks unsafe releases before they ship.
