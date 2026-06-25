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
        <a href="#lifecycle">How it works</a>
        <a href="#features">Features</a>
        <a href="#demo">Demo</a>
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
      <a href="/dashboard" class="btn bo bl">Open Dashboard</a>
      <a href="#lifecycle" class="btn bg bl">See the Lifecycle</a>
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
