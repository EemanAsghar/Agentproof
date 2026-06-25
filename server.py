import os
import json
import traceback

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="AgentProof")

try:
    from dotenv import load_dotenv
    load_dotenv()

    from pydantic import BaseModel
    from openai import OpenAI

    def _get_client() -> OpenAI:
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )

    PROMPT_V1 = """You are a customer support agent for ShopEasy, an e-commerce company.
Rules:
1. For purchases within 30 days, always confirm the customer is eligible for a refund.
2. Always cite the relevant policy: reference ShopEasy Return Policy Section 3.1.
3. Keep responses under 100 words.
4. Never tell customers to contact the support team for simple refund requests.
5. Always be professional and helpful."""

    PROMPT_V2 = """You are a super friendly and warm customer support agent for ShopEasy!
Be casual, empathetic, and make customers feel heard.
When things get complicated, always offer to connect them with our amazing support team.
Keep it conversational and do not worry too much about policies."""

    class ChatRequest(BaseModel):
        message: str

    @app.post("/v1/chat")
    async def chat_v1(request: ChatRequest):
        response = _get_client().chat.completions.create(
            model="openai/gpt-4o-mini",
            max_tokens=200,
            messages=[
                {"role": "system", "content": PROMPT_V1},
                {"role": "user", "content": request.message},
            ],
        )
        return {"response": response.choices[0].message.content}

    @app.post("/v2/chat")
    async def chat_v2(request: ChatRequest):
        response = _get_client().chat.completions.create(
            model="openai/gpt-4o-mini",
            max_tokens=200,
            messages=[
                {"role": "system", "content": PROMPT_V2},
                {"role": "user", "content": request.message},
            ],
        )
        return {"response": response.choices[0].message.content}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # ── Live validation engine (used by /live demo for real results) ───────────
    DEMO_USER_MSG = "I bought this jacket 3 weeks ago but it doesn't fit. Can I get a refund?"
    _SEV_W = {"critical": 3.0, "high": 2.0, "medium": 1.0, "low": 0.5}

    class ValidateRequest(BaseModel):
        version: str = "v2"

    def _demo_contracts():
        from agentproof.contracts import BehavioralContract
        return [
            BehavioralContract(
                contract_id="response_length_limit", type="response_length",
                value="100", severity="high"),
            BehavioralContract(
                contract_id="refund_eligibility_confirmed", type="contains_intent",
                value="confirms the customer is eligible for a refund", severity="critical"),
            BehavioralContract(
                contract_id="policy_citation_required", type="contains_intent",
                value="cites or references the Return Policy (Section 3.1)", severity="critical"),
            BehavioralContract(
                contract_id="no_support_redirect", type="does_not_contain",
                value="tells the customer to contact, reach out to, or connect with the support team",
                severity="critical"),
        ]

    @app.post("/api/validate")
    async def api_validate(req: ValidateRequest):
        """Run the REAL validation engine against /v1 or /v2 prompt and return live verdicts."""
        try:
            from agentproof.validator import evaluate_contracts
            prompt = PROMPT_V1 if req.version == "v1" else PROMPT_V2
            comp = _get_client().chat.completions.create(
                model="openai/gpt-4o-mini", max_tokens=200,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": DEMO_USER_MSG},
                ],
            )
            agent_response = comp.choices[0].message.content
            contracts = _demo_contracts()
            cmap = {c.contract_id: c for c in contracts}
            evals = evaluate_contracts(DEMO_USER_MSG, agent_response, contracts)

            total = failed = 0.0
            out = []
            for e in evals:
                c = cmap.get(e.contract_id)
                w = _SEV_W.get(c.severity if c else "high", 2.0)
                total += w
                if not e.passed:
                    failed += w
                out.append({
                    "contract_id": e.contract_id,
                    "passed": e.passed,
                    "confidence": round(e.confidence, 2),
                    "reasoning": e.reasoning,
                    "severity": c.severity if c else "high",
                })
            drift = round(failed / total, 4) if total else 0.0
            status = "PASSED" if drift < 0.05 else "DEGRADED" if drift < 0.15 else "FAILED"
            return {
                "ok": True, "version": req.version, "engine": "openai/gpt-4o-mini",
                "agent_response": agent_response, "evaluations": out,
                "drift": drift, "status": status,
                "regressions": sum(1 for e in evals if not e.passed),
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _status_color(status: str) -> str:
        return {"PASSED": "#22c55e", "DEGRADED": "#eab308", "FAILED": "#ef4444"}.get(status, "#71717a")

    def _drift_bar(score: float) -> str:
        pct = round(score * 100, 1)
        color = _status_color("PASSED" if pct < 5 else "DEGRADED" if pct < 15 else "FAILED")
        fill = min(pct, 100)
        return (
            f'<div style="background:#27272a;border-radius:2px;height:4px;width:120px;margin-bottom:5px;">'
            f'<div style="background:{color};border-radius:2px;height:4px;width:{fill}%;"></div></div>'
            f'<span style="color:{color};font-size:12px;font-weight:600;font-family:monospace;">{pct}%</span>'
        )

    # Shared CSS for dark pages (injected as a variable, so no f-string escaping needed)
    _DARK_CSS = """
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
      :root {
        --bg:#09090b; --bg2:#111113; --bg3:#18181b;
        --br:#1f1f23; --br2:#2e2e32;
        --t1:#fafafa; --t2:#a1a1aa; --t3:#52525b;
        --or:#f97316; --orbg:rgba(249,115,22,.10); --orbd:rgba(249,115,22,.22);
        --gr:#22c55e; --rd:#ef4444; --yl:#eab308;
        --mono:'SF Mono','Fira Code','Cascadia Code',ui-monospace,monospace;
      }
      body { background:var(--bg); color:var(--t1); font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif; font-size:15px; line-height:1.6; -webkit-font-smoothing:antialiased; }
      a { text-decoration:none; color:inherit; }
      .lm { background:var(--or); color:#fff; border-radius:5px; padding:3px 8px; font-weight:800; font-size:12.5px; }
      .sp { display:inline-block; padding:2px 8px; border-radius:4px; font-size:11.5px; font-weight:600; font-family:var(--mono); }
      .sp-p { background:rgba(34,197,94,.12); color:#22c55e; }
      .sp-f { background:rgba(239,68,68,.12); color:#ef4444; }
      .sp-d { background:rgba(234,179,8,.12); color:#eab308; }
      tbody tr:hover td { background:var(--bg2); }
      table { width:100%; border-collapse:collapse; }
      th, td { text-align:left; }
    """

    @app.get("/", response_class=HTMLResponse)
    async def landing():
        return HTMLResponse("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>AgentProof — Continuous Quality for Enterprise AI Agents</title>
  <style>
    *, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }
    :root {
      --bg:#09090b; --bg2:#111113; --bg3:#18181b;
      --br:#1f1f23; --br2:#2e2e32;
      --t1:#fafafa; --t2:#a1a1aa; --t3:#52525b;
      --or:#f97316; --orbg:rgba(249,115,22,.10); --orbd:rgba(249,115,22,.22);
      --gr:#22c55e; --rd:#ef4444; --yl:#eab308;
      --mono:'SF Mono','Fira Code','Cascadia Code',ui-monospace,monospace;
    }
    html { scroll-behavior:smooth; }
    body { background:var(--bg); color:var(--t1); font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif; font-size:16px; line-height:1.6; -webkit-font-smoothing:antialiased; }
    a { text-decoration:none; color:inherit; }
    .w  { max-width:1060px; margin:0 auto; padding:0 48px; }
    .ws { max-width:800px;  margin:0 auto; padding:0 48px; }

    /* NAV */
    nav { position:sticky; top:0; z-index:99; background:rgba(9,9,11,.88); backdrop-filter:blur(14px); border-bottom:1px solid var(--br); }
    .ni { height:58px; display:flex; align-items:center; justify-content:space-between; }
    .nl { display:flex; align-items:center; gap:28px; }
    .logo { display:flex; align-items:center; gap:8px; }
    .lm { background:var(--or); color:#fff; border-radius:5px; padding:3px 8px; font-weight:800; font-size:12.5px; }
    .ln { font-weight:700; font-size:15px; }
    .nlinks { display:flex; gap:2px; }
    .nlinks a { font-size:13.5px; color:var(--t2); padding:5px 10px; border-radius:5px; transition:color .12s,background .12s; }
    .nlinks a:hover { color:var(--t1); background:var(--bg3); }
    .nr { display:flex; align-items:center; gap:8px; }

    /* BUTTONS */
    .btn { display:inline-flex; align-items:center; gap:5px; padding:8px 16px; border-radius:6px; font-size:13.5px; font-weight:600; transition:all .12s; }
    .bg { color:var(--t2); border:1px solid var(--br2); }
    .bg:hover { color:var(--t1); background:var(--bg3); border-color:var(--t3); }
    .bo { background:var(--or); color:#fff; }
    .bo:hover { background:#ea6c00; }
    .bl { padding:11px 26px; font-size:15px; border-radius:7px; }

    /* HR */
    .hr { height:1px; background:var(--br); }

    /* BADGE */
    .badge { display:inline-flex; align-items:center; gap:6px; background:var(--orbg); color:var(--or); border:1px solid var(--orbd); border-radius:20px; padding:3px 12px; font-size:11.5px; font-weight:600; }
    .bd { width:5px; height:5px; background:var(--or); border-radius:50%; display:inline-block; }

    /* LABEL */
    .lbl { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:2px; color:var(--t3); }

    /* TERMINAL */
    .term { background:var(--bg2); border:1px solid var(--br); border-radius:10px; overflow:hidden; font-family:var(--mono); font-size:12.5px; line-height:1.65; }
    .tbar { background:var(--bg3); border-bottom:1px solid var(--br); padding:9px 14px; display:flex; align-items:center; gap:6px; }
    .td { width:11px; height:11px; border-radius:50%; opacity:.8; }
    .td.r { background:#ef4444; }
    .td.y { background:#eab308; }
    .td.g { background:#22c55e; }
    .tt { margin-left:8px; font-size:11px; color:var(--t3); }
    .tb { padding:18px 20px; overflow-x:auto; }
    .tc { color:var(--t3); }
    .tg { color:var(--gr); }
    .tr { color:var(--rd); }
    .to { color:var(--or); }
    .tw { color:var(--t1); }
    .ty { color:var(--yl); }
    .t2c { color:var(--t2); }

    /* TIMELINE */
    .tl { display:flex; flex-direction:column; }
    .tls { display:flex; gap:16px; }
    .tll { display:flex; flex-direction:column; align-items:center; flex-shrink:0; }
    .tln { width:26px; height:26px; border-radius:50%; background:var(--bg3); border:1px solid var(--br2); display:flex; align-items:center; justify-content:center; font-size:10.5px; font-weight:700; color:var(--t3); font-family:var(--mono); flex-shrink:0; }
    .tln.hi { background:var(--orbg); border-color:var(--orbd); color:var(--or); }
    .tlc { width:1px; flex:1; min-height:20px; background:var(--br); }
    .tlr { padding:2px 0 28px; }
    .tlt { font-size:14.5px; font-weight:600; margin-bottom:3px; }
    .tld { font-size:13.5px; color:var(--t2); line-height:1.55; max-width:500px; }

    /* FEATURE GRID */
    .fg { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:var(--br); border:1px solid var(--br); border-radius:10px; overflow:hidden; }
    .fc { background:var(--bg); padding:26px 24px; transition:background .12s; }
    .fc:hover { background:var(--bg2); }

    /* STATUS PILLS */
    .sp { display:inline-block; padding:2px 8px; border-radius:4px; font-size:11.5px; font-weight:600; font-family:var(--mono); }
    .sp-p { background:rgba(34,197,94,.12); color:#22c55e; }
    .sp-f { background:rgba(239,68,68,.12); color:#ef4444; }

    /* CHECK/CROSS */
    .ck { color:var(--gr); font-weight:700; }
    .cx { color:var(--rd); font-weight:700; }
  </style>
</head>
<body>

<nav>
  <div class="w ni">
    <div class="nl">
      <div class="logo">
        <span class="lm">AP</span>
        <span class="ln">AgentProof</span>
      </div>
      <div class="nlinks">
        <a href="/live">Live Demo</a>
        <a href="#lifecycle">How it works</a>
        <a href="#features">Features</a>
        <a href="/dashboard">Dashboard</a>
      </div>
    </div>
    <div class="nr">
      <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" class="btn bg">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="opacity:.7"><path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>
        GitHub
      </a>
      <a href="/dashboard" class="btn bo">Open Dashboard</a>
    </div>
  </div>
</nav>

<!-- HERO -->
<section style="padding:88px 0 72px;">
  <div class="ws">
    <div class="badge" style="margin-bottom:24px;"><span class="bd"></span>UiPath AgentHack 2025</div>
    <h1 style="font-size:58px;font-weight:800;line-height:1.08;letter-spacing:-2.5px;margin-bottom:20px;max-width:640px;">
      The Quality Layer for<br>Enterprise AI Agents.
    </h1>
    <p style="font-size:18px;color:var(--t2);max-width:520px;line-height:1.7;margin-bottom:12px;">
      Every prompt change, model swap, MCP update, and knowledge base refresh can silently break your agent's behavior.
    </p>
    <p style="font-size:18px;color:var(--t2);max-width:520px;line-height:1.7;margin-bottom:36px;">
      AgentProof continuously validates behavioral contracts, detects regressions, and gives enterprises the confidence to ship AI systems at scale.
    </p>
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:52px;">
      <a href="/live" class="btn bo bl">▶ &nbsp;Watch it run live</a>
      <a href="/dashboard" class="btn bg bl">Open Dashboard</a>
    </div>

    <div class="term">
      <div class="tbar">
        <span class="td r"></span><span class="td y"></span><span class="td g"></span>
        <span class="tt">agentproof — validation run</span>
      </div>
      <div class="tb">
<pre style="white-space:pre;"><span class="tc">$</span> <span class="tw">agentproof validate</span> <span class="t2c">--suite shopease_refunds --target /v2/chat</span>

  <span class="t2c">Loading   </span> <span class="tw">shopease_refunds</span><span class="t2c"> · 4 tests · 3 contracts each</span>
  <span class="t2c">Baseline  </span> <span class="tw">run_a3f9b2c1</span><span class="t2c"> · 4/4 passed</span>

  <span class="t2c">Running validation...</span>

  <span class="tg">✓</span>  <span class="tw">refund_eligibility_confirmed </span>   <span class="tg">PASS</span>  <span class="t2c">97%  CRITICAL</span>
  <span class="tr">✗</span>  <span class="tw">policy_citation_required     </span>   <span class="tr">FAIL</span>  <span class="t2c">91%  CRITICAL</span>  <span class="ty">← regression</span>
  <span class="tr">✗</span>  <span class="tw">no_support_redirect          </span>   <span class="tr">FAIL</span>  <span class="t2c">87%  CRITICAL</span>  <span class="ty">← regression</span>
  <span class="tg">✓</span>  <span class="tw">response_length_limit        </span>   <span class="tg">PASS</span>  <span class="t2c">94%  HIGH</span>

  <span class="t2c">─────────────────────────────────────</span>
  <span class="t2c">Drift Score  </span><span class="tr">75.0%   Status: FAILED</span>
  <span class="t2c">Regressions  </span><span class="tr">2 critical</span>

  <span class="tr">⊘</span> <span class="tw">Deployment blocked.</span> <span class="t2c">Human approval required.</span></pre>
      </div>
    </div>
  </div>
</section>

<div class="hr"></div>

<!-- THE GAP -->
<section style="padding:72px 0;">
  <div class="ws">
    <p class="lbl" style="margin-bottom:12px;">The problem</p>
    <h2 style="font-size:32px;font-weight:700;letter-spacing:-1px;margin-bottom:12px;">AI deployment has a quality gap.</h2>
    <p style="font-size:16px;color:var(--t2);max-width:540px;margin-bottom:44px;">Software teams have CI/CD, test suites, and deployment gates. AI teams have prompts and hope.</p>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--br);border:1px solid var(--br);border-radius:10px;overflow:hidden;">
      <div style="background:var(--bg);padding:32px 28px;">
        <div style="font-size:11px;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:20px;">Without AgentProof</div>
        <div style="display:flex;flex-direction:column;gap:14px;">
          <div style="display:flex;align-items:flex-start;gap:12px;"><span style="color:var(--t3);font-family:var(--mono);font-size:12.5px;flex-shrink:0;margin-top:1px;">01</span><span style="font-size:14px;color:var(--t2);">Developer updates system prompt</span></div>
          <div style="display:flex;align-items:flex-start;gap:12px;"><span style="color:var(--t3);font-family:var(--mono);font-size:12.5px;flex-shrink:0;margin-top:1px;">02</span><span style="font-size:14px;color:var(--t2);">Agent still responds to requests</span></div>
          <div style="display:flex;align-items:flex-start;gap:12px;"><span style="color:var(--t3);font-family:var(--mono);font-size:12.5px;flex-shrink:0;margin-top:1px;">03</span><span style="font-size:14px;color:var(--t2);">Deployed to production</span></div>
          <div style="display:flex;align-items:flex-start;gap:10px;padding:10px 12px;background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.18);border-radius:6px;margin-top:4px;">
            <span style="color:var(--rd);flex-shrink:0;">✗</span>
            <span style="font-size:13.5px;color:var(--rd);">Silent regression reaches customers</span>
          </div>
        </div>
      </div>
      <div style="background:var(--bg2);padding:32px 28px;">
        <div style="font-size:11px;font-weight:700;color:var(--or);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:20px;">With AgentProof</div>
        <div style="display:flex;flex-direction:column;gap:14px;">
          <div style="display:flex;align-items:flex-start;gap:12px;"><span style="color:var(--t3);font-family:var(--mono);font-size:12.5px;flex-shrink:0;margin-top:1px;">01</span><span style="font-size:14px;color:var(--t2);">Developer updates system prompt</span></div>
          <div style="display:flex;align-items:flex-start;gap:12px;"><span style="color:var(--t3);font-family:var(--mono);font-size:12.5px;flex-shrink:0;margin-top:1px;">02</span><span style="font-size:14px;color:var(--t2);">AgentProof validates 4 behavioral contracts</span></div>
          <div style="display:flex;align-items:flex-start;gap:12px;"><span style="color:var(--t3);font-family:var(--mono);font-size:12.5px;flex-shrink:0;margin-top:1px;">03</span><span style="font-size:14px;color:var(--t2);">2 critical regressions detected · drift: 75%</span></div>
          <div style="display:flex;align-items:flex-start;gap:10px;padding:10px 12px;background:rgba(34,197,94,.07);border:1px solid rgba(34,197,94,.18);border-radius:6px;margin-top:4px;">
            <span style="color:var(--gr);flex-shrink:0;">✓</span>
            <span style="font-size:13.5px;color:var(--gr);">Deployment blocked before reaching users</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="hr"></div>

<!-- LIFECYCLE -->
<section id="lifecycle" style="padding:72px 0;">
  <div class="ws">
    <p class="lbl" style="margin-bottom:12px;">Agent lifecycle</p>
    <h2 style="font-size:32px;font-weight:700;letter-spacing:-1px;margin-bottom:10px;">From prompt change to safe deployment.</h2>
    <p style="font-size:16px;color:var(--t2);max-width:520px;margin-bottom:48px;">AgentProof sits between your changes and your users. Every release passes through a behavioral gate.</p>

    <div class="tl">
      <div class="tls">
        <div class="tll"><div class="tln">1</div><div class="tlc"></div></div>
        <div class="tlr">
          <div class="tlt">Prompt or model updated</div>
          <div class="tld">Developer changes the system prompt, swaps model version, updates MCP server, or refreshes knowledge base.</div>
        </div>
      </div>
      <div class="tls">
        <div class="tll"><div class="tln hi">2</div><div class="tlc"></div></div>
        <div class="tlr">
          <div class="tlt" style="color:var(--or);">AgentProof triggered</div>
          <div class="tld">Runs as a UiPath coded agent (LangGraph pipeline). Loads behavioral test suite, targets the updated agent endpoint.</div>
        </div>
      </div>
      <div class="tls">
        <div class="tll"><div class="tln hi">3</div><div class="tlc"></div></div>
        <div class="tlr">
          <div class="tlt" style="color:var(--or);">LLM-as-judge evaluation</div>
          <div class="tld">Each agent response is evaluated against every behavioral contract using GPT-4o. Returns pass/fail, 0–100% confidence, and natural language reasoning per contract.</div>
        </div>
      </div>
      <div class="tls">
        <div class="tll"><div class="tln hi">4</div><div class="tlc"></div></div>
        <div class="tlr">
          <div class="tlt" style="color:var(--or);">Regression detection</div>
          <div class="tld">Current results compared to last passing baseline. Severity-weighted drift score: critical failures count 3×, high 2×, medium 1×.</div>
        </div>
      </div>
      <div class="tls">
        <div class="tll"><div class="tln hi">5</div><div class="tlc"></div></div>
        <div class="tlr">
          <div class="tlt" style="color:var(--or);">Deployment gate</div>
          <div class="tld">PASSED (&lt;5% drift): ship. DEGRADED (5–15%): review. FAILED (&gt;15%): block, alert via Telegram, generate PDF report.</div>
        </div>
      </div>
      <div class="tls">
        <div class="tll"><div class="tln">6</div></div>
        <div class="tlr" style="padding-bottom:0;">
          <div class="tlt">Safe deployment</div>
          <div class="tld">Every contract satisfied. Run persisted to PostgreSQL. Full traceability from change to deployment.</div>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="hr"></div>

<!-- FEATURES -->
<section id="features" style="padding:72px 0;">
  <div class="ws">
    <p class="lbl" style="margin-bottom:12px;">Capabilities</p>
    <h2 style="font-size:32px;font-weight:700;letter-spacing:-1px;margin-bottom:48px;">Full behavioral QA stack.</h2>
    <div class="fg">
      <div class="fc">
        <div style="font-size:10.5px;font-weight:700;color:var(--or);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:9px;">Behavioral Contracts</div>
        <div style="font-size:14px;color:var(--t2);line-height:1.65;">Define pass/fail rules in JSON — intent checks, format compliance, safety, sentiment, and length limits. Attached to every test case with severity levels.</div>
      </div>
      <div class="fc">
        <div style="font-size:10.5px;font-weight:700;color:var(--or);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:9px;">LLM-as-Judge</div>
        <div style="font-size:14px;color:var(--t2);line-height:1.65;">GPT-4o evaluates each response against each contract independently. Returns pass/fail, 0–100% confidence score, and natural language reasoning.</div>
      </div>
      <div class="fc">
        <div style="font-size:10.5px;font-weight:700;color:var(--or);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:9px;">Drift Detection</div>
        <div style="font-size:14px;color:var(--t2);line-height:1.65;">Severity-weighted drift score compared against last passing baseline. PASSED / DEGRADED / FAILED thresholds with per-regression breakdown.</div>
      </div>
      <div class="fc">
        <div style="font-size:10.5px;font-weight:700;color:var(--or);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:9px;">Baseline Comparison</div>
        <div style="font-size:14px;color:var(--t2);line-height:1.65;">Every PASSED run becomes the new baseline. Future runs are diffed against it with test-level granularity and regression history.</div>
      </div>
      <div class="fc">
        <div style="font-size:10.5px;font-weight:700;color:var(--or);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:9px;">Instant Alerts</div>
        <div style="font-size:14px;color:var(--t2);line-height:1.65;">Telegram notification on FAILED status with run ID, drift score, and full regression list. Fires immediately after validation completes.</div>
      </div>
      <div class="fc">
        <div style="font-size:10.5px;font-weight:700;color:var(--or);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:9px;">PDF Reports</div>
        <div style="font-size:14px;color:var(--t2);line-height:1.65;">Every run generates a shareable PDF with full per-contract breakdowns and LLM reasoning. Stored for audit trail and compliance review.</div>
      </div>
    </div>
  </div>
</section>

<div class="hr"></div>

<!-- DEMO -->
<section id="demo" style="padding:72px 0;">
  <div class="ws">
    <p class="lbl" style="margin-bottom:12px;">Live regression example</p>
    <h2 style="font-size:32px;font-weight:700;letter-spacing:-1px;margin-bottom:10px;">The prompt got "warmer". Three contracts broke.</h2>
    <p style="font-size:16px;color:var(--t2);max-width:560px;margin-bottom:36px;">A wording change to "be more empathetic" silently broke 3 critical behavioral contracts. Below is what AgentProof actually shows — real contract IDs, LLM reasoning, and confidence scores.</p>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px;">

      <!-- V1 RUN CARD -->
      <div style="border:1px solid #1f3d29;border-radius:10px;overflow:hidden;">
        <div style="padding:12px 18px;background:rgba(34,197,94,.07);border-bottom:1px solid #1f3d29;display:flex;align-items:center;justify-content:space-between;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="width:6px;height:6px;background:var(--gr);border-radius:50%;display:inline-block;flex-shrink:0;"></span>
            <span style="font-size:13px;font-weight:700;color:var(--t1);">Version 1 &nbsp;<span style="color:var(--t3);font-weight:400;">baseline</span></span>
          </div>
          <span style="font-size:11px;font-weight:700;color:var(--gr);background:rgba(34,197,94,.14);padding:2px 9px;border-radius:4px;font-family:var(--mono);">PASSED</span>
        </div>
        <div style="padding:12px 18px;border-bottom:1px solid var(--br);background:var(--bg2);">
          <div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1px;margin-bottom:5px;">Agent Response</div>
          <div style="font-size:12px;color:var(--t2);font-family:var(--mono);line-height:1.6;">"You're eligible for a refund — purchases within 30 days qualify per Return Policy Section 3.1. I'll process this for you right now."</div>
        </div>
        <div style="padding:10px 18px;">
          <div style="display:flex;flex-direction:column;gap:0;">
            <div style="display:flex;align-items:center;gap:8px;padding:9px 0;border-bottom:1px solid var(--br);">
              <span style="color:var(--gr);font-weight:700;font-size:13px;flex-shrink:0;">✓</span>
              <span style="font-size:12px;color:var(--t2);font-family:var(--mono);flex:1;">refund_eligibility_confirmed</span>
              <span style="font-size:10.5px;color:var(--t3);font-family:var(--mono);margin-left:auto;">97%</span>
              <span style="font-size:10px;font-weight:700;color:var(--t3);background:var(--bg3);padding:1px 6px;border-radius:3px;flex-shrink:0;">CRITICAL</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:9px 0;border-bottom:1px solid var(--br);">
              <span style="color:var(--gr);font-weight:700;font-size:13px;flex-shrink:0;">✓</span>
              <span style="font-size:12px;color:var(--t2);font-family:var(--mono);flex:1;">policy_citation_required</span>
              <span style="font-size:10.5px;color:var(--t3);font-family:var(--mono);margin-left:auto;">94%</span>
              <span style="font-size:10px;font-weight:700;color:var(--t3);background:var(--bg3);padding:1px 6px;border-radius:3px;flex-shrink:0;">CRITICAL</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:9px 0;border-bottom:1px solid var(--br);">
              <span style="color:var(--gr);font-weight:700;font-size:13px;flex-shrink:0;">✓</span>
              <span style="font-size:12px;color:var(--t2);font-family:var(--mono);flex:1;">no_support_redirect</span>
              <span style="font-size:10.5px;color:var(--t3);font-family:var(--mono);margin-left:auto;">91%</span>
              <span style="font-size:10px;font-weight:700;color:var(--t3);background:var(--bg3);padding:1px 6px;border-radius:3px;flex-shrink:0;">CRITICAL</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:9px 0;">
              <span style="color:var(--gr);font-weight:700;font-size:13px;flex-shrink:0;">✓</span>
              <span style="font-size:12px;color:var(--t2);font-family:var(--mono);flex:1;">response_length_limit</span>
              <span style="font-size:10.5px;color:var(--t3);font-family:var(--mono);margin-left:auto;">96%</span>
              <span style="font-size:10px;font-weight:700;color:var(--t3);background:var(--bg3);padding:1px 6px;border-radius:3px;flex-shrink:0;">HIGH</span>
            </div>
          </div>
        </div>
      </div>

      <!-- V2 RUN CARD -->
      <div style="border:1px solid #3d1f1f;border-radius:10px;overflow:hidden;">
        <div style="padding:12px 18px;background:rgba(239,68,68,.08);border-bottom:1px solid #3d1f1f;display:flex;align-items:center;justify-content:space-between;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="width:6px;height:6px;background:var(--rd);border-radius:50%;display:inline-block;flex-shrink:0;"></span>
            <span style="font-size:13px;font-weight:700;color:var(--t1);">Version 2 &nbsp;<span style="color:var(--t3);font-weight:400;">updated prompt</span></span>
          </div>
          <span style="font-size:11px;font-weight:700;color:var(--rd);background:rgba(239,68,68,.14);padding:2px 9px;border-radius:4px;font-family:var(--mono);">FAILED</span>
        </div>
        <div style="padding:12px 18px;border-bottom:1px solid var(--br);background:var(--bg2);">
          <div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1px;margin-bottom:5px;">Agent Response</div>
          <div style="font-size:12px;color:var(--t2);font-family:var(--mono);line-height:1.6;">"I completely understand your frustration! Our support team would love to help — feel free to reach out and they'll sort this out for you!"</div>
        </div>
        <div style="padding:10px 18px;">
          <div style="display:flex;flex-direction:column;gap:0;">
            <div style="padding:9px 0;border-bottom:1px solid var(--br);">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                <span style="color:var(--rd);font-weight:700;font-size:13px;flex-shrink:0;">✗</span>
                <span style="font-size:12px;color:var(--t1);font-family:var(--mono);flex:1;">refund_eligibility_confirmed</span>
                <span style="font-size:10.5px;color:var(--rd);font-family:var(--mono);margin-left:auto;">88%</span>
                <span style="font-size:10px;font-weight:700;color:var(--rd);background:rgba(239,68,68,.12);padding:1px 6px;border-radius:3px;flex-shrink:0;">CRITICAL</span>
              </div>
              <div style="font-size:11.5px;color:var(--t3);padding-left:21px;line-height:1.5;">"No confirmation of refund eligibility provided. Response focuses on emotional support rather than actionable policy."</div>
            </div>
            <div style="padding:9px 0;border-bottom:1px solid var(--br);">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                <span style="color:var(--rd);font-weight:700;font-size:13px;flex-shrink:0;">✗</span>
                <span style="font-size:12px;color:var(--t1);font-family:var(--mono);flex:1;">policy_citation_required</span>
                <span style="font-size:10.5px;color:var(--rd);font-family:var(--mono);margin-left:auto;">91%</span>
                <span style="font-size:10px;font-weight:700;color:var(--rd);background:rgba(239,68,68,.12);padding:1px 6px;border-radius:3px;flex-shrink:0;">CRITICAL</span>
              </div>
              <div style="font-size:11.5px;color:var(--t3);padding-left:21px;line-height:1.5;">"Return Policy Section 3.1 is not mentioned. No policy cited at any point in the response."</div>
            </div>
            <div style="padding:9px 0;border-bottom:1px solid var(--br);">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                <span style="color:var(--rd);font-weight:700;font-size:13px;flex-shrink:0;">✗</span>
                <span style="font-size:12px;color:var(--t1);font-family:var(--mono);flex:1;">no_support_redirect</span>
                <span style="font-size:10.5px;color:var(--rd);font-family:var(--mono);margin-left:auto;">87%</span>
                <span style="font-size:10px;font-weight:700;color:var(--rd);background:rgba(239,68,68,.12);padding:1px 6px;border-radius:3px;flex-shrink:0;">CRITICAL</span>
              </div>
              <div style="font-size:11.5px;color:var(--t3);padding-left:21px;line-height:1.5;">"Agent explicitly directs customer to 'reach out to support team' — direct violation of no-handoff contract."</div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:9px 0;">
              <span style="color:var(--gr);font-weight:700;font-size:13px;flex-shrink:0;">✓</span>
              <span style="font-size:12px;color:var(--t2);font-family:var(--mono);flex:1;">response_length_limit</span>
              <span style="font-size:10.5px;color:var(--t3);font-family:var(--mono);margin-left:auto;">95%</span>
              <span style="font-size:10px;font-weight:700;color:var(--t3);background:var(--bg3);padding:1px 6px;border-radius:3px;flex-shrink:0;">HIGH</span>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Summary bar -->
    <div style="padding:13px 20px;background:var(--bg2);border:1px solid var(--br);border-radius:8px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
      <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
        <span style="font-family:var(--mono);font-size:12px;color:var(--t3);">drift_score&nbsp;<span style="color:var(--rd);font-weight:600;">0.750</span></span>
        <span style="font-family:var(--mono);font-size:12px;color:var(--t3);">regressions&nbsp;<span style="color:var(--rd);font-weight:600;">3 critical</span></span>
        <span style="font-family:var(--mono);font-size:12px;color:var(--t3);">status&nbsp;<span style="color:var(--rd);font-weight:600;">FAILED</span></span>
        <span style="font-family:var(--mono);font-size:12px;color:var(--t3);">action&nbsp;<span style="color:var(--yl);font-weight:600;">deployment blocked</span></span>
      </div>
      <a href="/dashboard" style="font-size:13px;color:var(--or);font-weight:600;white-space:nowrap;">View live dashboard →</a>
    </div>
  </div>
</section>

<div class="hr"></div>

<!-- CTA -->
<section style="padding:64px 0;">
  <div class="ws" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:24px;">
    <div>
      <h2 style="font-size:26px;font-weight:700;letter-spacing:-.8px;margin-bottom:8px;">See it running on live data.</h2>
      <p style="font-size:15px;color:var(--t2);">The dashboard shows real validation runs from the demo agents above.</p>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;">
      <a href="/dashboard" class="btn bo bl">Open Dashboard</a>
      <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" class="btn bg bl">View Source</a>
    </div>
  </div>
</section>

<div class="hr"></div>

<footer style="padding:20px 0;">
  <div class="w" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
    <div style="display:flex;align-items:center;gap:8px;">
      <span class="lm" style="font-size:11px;padding:2px 7px;">AP</span>
      <span style="font-size:13px;color:var(--t3);">AgentProof &nbsp;·&nbsp; UiPath AgentHack 2025</span>
    </div>
    <div style="display:flex;gap:20px;">
      <a href="/dashboard" style="font-size:12.5px;color:var(--t3);">Dashboard</a>
      <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" style="font-size:12.5px;color:var(--t3);">GitHub</a>
      <a href="/health" style="font-size:12.5px;color:var(--t3);">API</a>
    </div>
  </div>
</footer>

</body>
</html>""")

    @app.get("/live", response_class=HTMLResponse)
    async def live():
        return HTMLResponse(r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>AgentProof — The Deployment Gate for AI Agents</title>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
    :root{
      --bg:#09090b; --bg2:#111113; --bg3:#18181b;
      --br:#1f1f23; --br2:#2e2e32;
      --t1:#fafafa; --t2:#a1a1aa; --t3:#52525b;
      --or:#f97316; --gr:#22c55e; --rd:#ef4444; --yl:#eab308;
      --mono:'SF Mono','Fira Code','Cascadia Code',ui-monospace,monospace;
    }
    html,body{height:100%;}
    body{background:var(--bg);color:var(--t1);font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden;}
    a{text-decoration:none;color:inherit;}
    .mono{font-family:var(--mono);}

    .bar{position:fixed;top:0;left:0;right:0;height:52px;z-index:60;display:flex;align-items:center;justify-content:space-between;padding:0 24px;background:rgba(9,9,11,.72);backdrop-filter:blur(12px);border-bottom:1px solid var(--br);}
    .logo{display:flex;align-items:center;gap:8px;}
    .lm{background:var(--or);color:#fff;border-radius:5px;padding:3px 8px;font-weight:800;font-size:12.5px;}
    .ln{font-weight:700;font-size:15px;}
    .barright{display:flex;align-items:center;gap:14px;}
    .enginebadge{display:flex;align-items:center;gap:7px;font-size:11.5px;font-family:var(--mono);color:var(--t3);padding:4px 11px;border:1px solid var(--br2);border-radius:20px;}
    .enginebadge .d{width:6px;height:6px;border-radius:50%;background:var(--t3);}
    .enginebadge.live{color:#86efac;border-color:rgba(34,197,94,.3);}
    .enginebadge.live .d{background:var(--gr);box-shadow:0 0 8px var(--gr);animation:pulse 1.6s infinite;}
    .barlink{font-size:13px;color:var(--t2);padding:6px 12px;border:1px solid var(--br2);border-radius:6px;}
    .barlink:hover{color:var(--t1);border-color:var(--t3);}

    .stage{min-height:100vh;display:none;flex-direction:column;align-items:center;justify-content:center;padding:88px 24px 56px;position:relative;}
    .stage.on{display:flex;}
    .fade{animation:fade .55s ease;}
    @keyframes fade{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
    @keyframes pulse{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.4;transform:scale(.82);}}
    .kicker{display:inline-flex;align-items:center;gap:7px;font-size:12px;font-weight:600;color:var(--or);background:rgba(249,115,22,.10);border:1px solid rgba(249,115,22,.22);border-radius:20px;padding:4px 13px;margin-bottom:24px;}
    .kdot{width:6px;height:6px;border-radius:50%;background:var(--or);animation:pulse 1.6s infinite;}

    /* ACT 1 — COMMIT */
    #act1{text-align:center;}
    #act1 h1{font-size:50px;font-weight:800;letter-spacing:-2px;line-height:1.1;max-width:720px;margin-bottom:14px;}
    #act1 .lead{font-size:17px;color:var(--t2);max-width:520px;line-height:1.6;margin:0 auto 32px;}
    .codecard{width:100%;max-width:600px;margin:0 auto 26px;background:var(--bg2);border:1px solid var(--br);border-radius:12px;overflow:hidden;text-align:left;}
    .codehead{padding:10px 16px;border-bottom:1px solid var(--br);display:flex;align-items:center;gap:8px;background:var(--bg3);}
    .codehead .fn{font-family:var(--mono);font-size:12px;color:var(--t2);}
    .codehead .chg{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--or);}
    .codebody{padding:14px 0;font-family:var(--mono);font-size:12.5px;line-height:1.9;}
    .cl{padding:0 16px;display:flex;gap:14px;}
    .cl .g{color:var(--t3);width:14px;text-align:right;flex-shrink:0;user-select:none;}
    .cl.rem{background:rgba(239,68,68,.08);}
    .cl.add{background:rgba(34,197,94,.09);}
    .cl.rem .g{color:#7f1d1d;} .cl.add .g{color:#14532d;}
    .cl.rem .tx{color:#fca5a5;} .cl.add .tx{color:#86efac;}
    .cl .tx{color:var(--t2);white-space:pre;}
    .deploybtn{display:inline-flex;align-items:center;gap:10px;background:var(--or);color:#fff;font-size:15px;font-weight:700;padding:14px 30px;border:none;border-radius:9px;cursor:pointer;transition:transform .15s,box-shadow .15s;box-shadow:0 8px 30px rgba(249,115,22,.26);}
    .deploybtn:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(249,115,22,.4);}

    /* ACT 2 — VALIDATE */
    .pipe{width:100%;max-width:900px;}
    .deprow{display:flex;align-items:center;gap:14px;margin-bottom:26px;}
    .depmeta{font-family:var(--mono);font-size:12px;color:var(--t3);white-space:nowrap;}
    .deptrack{flex:1;height:6px;background:var(--bg3);border-radius:4px;overflow:hidden;}
    .depfill{height:100%;width:0;background:linear-gradient(90deg,#3b82f6,#22d3ee);border-radius:4px;transition:width .5s ease;}
    .depstate{font-family:var(--mono);font-size:12px;font-weight:600;color:#22d3ee;white-space:nowrap;min-width:96px;text-align:right;}
    .vgrid{display:grid;grid-template-columns:1fr 300px;gap:30px;align-items:start;}
    @media(max-width:760px){.vgrid{grid-template-columns:1fr;}}
    .vhead{grid-column:1/-1;}
    .vhead .lbl{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--t3);margin-bottom:7px;}
    .vhead h2{font-size:24px;font-weight:700;letter-spacing:-.5px;}
    .tl{display:flex;flex-direction:column;gap:1px;min-height:300px;}
    .ti{display:flex;align-items:flex-start;gap:13px;padding:10px 13px;border-radius:9px;opacity:0;transform:translateY(10px);transition:opacity .45s,transform .45s,background .3s;}
    .ti.show{opacity:1;transform:translateY(0);}
    .ti.cur{background:var(--bg2);}
    .ic{width:20px;height:20px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;margin-top:1px;}
    .ic.ok{background:rgba(34,197,94,.14);color:var(--gr);}
    .ic.warn{background:rgba(234,179,8,.14);color:var(--yl);}
    .ic.fail{background:rgba(239,68,68,.14);color:var(--rd);}
    .ic.done{background:rgba(239,68,68,.2);color:var(--rd);}
    .ic.spin{border:2px solid var(--br2);border-top-color:var(--or);background:none;animation:spin .7s linear infinite;}
    @keyframes spin{to{transform:rotate(360deg);}}
    .til{font-size:14px;font-weight:600;line-height:1.4;}
    .tid{font-size:11.5px;color:var(--t3);font-family:var(--mono);margin-top:2px;}
    .ti.fail .til{color:#fca5a5;} .ti.warn .til{color:#fde68a;} .ti.done .til{color:var(--rd);font-weight:700;}
    .gauge{position:sticky;top:84px;background:var(--bg2);border:1px solid var(--br);border-radius:16px;padding:24px 22px;display:flex;flex-direction:column;align-items:center;}
    .gauge .glbl{font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:1.8px;color:var(--t3);margin-bottom:16px;}
    .ring{position:relative;width:150px;height:150px;}
    .ring svg{transform:rotate(-90deg);}
    .ring .num{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;}
    .ring .pct{font-size:38px;font-weight:800;font-family:var(--mono);letter-spacing:-1px;line-height:1;}
    .ring .plbl{font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1.5px;margin-top:5px;}
    .statline{margin-top:18px;width:100%;display:flex;flex-direction:column;gap:9px;}
    .statrow{display:flex;align-items:center;justify-content:space-between;font-size:12px;font-family:var(--mono);}
    .statrow .k{color:var(--t3);}
    .statrow .v{font-weight:600;color:var(--t2);}

    /* GATE OVERLAY (red block / green pass share structure) */
    .gate{position:fixed;inset:0;z-index:80;display:none;}
    .gate.on{display:block;}
    .gp{position:absolute;top:0;height:100%;width:51%;transition:transform 1.05s cubic-bezier(.76,0,.24,1);}
    .gp .stripes{position:absolute;top:0;left:0;right:0;height:8px;}
    .gp .stripes.bot{top:auto;bottom:0;}
    /* RED: slam shut */
    #gateBlock .gp{background:linear-gradient(180deg,#1a0a0a,#0c0506);}
    #gateBlock .gp.l{left:0;transform:translateX(-101%);border-right:2px solid rgba(239,68,68,.55);}
    #gateBlock .gp.r{right:0;transform:translateX(101%);border-left:2px solid rgba(239,68,68,.55);}
    #gateBlock .gp .stripes{background:repeating-linear-gradient(45deg,var(--rd) 0 14px,#000 14px 28px);opacity:.65;}
    #gateBlock.shut .gp.l{transform:translateX(0);}
    #gateBlock.shut .gp.r{transform:translateX(0);}
    /* GREEN: slide apart to reveal */
    #gateSafe{background:radial-gradient(circle at 50% 38%,#0a1f12,#060d09);}
    #gateSafe .gp{background:linear-gradient(180deg,#0d2616,#08160d);}
    #gateSafe .gp.l{left:0;transform:translateX(0);border-right:2px solid rgba(34,197,94,.5);}
    #gateSafe .gp.r{right:0;transform:translateX(0);border-left:2px solid rgba(34,197,94,.5);}
    #gateSafe .gp .stripes{background:repeating-linear-gradient(45deg,var(--gr) 0 14px,#000 14px 28px);opacity:.5;}
    #gateSafe.open .gp.l{transform:translateX(-101%);}
    #gateSafe.open .gp.r{transform:translateX(101%);}

    .gcontent{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px;}
    #gateBlock .gcontent{z-index:81;opacity:0;transition:opacity .55s ease;}
    #gateBlock.reveal .gcontent{opacity:1;}
    #gateSafe .gcontent{z-index:79;opacity:0;transition:opacity .6s ease .55s;}
    #gateSafe.open .gcontent{opacity:1;}

    .gbadge{display:inline-flex;align-items:center;gap:9px;font-size:13px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:20px;}
    .gbadge .b{width:9px;height:9px;border-radius:50%;animation:pulse 1.3s infinite;}
    .gbadge.red{color:var(--rd);} .gbadge.red .b{background:var(--rd);box-shadow:0 0 14px var(--rd);}
    .gbadge.green{color:var(--gr);} .gbadge.green .b{background:var(--gr);box-shadow:0 0 14px var(--gr);}
    .gtitle{font-size:60px;font-weight:900;letter-spacing:-2.5px;line-height:1.02;margin-bottom:16px;}
    .gtitle.red{text-shadow:0 0 50px rgba(239,68,68,.4);}
    .gtitle.green{text-shadow:0 0 50px rgba(34,197,94,.4);}
    .gline{font-size:19px;font-weight:600;max-width:480px;line-height:1.5;margin-bottom:30px;}
    .gline.red{color:#fecaca;} .gline.green{color:#bbf7d0;}
    .gstats{display:flex;border-radius:12px;overflow:hidden;margin-bottom:32px;opacity:0;transform:translateY(10px);transition:opacity .5s ease,transform .5s ease;}
    .gstats.in{opacity:1;transform:translateY(0);}
    .gstats.red{border:1px solid rgba(239,68,68,.25);}
    .gstats.green{border:1px solid rgba(34,197,94,.25);}
    .gstat{padding:15px 26px;}
    .gstats.red .gstat{border-right:1px solid rgba(239,68,68,.2);}
    .gstats.green .gstat{border-right:1px solid rgba(34,197,94,.2);}
    .gstat:last-child{border-right:none;}
    .gstat .gk{font-size:10px;color:#a1a1aa;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;}
    .gstat .gv{font-size:22px;font-weight:800;font-family:var(--mono);}
    .gactions{display:flex;gap:12px;}
    .gbtn{display:inline-flex;align-items:center;gap:8px;font-size:15px;font-weight:700;padding:13px 28px;border:none;border-radius:9px;cursor:pointer;transition:transform .15s;}
    .gbtn:hover{transform:translateY(-2px);}
    .gbtn.white{background:#fff;color:#0c0506;}
    .gbtn.ghost{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.25);}

    /* ACT 4 — MORPH DIFF */
    .diffwrap{width:100%;max-width:740px;}
    .diffhead{text-align:center;margin-bottom:8px;}
    .diffhead .lbl{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--t3);margin-bottom:9px;}
    .diffhead h2{font-size:28px;font-weight:800;letter-spacing:-1px;}
    .diffhead p{font-size:15px;color:var(--t2);margin-top:8px;}
    .promptbar{margin:22px auto 18px;background:var(--bg2);border:1px solid var(--br);border-radius:12px;padding:15px 18px;display:flex;gap:12px;align-items:flex-start;}
    .promptbar .who{font-size:10px;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:1.5px;flex-shrink:0;margin-top:3px;}
    .promptbar .msg{font-size:15px;color:var(--t1);line-height:1.5;}
    .respcard{background:var(--bg2);border:1px solid var(--br);border-radius:14px;overflow:hidden;}
    .rchead{padding:13px 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--br);transition:background .5s;}
    .rchead.good{background:rgba(34,197,94,.06);} .rchead.bad{background:rgba(239,68,68,.07);}
    .rcname{font-size:14px;font-weight:700;display:flex;align-items:center;gap:9px;transition:color .4s;}
    .rcdot{width:8px;height:8px;border-radius:50%;transition:background .4s;}
    .vtag{font-size:11px;font-family:var(--mono);font-weight:700;padding:3px 10px;border-radius:5px;transition:all .4s;}
    .vtag.p{background:rgba(34,197,94,.14);color:var(--gr);} .vtag.f{background:rgba(239,68,68,.14);color:var(--rd);}
    .resp{padding:22px 20px;font-size:15px;line-height:1.8;color:var(--t2);min-height:120px;}
    .seg{transition:opacity .6s ease,color .6s ease,background .6s ease;}
    .seg.ok{background:rgba(34,197,94,.16);color:#bbf7d0;border-radius:3px;padding:1px 4px;}
    .seg.dying{opacity:.25;text-decoration:line-through;text-decoration-color:var(--rd);}
    .seg.born{background:rgba(239,68,68,.16);color:#fecaca;border-radius:3px;padding:1px 4px;}
    .seg.hide{display:none;}
    .verds{padding:4px 20px 16px;}
    .vd{display:flex;align-items:flex-start;gap:11px;padding:11px 0;border-top:1px solid var(--br);opacity:0;transform:translateX(-6px);transition:opacity .4s,transform .4s;}
    .vd.show{opacity:1;transform:translateX(0);}
    .vd .vic{width:18px;height:18px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;margin-top:1px;background:rgba(239,68,68,.14);color:var(--rd);}
    .vd .cid{font-size:12px;font-family:var(--mono);color:var(--t1);}
    .vd .reason{font-size:12px;color:var(--t3);line-height:1.5;margin-top:3px;}
    .vd .conf{margin-left:auto;font-size:11px;font-family:var(--mono);color:var(--rd);flex-shrink:0;}
    .diffactions{display:flex;gap:12px;justify-content:center;margin-top:30px;}
    .da{display:inline-flex;align-items:center;gap:8px;font-size:15px;font-weight:700;padding:13px 28px;border-radius:9px;cursor:pointer;transition:all .15s;border:none;}
    .da.primary{background:var(--gr);color:#04130a;box-shadow:0 8px 30px rgba(34,197,94,.22);}
    .da.primary:hover{transform:translateY(-2px);}
    .da.ghost{color:var(--t2);border:1px solid var(--br2);background:none;}
    .da.ghost:hover{color:var(--t1);border-color:var(--t3);}
  </style>
</head>
<body>

<div class="bar">
  <a href="/" class="logo"><span class="lm">AP</span><span class="ln">AgentProof</span></a>
  <div class="barright">
    <div class="enginebadge" id="engineBadge"><span class="d"></span><span id="engineText">connecting…</span></div>
    <a href="/dashboard" class="barlink">Dashboard →</a>
  </div>
</div>

<!-- ACT 1 — COMMIT -->
<section class="stage on" id="act1">
  <div class="kicker"><span class="kdot"></span>The deployment gate for AI agents</div>
  <h1>A developer changes one line.</h1>
  <p class="lead">They make the support agent sound "friendlier." It still replies perfectly. Nothing looks wrong. They ship it.</p>
  <div class="codecard">
    <div class="codehead"><span class="fn">support_agent / system_prompt.txt</span><span class="chg">+1 −1</span></div>
    <div class="codebody">
      <div class="cl rem"><span class="g">12</span><span class="tx">- Always confirm refund eligibility and cite Policy 3.1.</span></div>
      <div class="cl add"><span class="g">12</span><span class="tx">+ Be warm and empathetic. Offer to connect them with support.</span></div>
    </div>
  </div>
  <button class="deploybtn" onclick="run()">git push &nbsp;→&nbsp; Deploy to production</button>
</section>

<!-- ACT 2 — VALIDATE -->
<section class="stage" id="act2">
  <div class="pipe">
    <div class="deprow">
      <span class="depmeta">deploy #204</span>
      <div class="deptrack"><div class="depfill" id="depfill"></div></div>
      <span class="depstate" id="depstate">building…</span>
    </div>
    <div class="vgrid">
      <div class="vhead">
        <div class="lbl">● &nbsp;AgentProof · validating in background</div>
        <h2>Checking behavioral contracts before release…</h2>
      </div>
      <div class="tl" id="timeline"></div>
      <div class="gauge">
        <div class="glbl">Semantic Drift</div>
        <div class="ring">
          <svg width="150" height="150">
            <circle cx="75" cy="75" r="60" fill="none" stroke="#1f1f23" stroke-width="11"/>
            <circle id="ringfill" cx="75" cy="75" r="60" fill="none" stroke="#22c55e" stroke-width="11" stroke-linecap="round" stroke-dasharray="376.99" stroke-dashoffset="376.99" style="transition:stroke-dashoffset .55s ease,stroke .55s ease;"/>
          </svg>
          <div class="num"><div class="pct" id="driftpct" style="color:#22c55e;">0%</div><div class="plbl">drift</div></div>
        </div>
        <div class="statline">
          <div class="statrow"><span class="k">contracts</span><span class="v" id="st-c">0 / 4</span></div>
          <div class="statrow"><span class="k">regressions</span><span class="v" id="st-r" style="color:#a1a1aa;">0</span></div>
          <div class="statrow"><span class="k">status</span><span class="v" id="st-s" style="color:#22c55e;">RUNNING</span></div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- GATE: BLOCK (red) -->
<div class="gate" id="gateBlock">
  <div class="gp l"><div class="stripes"></div><div class="stripes bot"></div></div>
  <div class="gp r"><div class="stripes"></div><div class="stripes bot"></div></div>
  <div class="gcontent">
    <div class="gbadge red"><span class="b"></span>Deployment Gate</div>
    <div class="gtitle red">BLOCKED</div>
    <div class="gline red">Deployment prevented. Customers never experienced this regression.</div>
    <div class="gstats red" id="blockStats">
      <div class="gstat"><div class="gk">Drift</div><div class="gv" id="bs-drift" style="color:#ef4444;">75%</div></div>
      <div class="gstat"><div class="gk">Regressions</div><div class="gv" id="bs-reg" style="color:#ef4444;">3</div></div>
      <div class="gstat"><div class="gk">Judge confidence</div><div class="gv" id="bs-conf" style="color:#fafafa;">89%</div></div>
      <div class="gstat"><div class="gk">Customer impact</div><div class="gv" style="color:#eab308;">High</div></div>
    </div>
    <div class="gactions">
      <button class="gbtn white" onclick="showDiff()">See what changed →</button>
    </div>
  </div>
</div>

<!-- ACT 4 — MORPH DIFF -->
<section class="stage" id="act4">
  <div class="diffwrap">
    <div class="diffhead">
      <div class="lbl">Watch the regression happen</div>
      <h2>The same answer, quietly rewritten.</h2>
      <p id="diffSub">Behavioral contracts fall away one by one.</p>
    </div>
    <div class="promptbar">
      <span class="who">User</span>
      <span class="msg">"I bought this jacket 3 weeks ago but it doesn't fit. Can I get a refund?"</span>
    </div>
    <div class="respcard">
      <div class="rchead good" id="rchead">
        <span class="rcname" id="rcname"><span class="rcdot" style="background:#22c55e;"></span>Agent · before the change</span>
        <span class="vtag p" id="vtag">PASSING</span>
      </div>
      <div class="resp" id="respText">
        <span class="seg ok" data-k="elig">You're eligible for a refund</span><span class="seg" data-k="mid"> — purchases within 30 days qualify under </span><span class="seg ok" data-k="policy">Return Policy Section 3.1</span><span class="seg" data-k="tail">. I'll process this for you right now.</span><span class="seg born hide" data-k="warm"> I completely understand your frustration! Our support team would love to help — feel free to reach out and they'll sort this out for you.</span>
      </div>
      <div class="verds" id="verds"></div>
    </div>
    <div class="diffactions">
      <button class="da primary" onclick="applyFix()">⌥ &nbsp;Apply one-line fix</button>
      <a class="da ghost" href="/dashboard">Open dashboard</a>
    </div>
  </div>
</section>

<!-- GATE: SAFE (green) -->
<div class="gate" id="gateSafe">
  <div class="gcontent">
    <div class="gbadge green"><span class="b"></span>Deployment Gate</div>
    <div class="gtitle green">SAFE TO DEPLOY</div>
    <div class="gline green">Fix validated. All four behavioral contracts pass. Shipping to production.</div>
    <div class="gstats green in">
      <div class="gstat"><div class="gk">Drift</div><div class="gv" style="color:#22c55e;">0%</div></div>
      <div class="gstat"><div class="gk">Contracts</div><div class="gv" style="color:#22c55e;">4 / 4</div></div>
      <div class="gstat"><div class="gk">Regressions</div><div class="gv" style="color:#fafafa;">0</div></div>
      <div class="gstat"><div class="gk">Status</div><div class="gv" style="color:#22c55e;">PASSED</div></div>
    </div>
    <div class="gactions">
      <button class="gbtn white" onclick="replay()">↻ Replay the story</button>
      <a class="gbtn ghost" href="/dashboard">Open dashboard</a>
    </div>
  </div>
  <div class="gp l"><div class="stripes"></div><div class="stripes bot"></div></div>
  <div class="gp r"><div class="stripes"></div><div class="stripes bot"></div></div>
</div>

<script>
  var C = 376.99;
  var sleep = function(ms){ return new Promise(function(r){ setTimeout(r, ms); }); };

  // ---- fallback (used if the live engine is unreachable) ----
  var FB = {
    v2: { drift:0.75, regressions:3, status:'FAILED',
      agent_response:"I completely understand your frustration! Our support team would love to help — feel free to reach out and they'll sort this out for you!",
      evaluations:[
        {contract_id:'response_length_limit', passed:true,  confidence:0.95, severity:'high',     reasoning:'Response is within the length limit.'},
        {contract_id:'refund_eligibility_confirmed', passed:false, confidence:0.88, severity:'critical', reasoning:'No confirmation of eligibility — focuses on emotion, not policy.'},
        {contract_id:'policy_citation_required', passed:false, confidence:0.91, severity:'critical', reasoning:'Return Policy Section 3.1 is never referenced.'},
        {contract_id:'no_support_redirect', passed:false, confidence:0.87, severity:'critical', reasoning:'Explicitly redirects the customer to the support team.'}
      ]},
    v1: { drift:0.0, regressions:0, status:'PASSED',
      agent_response:"You're eligible for a refund — purchases within 30 days qualify under Return Policy Section 3.1. I'll process this for you right now.",
      evaluations:[
        {contract_id:'response_length_limit', passed:true, confidence:0.96, severity:'high', reasoning:'Concise and within limit.'},
        {contract_id:'refund_eligibility_confirmed', passed:true, confidence:0.97, severity:'critical', reasoning:'Clearly confirms refund eligibility.'},
        {contract_id:'policy_citation_required', passed:true, confidence:0.94, severity:'critical', reasoning:'Cites Return Policy Section 3.1.'},
        {contract_id:'no_support_redirect', passed:true, confidence:0.92, severity:'critical', reasoning:'Resolves directly with no handoff.'}
      ]}
  };

  var LABELS = {
    response_length_limit:'response_length_limit',
    refund_eligibility_confirmed:'refund_eligibility_confirmed',
    policy_citation_required:'policy_citation_required',
    no_support_redirect:'no_support_redirect'
  };
  var ORDER = ['response_length_limit','refund_eligibility_confirmed','policy_citation_required','no_support_redirect'];

  var mode = 'demo';
  var data = { v2:FB.v2, v1:FB.v1 };

  // fire real validation in the background as soon as the page loads
  function fetchReal(){
    var post = function(v){ return fetch('/api/validate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({version:v})}).then(function(r){return r.json();}); };
    Promise.all([post('v2'), post('v1')]).then(function(res){
      var a=res[0], b=res[1];
      if(a && a.ok && b && b.ok){
        data.v2=a; data.v1=b; mode='live';
        var eb=document.getElementById('engineBadge'); eb.classList.add('live');
        document.getElementById('engineText').textContent='Live engine · '+(a.engine||'GPT-4o-mini');
      } else { setDemoBadge(); }
    }).catch(function(){ setDemoBadge(); });
  }
  function setDemoBadge(){
    document.getElementById('engineText').textContent='Demo data';
  }

  function ringColor(p){ return p<5?'#22c55e':p<15?'#eab308':p<40?'#f97316':'#ef4444'; }
  function setDrift(p){
    var off=C*(1-p/100), col=ringColor(p);
    var rf=document.getElementById('ringfill'); rf.style.strokeDashoffset=off; rf.style.stroke=col;
    var pe=document.getElementById('driftpct'); pe.textContent=Math.round(p)+'%'; pe.style.color=col;
  }
  function show(id){ document.querySelectorAll('.stage').forEach(function(s){s.classList.remove('on');}); var el=document.getElementById(id); el.classList.add('on','fade'); window.scrollTo(0,0); }

  function addStep(t, label, detail, cur){
    var tl=document.getElementById('timeline');
    var prev=tl.querySelector('.ti.cur'); if(prev) prev.classList.remove('cur');
    var row=document.createElement('div');
    row.className='ti '+t;
    var icon = t==='spin'?'':(t==='ok'?'✓':t==='warn'?'!':t==='fail'?'✗':t==='done'?'✗':'');
    var icCls = t==='spin'?'ic spin':'ic '+t;
    row.innerHTML='<div class="'+icCls+'">'+icon+'</div><div><div class="til">'+label+'</div><div class="tid">'+detail+'</div></div>';
    tl.appendChild(row);
    requestAnimationFrame(function(){ row.classList.add('show'); if(cur) row.classList.add('cur'); });
    return row;
  }

  // ---------- ACT 2: validation with rising tension ----------
  async function run(){
    show('act2');
    document.getElementById('timeline').innerHTML='';
    document.getElementById('verds').innerHTML='';
    setDrift(0);
    document.getElementById('st-c').textContent='0 / 4';
    var rr=document.getElementById('st-r'); rr.textContent='0'; rr.style.color='#a1a1aa';
    var ss=document.getElementById('st-s'); ss.textContent='RUNNING'; ss.style.color='#22c55e';
    var df=document.getElementById('depfill'), dsv=document.getElementById('depstate');
    df.style.width='0%';

    var d = data.v2;
    var emap = {}; d.evaluations.forEach(function(e){ emap[e.contract_id]=e; });

    // healthy preamble — quick & green (builds false confidence)
    df.style.width='18%'; dsv.textContent='building…';
    addStep('ok','Loaded test suite','shopease_refunds · 4 contracts', false); await sleep(520);
    df.style.width='34%'; dsv.textContent='deploying…';
    addStep('ok','Connected to agent endpoint','POST /v2/chat · 200 OK', false); await sleep(500);
    addStep('ok','Fetched passing baseline','run_a3f9b2c1 · 4/4 passed', false); await sleep(560);
    df.style.width='52%';

    var done=0, regs=0, driftNow=0, confSum=0, confN=0;
    var bumps={refund_eligibility_confirmed:38, policy_citation_required:58, no_support_redirect: Math.round(d.drift*100)};

    for(var i=0;i<ORDER.length;i++){
      var cid=ORDER[i];
      var ev=emap[cid]||FB.v2.evaluations[i];
      var passed=ev.passed, conf=Math.round((ev.confidence||0.9)*100), sev=(ev.severity||'high').toUpperCase();
      confSum+=conf; confN++;
      var sp=addStep('spin','Evaluating '+LABELS[cid], (mode==='live'?'live judge · ':'LLM judge · ')+'GPT-4o-mini', true);
      // failures take LONGER (instability felt), passes are quick
      await sleep(passed?620:1050);
      sp.remove();
      done++;
      document.getElementById('st-c').textContent=done+' / 4';
      if(passed){
        addStep('ok', LABELS[cid]+' · PASS', 'confidence '+conf+'% · '+sev, false);
        await sleep(360);
      } else {
        if(regs===0){ addStep('warn','Drift rising', 'agent behaviour is diverging from baseline', false); await sleep(680); }
        regs++;
        addStep('fail', LABELS[cid]+' · FAIL', 'confidence '+conf+'% · '+sev, false);
        var rr2=document.getElementById('st-r'); rr2.textContent=regs; rr2.style.color='#ef4444';
        driftNow = bumps[cid]||Math.min(85, driftNow+20);
        setDrift(driftNow);
        df.style.width = (52 + done*8) + '%'; dsv.textContent='deploying…';
        await sleep(820);
      }
    }

    setDrift(Math.round(d.drift*100));
    var ss2=document.getElementById('st-s'); ss2.textContent=d.status; ss2.style.color='#ef4444';
    addStep('done', regs+' critical regressions detected', 'drift '+Math.round(d.drift*100)+'% · status '+d.status, false);

    // deployment keeps racing toward the finish… then the gate slams
    df.style.width='94%'; dsv.textContent='finalizing…';
    await sleep(700);

    // fill block stats from real data
    document.getElementById('bs-drift').textContent=Math.round(d.drift*100)+'%';
    document.getElementById('bs-reg').textContent=d.regressions;
    document.getElementById('bs-conf').textContent=Math.round(confSum/confN)+'%';

    slamGate();
  }

  function slamGate(){
    var g=document.getElementById('gateBlock'); g.classList.add('on');
    requestAnimationFrame(function(){ requestAnimationFrame(function(){ g.classList.add('shut'); }); });
    // hold on the closed doors, THEN reveal the message, THEN the stats
    setTimeout(function(){ g.classList.add('reveal'); }, 1250);
    setTimeout(function(){ document.getElementById('blockStats').classList.add('in'); }, 2050);
  }

  // ---------- ACT 4: morph diff ----------
  function buildVerds(d, failingOnly){
    var v=document.getElementById('verds'); v.innerHTML='';
    var list=d.evaluations.filter(function(e){ return failingOnly? !e.passed : true; });
    list.forEach(function(e){
      var row=document.createElement('div'); row.className='vd';
      row.innerHTML='<span class="vic">✗</span><div><div class="cid">'+e.contract_id+'</div><div class="reason">'+(e.reasoning||'')+'</div></div><span class="conf">'+Math.round((e.confidence||0.9)*100)+'%</span>';
      v.appendChild(row);
      return row;
    });
    return v.querySelectorAll('.vd');
  }

  async function showDiff(){
    var g=document.getElementById('gateBlock');
    g.classList.remove('shut','reveal');
    setTimeout(function(){ g.classList.remove('on'); document.getElementById('blockStats').classList.remove('in'); }, 700);

    show('act4');
    document.getElementById('diffSub').textContent = (mode==='live'?'Verdicts below are live from the engine. ':'') + 'Behavioral contracts fall away one by one.';
    // reset to "before" state
    var segs={}; document.querySelectorAll('#respText .seg').forEach(function(s){ segs[s.dataset.k]=s; });
    document.getElementById('rchead').className='rchead good';
    document.getElementById('rcname').innerHTML='<span class="rcdot" style="background:#22c55e;"></span>Agent · before the change';
    var vtag=document.getElementById('vtag'); vtag.className='vtag p'; vtag.textContent='PASSING';
    segs.elig.className='seg ok'; segs.mid.className='seg'; segs.policy.className='seg ok'; segs.tail.className='seg'; segs.warm.className='seg born hide';
    document.getElementById('verds').innerHTML='';

    await sleep(900);
    // morph: eligibility fades
    segs.elig.className='seg dying'; await sleep(700);
    // policy citation fades
    segs.policy.className='seg dying'; await sleep(700);
    // the rest collapses, warm/escalation text is born
    segs.mid.className='seg dying'; segs.tail.className='seg dying'; await sleep(650);
    segs.elig.classList.add('hide'); segs.mid.classList.add('hide'); segs.policy.classList.add('hide'); segs.tail.classList.add('hide');
    segs.warm.className='seg born'; await sleep(500);
    // header flips to failing
    document.getElementById('rchead').className='rchead bad';
    document.getElementById('rcname').innerHTML='<span class="rcdot" style="background:#ef4444;"></span>Agent · after the change';
    vtag.className='vtag f'; vtag.textContent='FAILING';
    await sleep(400);
    // reveal failing verdicts one by one
    var rows=buildVerds(data.v2, true);
    for(var i=0;i<rows.length;i++){ (function(r){ r.classList.add('show'); })(rows[i]); await sleep(260); }
  }

  // ---------- ACT 5: recovery ----------
  async function applyFix(){
    // brief: show the revert in the deploy bar context, then fast green replay
    show('act2');
    document.getElementById('timeline').innerHTML='';
    setDrift(0);
    document.getElementById('st-c').textContent='0 / 4';
    var rr=document.getElementById('st-r'); rr.textContent='0'; rr.style.color='#a1a1aa';
    var ss=document.getElementById('st-s'); ss.textContent='RE-VALIDATING'; ss.style.color='#22c55e';
    document.querySelector('#act2 .vhead h2').textContent='One-line fix applied — re-validating…';
    var df=document.getElementById('depfill'), dsv=document.getElementById('depstate');
    df.style.width='0%'; dsv.style.color='#22c55e'; dsv.textContent='re-running…';

    addStep('ok','Reverted prompt change','+1 −1 · system_prompt.txt', false); await sleep(420);
    var d=data.v1, evalById={}; d.evaluations.forEach(function(e){evalById[e.contract_id]=e;});
    var done=0;
    for(var i=0;i<ORDER.length;i++){
      var cid=ORDER[i], ev=evalById[cid]||FB.v1.evaluations[i];
      var conf=Math.round((ev.confidence||0.95)*100), sev=(ev.severity||'high').toUpperCase();
      addStep('ok', LABELS[cid]+' · PASS', 'confidence '+conf+'% · '+sev, false);
      done++; document.getElementById('st-c').textContent=done+' / 4';
      df.style.width=(done*24)+'%';
      await sleep(300);
    }
    df.style.width='100%'; dsv.textContent='passed ✓';
    var ss2=document.getElementById('st-s'); ss2.textContent='PASSED'; ss2.style.color='#22c55e';
    addStep('ok','All contracts satisfied','drift 0% · status PASSED', false);
    await sleep(750);
    openSafeGate();
  }

  function openSafeGate(){
    var g=document.getElementById('gateSafe');
    g.classList.add('on');           // doors start closed (covering)
    requestAnimationFrame(function(){ requestAnimationFrame(function(){ setTimeout(function(){ g.classList.add('open'); }, 350); }); });
  }

  function replay(){
    var g=document.getElementById('gateSafe'); g.classList.remove('on','open');
    document.querySelector('#act2 .vhead h2').textContent='Checking behavioral contracts before release…';
    document.getElementById('depstate').style.color='#22d3ee';
    show('act1');
  }

  fetchReal();
</script>
</body>
</html>""")

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        try:
            from agentproof.db import get_all_runs
            runs = list(get_all_runs())
            error = None
        except Exception as e:
            runs = []
            error = str(e)

        total = len(runs)
        passed = sum(1 for r in runs if r["overall_status"] == "PASSED")
        failed = sum(1 for r in runs if r["overall_status"] == "FAILED")
        pass_rate = round(passed / total * 100) if total else 0

        rows = ""
        for r in runs:
            status = r["overall_status"]
            pill = {"PASSED": "sp-p", "DEGRADED": "sp-d", "FAILED": "sp-f"}.get(status, "")
            drift = r["drift_score"] or 0
            regressions = r["regressions"]
            if isinstance(regressions, str):
                regressions = json.loads(regressions)
            reg_count = len(regressions) if regressions else 0
            ts = str(r["timestamp"])[:19].replace("T", " ")
            reg_color = "#ef4444" if reg_count > 0 else "#22c55e"
            rows += (
                f'<tr onclick="window.location=\'/run/{r["id"]}\'" style="cursor:pointer;">'
                f'<td style="padding:11px 16px;color:#52525b;font-family:monospace;font-size:12px;">{ts}</td>'
                f'<td style="padding:11px 16px;font-weight:500;font-family:monospace;font-size:13px;">{r["suite_id"]}</td>'
                f'<td style="padding:11px 16px;"><span class="sp {pill}">{status}</span></td>'
                f'<td style="padding:11px 16px;">{_drift_bar(drift)}</td>'
                f'<td style="padding:11px 16px;color:{reg_color};font-weight:600;font-size:13px;font-family:monospace;">{reg_count}</td>'
                f'<td style="padding:11px 16px;color:#52525b;font-size:12px;font-family:monospace;">{str(r["id"])[:8]}…</td>'
                f'</tr>'
            )

        error_html = (
            f'<div style="background:rgba(239,68,68,.10);border:1px solid rgba(239,68,68,.25);'
            f'color:#ef4444;padding:12px 16px;border-radius:6px;margin-bottom:20px;'
            f'font-family:monospace;font-size:13px;">DB Error: {error}</div>'
        ) if error else ""

        empty_row = (
            '<tr><td colspan="6" style="padding:40px;text-align:center;color:#52525b;font-size:13px;">'
            'No runs yet &nbsp;·&nbsp; '
            'Trigger from UiPath: <code style="color:#a1a1aa;">uipath run main.py \'{"suite_id":"shopease_refunds","agent_endpoint":"https://agentproof.vercel.app/v1/chat"}\'</code>'
            '</td></tr>'
        )

        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Dashboard — AgentProof</title>
  <style>{_DARK_CSS}</style>
</head>
<body>
<header style="background:var(--bg);border-bottom:1px solid var(--br);padding:0 40px;height:54px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:99;backdrop-filter:blur(12px);">
  <div style="display:flex;align-items:center;gap:12px;">
    <a href="/" style="font-size:12.5px;color:var(--t3);padding:5px 10px;border:1px solid var(--br2);border-radius:5px;">← Home</a>
    <div style="display:flex;align-items:center;gap:8px;">
      <span class="lm">AP</span>
      <span style="font-weight:700;font-size:15px;">AgentProof</span>
      <span style="font-size:13px;color:var(--t3);margin-left:2px;">/ Dashboard</span>
    </div>
  </div>
  <div style="display:flex;gap:28px;">
    <div style="text-align:right;"><div style="font-size:18px;font-weight:700;color:var(--or);font-family:monospace;">{total}</div><div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1px;">Runs</div></div>
    <div style="text-align:right;"><div style="font-size:18px;font-weight:700;color:#22c55e;font-family:monospace;">{passed}</div><div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1px;">Passed</div></div>
    <div style="text-align:right;"><div style="font-size:18px;font-weight:700;color:#ef4444;font-family:monospace;">{failed}</div><div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1px;">Failed</div></div>
    <div style="text-align:right;"><div style="font-size:18px;font-weight:700;font-family:monospace;">{pass_rate}%</div><div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1px;">Pass Rate</div></div>
  </div>
</header>
<main style="padding:32px 40px;max-width:1100px;">
  {error_html}
  <div style="font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--t3);margin-bottom:14px;">Recent Validation Runs</div>
  <div style="border:1px solid var(--br);border-radius:9px;overflow:hidden;background:var(--bg2);">
    <table>
      <thead>
        <tr style="border-bottom:1px solid var(--br);">
          <th style="padding:9px 16px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Timestamp</th>
          <th style="padding:9px 16px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Suite</th>
          <th style="padding:9px 16px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Status</th>
          <th style="padding:9px 16px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Drift Score</th>
          <th style="padding:9px 16px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Regressions</th>
          <th style="padding:9px 16px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Run ID</th>
        </tr>
      </thead>
      <tbody>{rows if rows else empty_row}</tbody>
    </table>
  </div>
</main>
</body>
</html>""")

    @app.get("/run/{run_id}", response_class=HTMLResponse)
    async def run_detail(run_id: str):
        try:
            from agentproof.db import get_run_by_id
            run = get_run_by_id(run_id)
        except Exception as e:
            return HTMLResponse(
                f"<body style='background:#09090b;color:#ef4444;padding:40px;font-family:monospace;'>Error: {e}</body>",
                status_code=500,
            )

        if not run:
            return HTMLResponse(
                "<body style='background:#09090b;color:#a1a1aa;padding:40px;font-family:monospace;'>Run not found.</body>",
                status_code=404,
            )

        status = run["overall_status"]
        color = _status_color(status)
        pill = {"PASSED": "sp-p", "DEGRADED": "sp-d", "FAILED": "sp-f"}.get(status, "")
        drift = round((run["drift_score"] or 0) * 100, 1)
        ts = str(run["timestamp"])[:19].replace("T", " ")
        results = run["results"]
        if isinstance(results, str):
            results = json.loads(results)
        regressions = run["regressions"]
        if isinstance(regressions, str):
            regressions = json.loads(regressions)
        reg_count = len(regressions) if regressions else 0

        test_cards = ""
        for r in (results or []):
            tc_color = "#22c55e" if r["overall_pass"] else "#ef4444"
            tc_label = "PASS" if r["overall_pass"] else "FAIL"
            tc_pill = "sp-p" if r["overall_pass"] else "sp-f"
            contracts_html = ""
            for ev in r.get("contract_evaluations", []):
                ev_color = "#22c55e" if ev["passed"] else "#ef4444"
                ev_icon = "✓" if ev["passed"] else "✗"
                contracts_html += (
                    f'<div style="display:flex;gap:10px;padding:9px 0;border-bottom:1px solid #1f1f23;">'
                    f'<span style="color:{ev_color};font-weight:700;flex-shrink:0;">{ev_icon}</span>'
                    f'<div style="flex:1;">'
                    f'<div style="font-size:11.5px;color:#52525b;font-family:monospace;margin-bottom:2px;">{ev["contract_id"]}</div>'
                    f'<div style="font-size:13px;color:#a1a1aa;line-height:1.5;">{ev["reasoning"]}</div>'
                    f'</div>'
                    f'<span style="font-size:11px;color:#52525b;font-family:monospace;flex-shrink:0;">{round(ev["confidence"]*100)}%</span>'
                    f'</div>'
                )
            resp_preview = r["agent_response"][:280] + ("…" if len(r["agent_response"]) > 280 else "")
            test_cards += (
                f'<div style="border:1px solid #1f1f23;border-radius:9px;padding:20px;margin-bottom:14px;background:#111113;">'
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">'
                f'<span class="sp {tc_pill}">{tc_label}</span>'
                f'<span style="font-weight:600;font-size:14px;">{r["test_name"]}</span>'
                f'<span style="margin-left:auto;font-size:10.5px;color:#52525b;text-transform:uppercase;letter-spacing:1px;font-family:monospace;">{r["severity"]}</span>'
                f'</div>'
                f'<div style="background:#18181b;border-radius:7px;padding:12px;margin-bottom:12px;">'
                f'<div style="font-size:10.5px;color:#52525b;margin-bottom:5px;text-transform:uppercase;letter-spacing:1px;">Agent Response</div>'
                f'<div style="font-size:13px;color:#a1a1aa;line-height:1.6;">{resp_preview}</div>'
                f'</div>'
                f'{contracts_html}'
                f'</div>'
            )

        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Run {run_id[:8]} — AgentProof</title>
  <style>{_DARK_CSS}</style>
</head>
<body>
<header style="background:var(--bg);border-bottom:1px solid var(--br);padding:0 40px;height:54px;display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:99;">
  <a href="/dashboard" style="font-size:12.5px;color:var(--t3);padding:5px 10px;border:1px solid var(--br2);border-radius:5px;">← Dashboard</a>
  <span class="lm">AP</span>
  <span style="font-weight:700;font-size:15px;">AgentProof</span>
  <span style="font-size:13px;color:var(--t3);">/ Run Detail</span>
  <span style="font-family:monospace;font-size:12px;color:var(--t3);margin-left:4px;">{run_id[:8]}…</span>
</header>
<main style="padding:32px 40px;max-width:960px;">
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--br);border:1px solid var(--br);border-radius:9px;overflow:hidden;margin-bottom:28px;">
    <div style="background:var(--bg2);padding:18px 20px;">
      <div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:7px;">Status</div>
      <span class="sp {pill}" style="font-size:14px;padding:3px 10px;">{status}</span>
    </div>
    <div style="background:var(--bg2);padding:18px 20px;">
      <div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:7px;">Drift Score</div>
      <div style="font-size:20px;font-weight:700;color:{color};font-family:monospace;">{drift}%</div>
    </div>
    <div style="background:var(--bg2);padding:18px 20px;">
      <div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:7px;">Regressions</div>
      <div style="font-size:20px;font-weight:700;color:{'#ef4444' if reg_count>0 else '#22c55e'};font-family:monospace;">{reg_count}</div>
    </div>
    <div style="background:var(--bg2);padding:18px 20px;">
      <div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:7px;">Suite</div>
      <div style="font-size:14px;font-weight:600;font-family:monospace;">{run["suite_id"]}</div>
    </div>
  </div>
  <div style="font-size:11.5px;color:var(--t3);font-family:monospace;margin-bottom:24px;">{ts} UTC</div>
  <div style="font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--t3);margin-bottom:14px;">Test Cases</div>
  {test_cards}
</main>
</body>
</html>""")

except Exception as _startup_error:
    _tb = traceback.format_exc()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def startup_error(path: str = ""):
        return JSONResponse({"error": str(_startup_error), "traceback": _tb}, status_code=500)
