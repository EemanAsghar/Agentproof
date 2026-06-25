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
        return {"PASSED": "#10B981", "DEGRADED": "#F59E0B", "FAILED": "#F43F5E"}.get(status, "#94A3B8")

    def _drift_bar(score: float) -> str:
        pct = round(score * 100, 1)
        color = _status_color("PASSED" if pct < 5 else "DEGRADED" if pct < 15 else "FAILED")
        return f"""<div style="background:#1E293B;border-radius:4px;height:8px;width:100%;margin-bottom:4px;"><div style="background:{color};border-radius:4px;height:8px;width:{min(pct,100)}%;"></div></div><span style="color:{color};font-size:12px;font-weight:600;">{pct}%</span>"""

    @app.get("/", response_class=HTMLResponse)
    async def landing():
        return HTMLResponse("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>AgentProof — Behavioral Testing for AI Agents</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;}
    body{background:#0F172A;color:#E2E8F0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh;}
    a{color:inherit;text-decoration:none;}
    .btn{display:inline-block;padding:12px 28px;border-radius:8px;font-weight:600;font-size:15px;cursor:pointer;transition:opacity 0.15s;}
    .btn:hover{opacity:0.85;}
    .btn-primary{background:#7C3AED;color:#fff;}
    .btn-outline{border:1px solid #334155;color:#CBD5E1;background:transparent;}
    .btn-outline:hover{background:#1E293B;}
    .card{background:#0F172A;border:1px solid #1E293B;border-radius:16px;padding:28px;}
    code{background:#1E293B;border-radius:4px;padding:2px 6px;font-size:13px;font-family:monospace;color:#A78BFA;}
  </style>
</head>
<body>

<!-- NAV -->
<nav style="border-bottom:1px solid #1E293B;padding:16px 48px;display:flex;align-items:center;gap:16px;position:sticky;top:0;background:#0F172A;z-index:10;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="background:#7C3AED;border-radius:10px;padding:6px 12px;font-weight:800;font-size:16px;letter-spacing:-0.5px;">AP</div>
    <span style="font-weight:700;font-size:18px;letter-spacing:-0.5px;">AgentProof</span>
  </div>
  <div style="margin-left:auto;display:flex;gap:12px;align-items:center;">
    <a href="/dashboard" class="btn btn-outline" style="padding:8px 20px;font-size:14px;">Dashboard</a>
    <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" class="btn btn-outline" style="padding:8px 20px;font-size:14px;">GitHub</a>
  </div>
</nav>

<!-- HERO -->
<section style="padding:96px 48px 80px;text-align:center;max-width:860px;margin:0 auto;">
  <div style="display:inline-flex;align-items:center;gap:8px;background:#7C3AED22;border:1px solid #7C3AED44;border-radius:20px;padding:6px 16px;font-size:13px;color:#A78BFA;margin-bottom:32px;">
    <span style="width:6px;height:6px;background:#A78BFA;border-radius:50%;display:inline-block;"></span>
    UiPath AgentHack 2025 Submission
  </div>
  <h1 style="font-size:clamp(36px,6vw,64px);font-weight:800;letter-spacing:-1.5px;line-height:1.1;margin-bottom:24px;">
    Catch AI Agent Regressions<br/>
    <span style="background:linear-gradient(135deg,#7C3AED,#06B6D4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Before They Reach Production</span>
  </h1>
  <p style="font-size:18px;color:#94A3B8;line-height:1.7;max-width:640px;margin:0 auto 40px;">
    AgentProof runs your AI agent against a suite of behavioral contracts and detects drift — when a prompt change, model update, or refactor silently breaks how your agent behaves.
  </p>
  <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
    <a href="/dashboard" class="btn btn-primary">View Live Dashboard →</a>
    <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" class="btn btn-outline">See the Code</a>
  </div>
</section>

<!-- PROBLEM STATEMENT -->
<section style="padding:0 48px 80px;max-width:860px;margin:0 auto;">
  <div style="background:linear-gradient(135deg,#7C3AED11,#06B6D411);border:1px solid #1E293B;border-radius:16px;padding:40px;text-align:center;">
    <p style="font-size:20px;color:#CBD5E1;line-height:1.7;font-style:italic;">
      "You updated the system prompt to sound friendlier. The agent now tells customers to
      <span style="color:#F43F5E;font-weight:600;">contact support</span> instead of
      <span style="color:#10B981;font-weight:600;">processing refunds directly</span>.
      Nobody noticed for two weeks."
    </p>
    <p style="margin-top:16px;color:#64748B;font-size:14px;">— The problem AgentProof solves</p>
  </div>
</section>

<!-- HOW IT WORKS -->
<section style="padding:0 48px 80px;max-width:1100px;margin:0 auto;">
  <h2 style="font-size:28px;font-weight:700;text-align:center;margin-bottom:48px;letter-spacing:-0.5px;">How It Works</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;">
    <div class="card" style="text-align:center;">
      <div style="font-size:32px;margin-bottom:16px;">📋</div>
      <div style="font-size:13px;font-weight:700;color:#7C3AED;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Step 1</div>
      <h3 style="font-size:17px;font-weight:600;margin-bottom:10px;">Define Contracts</h3>
      <p style="font-size:14px;color:#64748B;line-height:1.6;">Write behavioral rules your agent must follow — policy citations, forbidden phrases, tone requirements.</p>
    </div>
    <div class="card" style="text-align:center;">
      <div style="font-size:32px;margin-bottom:16px;">🤖</div>
      <div style="font-size:13px;font-weight:700;color:#7C3AED;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Step 2</div>
      <h3 style="font-size:17px;font-weight:600;margin-bottom:10px;">Run Test Suite</h3>
      <p style="font-size:14px;color:#64748B;line-height:1.6;">AgentProof sends test scenarios to your agent endpoint and captures every response via UiPath Orchestrator.</p>
    </div>
    <div class="card" style="text-align:center;">
      <div style="font-size:32px;margin-bottom:16px;">🧠</div>
      <div style="font-size:13px;font-weight:700;color:#7C3AED;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Step 3</div>
      <h3 style="font-size:17px;font-weight:600;margin-bottom:10px;">LLM Evaluation</h3>
      <p style="font-size:14px;color:#64748B;line-height:1.6;">A judge LLM checks each response against every contract with a pass/fail verdict and confidence score.</p>
    </div>
    <div class="card" style="text-align:center;">
      <div style="font-size:32px;margin-bottom:16px;">📊</div>
      <div style="font-size:13px;font-weight:700;color:#7C3AED;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Step 4</div>
      <h3 style="font-size:17px;font-weight:600;margin-bottom:10px;">Detect Drift</h3>
      <p style="font-size:14px;color:#64748B;line-height:1.6;">Results are compared to the last passing baseline. Regressions and drift scores are stored and surfaced in the dashboard.</p>
    </div>
  </div>
</section>

<!-- FEATURES -->
<section style="padding:0 48px 80px;max-width:1100px;margin:0 auto;">
  <h2 style="font-size:28px;font-weight:700;text-align:center;margin-bottom:48px;letter-spacing:-0.5px;">Built for the UiPath Ecosystem</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;">
    <div class="card" style="display:flex;gap:16px;align-items:flex-start;">
      <div style="background:#7C3AED22;border-radius:10px;padding:10px;flex-shrink:0;">
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#A78BFA" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      </div>
      <div>
        <h3 style="font-size:16px;font-weight:600;margin-bottom:6px;">UiPath Coded Agent</h3>
        <p style="font-size:14px;color:#64748B;line-height:1.6;">Built as a native UiPath Python coded agent using the UiPath SDK — runs directly from Orchestrator with Input/Output schemas.</p>
      </div>
    </div>
    <div class="card" style="display:flex;gap:16px;align-items:flex-start;">
      <div style="background:#06B6D422;border-radius:10px;padding:10px;flex-shrink:0;">
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#06B6D4" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
      </div>
      <div>
        <h3 style="font-size:16px;font-weight:600;margin-bottom:6px;">LangGraph Pipeline</h3>
        <p style="font-size:14px;color:#64748B;line-height:1.6;">Orchestrates test execution, LLM-based evaluation, drift detection, and report generation as a stateful graph.</p>
      </div>
    </div>
    <div class="card" style="display:flex;gap:16px;align-items:flex-start;">
      <div style="background:#10B98122;border-radius:10px;padding:10px;flex-shrink:0;">
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#10B981" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"/></svg>
      </div>
      <div>
        <h3 style="font-size:16px;font-weight:600;margin-bottom:6px;">Persistent History</h3>
        <p style="font-size:14px;color:#64748B;line-height:1.6;">Every test run is stored in Neon PostgreSQL. Baselines are auto-tracked so drift is measured against real passing runs.</p>
      </div>
    </div>
    <div class="card" style="display:flex;gap:16px;align-items:flex-start;">
      <div style="background:#F59E0B22;border-radius:10px;padding:10px;flex-shrink:0;">
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#F59E0B" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
      </div>
      <div>
        <h3 style="font-size:16px;font-weight:600;margin-bottom:6px;">Drift Scoring</h3>
        <p style="font-size:14px;color:#64748B;line-height:1.6;">Calculates a % behavioral drift score against the baseline. PASSED / DEGRADED / FAILED thresholds with per-contract breakdown.</p>
      </div>
    </div>
    <div class="card" style="display:flex;gap:16px;align-items:flex-start;">
      <div style="background:#F43F5E22;border-radius:10px;padding:10px;flex-shrink:0;">
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#F43F5E" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
      </div>
      <div>
        <h3 style="font-size:16px;font-weight:600;margin-bottom:6px;">Regression Detection</h3>
        <p style="font-size:14px;color:#64748B;line-height:1.6;">Flags specific contracts that passed before but now fail. Gives you a precise list of what broke and why.</p>
      </div>
    </div>
    <div class="card" style="display:flex;gap:16px;align-items:flex-start;">
      <div style="background:#8B5CF622;border-radius:10px;padding:10px;flex-shrink:0;">
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#8B5CF6" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"/></svg>
      </div>
      <div>
        <h3 style="font-size:16px;font-weight:600;margin-bottom:6px;">Demo Agent Included</h3>
        <p style="font-size:14px;color:#64748B;line-height:1.6;">Ships with a ShopEasy customer support demo agent in two versions — V1 (compliant) vs V2 (drifted) — to showcase detection live.</p>
      </div>
    </div>
  </div>
</section>

<!-- DEMO SCENARIO -->
<section style="padding:0 48px 80px;max-width:860px;margin:0 auto;">
  <h2 style="font-size:28px;font-weight:700;text-align:center;margin-bottom:16px;letter-spacing:-0.5px;">Live Demo Scenario</h2>
  <p style="text-align:center;color:#64748B;margin-bottom:40px;font-size:15px;">Two versions of a ShopEasy refund agent. Same task, different behavior.</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
    <div class="card">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
        <span style="background:#10B98122;color:#10B981;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700;">V1 — Compliant</span>
      </div>
      <ul style="list-style:none;display:flex;flex-direction:column;gap:8px;">
        <li style="display:flex;gap:8px;font-size:13px;color:#CBD5E1;"><span style="color:#10B981;">✓</span> Confirms refund eligibility</li>
        <li style="display:flex;gap:8px;font-size:13px;color:#CBD5E1;"><span style="color:#10B981;">✓</span> Cites Section 3.1 policy</li>
        <li style="display:flex;gap:8px;font-size:13px;color:#CBD5E1;"><span style="color:#10B981;">✓</span> Handles request directly</li>
        <li style="display:flex;gap:8px;font-size:13px;color:#CBD5E1;"><span style="color:#10B981;">✓</span> Stays under 100 words</li>
      </ul>
    </div>
    <div class="card">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
        <span style="background:#F43F5E22;color:#F43F5E;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700;">V2 — Drifted</span>
      </div>
      <ul style="list-style:none;display:flex;flex-direction:column;gap:8px;">
        <li style="display:flex;gap:8px;font-size:13px;color:#CBD5E1;"><span style="color:#F43F5E;">✗</span> Skips refund confirmation</li>
        <li style="display:flex;gap:8px;font-size:13px;color:#CBD5E1;"><span style="color:#F43F5E;">✗</span> No policy citation</li>
        <li style="display:flex;gap:8px;font-size:13px;color:#CBD5E1;"><span style="color:#F43F5E;">✗</span> Deflects to support team</li>
        <li style="display:flex;gap:8px;font-size:13px;color:#CBD5E1;"><span style="color:#10B981;">✓</span> Friendly tone</li>
      </ul>
    </div>
  </div>
  <div style="text-align:center;margin-top:32px;">
    <a href="/dashboard" class="btn btn-primary">See Detection Results in Dashboard →</a>
  </div>
</section>

<!-- TECH STACK -->
<section style="padding:0 48px 80px;max-width:860px;margin:0 auto;text-align:center;">
  <h2 style="font-size:22px;font-weight:700;margin-bottom:32px;color:#94A3B8;">Built With</h2>
  <div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;">
    <span style="background:#1E293B;border:1px solid #334155;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:500;">UiPath SDK</span>
    <span style="background:#1E293B;border:1px solid #334155;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:500;">LangGraph</span>
    <span style="background:#1E293B;border:1px solid #334155;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:500;">OpenRouter / GPT-4o-mini</span>
    <span style="background:#1E293B;border:1px solid #334155;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:500;">FastAPI</span>
    <span style="background:#1E293B;border:1px solid #334155;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:500;">Neon PostgreSQL</span>
    <span style="background:#1E293B;border:1px solid #334155;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:500;">Vercel</span>
    <span style="background:#1E293B;border:1px solid #334155;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:500;">Python 3.12</span>
  </div>
</section>

<!-- FOOTER -->
<footer style="border-top:1px solid #1E293B;padding:32px 48px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="background:#7C3AED;border-radius:8px;padding:4px 10px;font-weight:800;font-size:14px;">AP</div>
    <span style="color:#64748B;font-size:14px;">AgentProof — UiPath AgentHack 2025</span>
  </div>
  <div style="display:flex;gap:16px;">
    <a href="/dashboard" style="color:#64748B;font-size:14px;">Dashboard</a>
    <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" style="color:#64748B;font-size:14px;">GitHub</a>
    <a href="/health" style="color:#64748B;font-size:14px;">API Status</a>
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

        rows = ""
        for r in runs:
            status = r["overall_status"]
            color = _status_color(status)
            drift = r["drift_score"] or 0
            regressions = r["regressions"]
            if isinstance(regressions, str):
                regressions = json.loads(regressions)
            reg_count = len(regressions) if regressions else 0
            ts = str(r["timestamp"])[:19].replace("T", " ")
            rows += f"""<tr onclick="window.location='/run/{r['id']}'" style="cursor:pointer;">
              <td style="padding:14px 16px;color:#94A3B8;font-size:13px;">{ts}</td>
              <td style="padding:14px 16px;color:#E2E8F0;font-weight:500;">{r['suite_id']}</td>
              <td style="padding:14px 16px;"><span style="background:{color}22;color:{color};padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">{status}</span></td>
              <td style="padding:14px 16px;min-width:160px;">{_drift_bar(drift)}</td>
              <td style="padding:14px 16px;color:{'#F43F5E' if reg_count>0 else '#10B981'};font-weight:600;">{reg_count}</td>
              <td style="padding:14px 16px;color:#64748B;font-size:12px;font-family:monospace;">{str(r['id'])[:8]}…</td>
            </tr>"""

        error_banner = f'<div style="background:#F43F5E22;border:1px solid #F43F5E;color:#F43F5E;padding:12px 16px;border-radius:8px;margin-bottom:24px;">DB Error: {error}</div>' if error else ""

        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AgentProof Dashboard</title>
<style>*{{box-sizing:border-box;margin:0;padding:0;}}body{{background:#0F172A;color:#E2E8F0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh;}}tr:hover td{{background:#1E293B;}}</style>
</head><body>
<header style="background:#0F172A;border-bottom:1px solid #1E293B;padding:20px 40px;display:flex;align-items:center;gap:16px;">
  <a href="/" style="background:#1E293B;border-radius:8px;padding:6px 14px;font-size:13px;color:#94A3B8;text-decoration:none;">← Home</a>
  <div style="background:#7C3AED;border-radius:10px;padding:8px 14px;font-weight:700;font-size:18px;">AP</div>
  <div><div style="font-size:20px;font-weight:700;">AgentProof</div><div style="font-size:12px;color:#64748B;">Behavioral Testing & Regression Detection</div></div>
  <div style="margin-left:auto;display:flex;gap:32px;text-align:center;">
    <div><div style="font-size:24px;font-weight:700;color:#7C3AED;">{len(runs)}</div><div style="font-size:11px;color:#64748B;">Total Runs</div></div>
    <div><div style="font-size:24px;font-weight:700;color:#10B981;">{sum(1 for r in runs if r['overall_status']=='PASSED')}</div><div style="font-size:11px;color:#64748B;">Passed</div></div>
    <div><div style="font-size:24px;font-weight:700;color:#F43F5E;">{sum(1 for r in runs if r['overall_status']=='FAILED')}</div><div style="font-size:11px;color:#64748B;">Failed</div></div>
  </div>
</header>
<main style="padding:40px;">
  {error_banner}
  <h2 style="font-size:14px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;margin-bottom:24px;">Recent Runs</h2>
  <div style="border:1px solid #1E293B;border-radius:12px;overflow:hidden;">
    <table style="width:100%;border-collapse:collapse;">
      <thead><tr style="border-bottom:1px solid #1E293B;">
        <th style="padding:12px 16px;text-align:left;font-size:12px;color:#64748B;font-weight:500;">Timestamp</th>
        <th style="padding:12px 16px;text-align:left;font-size:12px;color:#64748B;font-weight:500;">Suite</th>
        <th style="padding:12px 16px;text-align:left;font-size:12px;color:#64748B;font-weight:500;">Status</th>
        <th style="padding:12px 16px;text-align:left;font-size:12px;color:#64748B;font-weight:500;">Drift Score</th>
        <th style="padding:12px 16px;text-align:left;font-size:12px;color:#64748B;font-weight:500;">Regressions</th>
        <th style="padding:12px 16px;text-align:left;font-size:12px;color:#64748B;font-weight:500;">Run ID</th>
      </tr></thead>
      <tbody>{rows if rows else '<tr><td colspan="6" style="padding:40px;text-align:center;color:#475569;">No runs yet. Trigger AgentProof from UiPath Orchestrator to see results.</td></tr>'}</tbody>
    </table>
  </div>
</main>
</body></html>""")

    @app.get("/run/{run_id}", response_class=HTMLResponse)
    async def run_detail(run_id: str):
        try:
            from agentproof.db import get_run_by_id
            run = get_run_by_id(run_id)
        except Exception as e:
            return HTMLResponse(f"<p style='color:red;padding:40px'>Error: {e}</p>", status_code=500)

        if not run:
            return HTMLResponse("<p style='padding:40px'>Run not found</p>", status_code=404)

        status = run["overall_status"]
        color = _status_color(status)
        drift = round((run["drift_score"] or 0) * 100, 1)
        ts = str(run["timestamp"])[:19].replace("T", " ")
        results = run["results"]
        if isinstance(results, str):
            results = json.loads(results)
        regressions = run["regressions"]
        if isinstance(regressions, str):
            regressions = json.loads(regressions)

        test_cards = ""
        for r in (results or []):
            tc_color = "#10B981" if r["overall_pass"] else "#F43F5E"
            tc_status = "PASS" if r["overall_pass"] else "FAIL"
            contracts_html = ""
            for ev in r.get("contract_evaluations", []):
                ev_color = "#10B981" if ev["passed"] else "#F43F5E"
                contracts_html += f"""<div style="display:flex;gap:10px;padding:10px 0;border-bottom:1px solid #1E293B;">
                  <span style="color:{ev_color};font-weight:700;">{"✓" if ev["passed"] else "✗"}</span>
                  <div style="flex:1;"><div style="font-size:12px;color:#94A3B8;font-family:monospace;">{ev['contract_id']}</div>
                  <div style="font-size:13px;color:#CBD5E1;margin-top:2px;">{ev['reasoning']}</div></div>
                  <span style="font-size:11px;color:#64748B;">{round(ev['confidence']*100)}%</span>
                </div>"""
            test_cards += f"""<div style="border:1px solid #1E293B;border-radius:12px;padding:20px;margin-bottom:16px;">
              <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <span style="background:{tc_color}22;color:{tc_color};padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700;">{tc_status}</span>
                <span style="font-weight:600;">{r['test_name']}</span>
                <span style="margin-left:auto;font-size:11px;color:#64748B;text-transform:uppercase;">{r['severity']}</span>
              </div>
              <div style="background:#1E293B;border-radius:8px;padding:12px;margin-bottom:12px;">
                <div style="font-size:11px;color:#64748B;margin-bottom:4px;">Agent Response</div>
                <div style="font-size:13px;color:#CBD5E1;line-height:1.6;">{r['agent_response'][:300]}{"…" if len(r["agent_response"])>300 else ""}</div>
              </div>{contracts_html}
            </div>"""

        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><title>Run {run_id[:8]} — AgentProof</title>
<style>*{{box-sizing:border-box;margin:0;padding:0;}}body{{background:#0F172A;color:#E2E8F0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}}</style>
</head><body>
<header style="background:#0F172A;border-bottom:1px solid #1E293B;padding:20px 40px;display:flex;align-items:center;gap:16px;">
  <a href="/dashboard" style="background:#1E293B;border-radius:8px;padding:6px 14px;font-size:13px;color:#94A3B8;text-decoration:none;">← Dashboard</a>
  <div style="background:#7C3AED;border-radius:10px;padding:6px 12px;font-weight:700;">AP</div>
  <div><div style="font-size:18px;font-weight:700;">Run Detail</div><div style="font-size:12px;color:#64748B;font-family:monospace;">{run_id}</div></div>
</header>
<main style="padding:40px;max-width:900px;">
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:32px;">
    <div style="border:1px solid #1E293B;border-radius:12px;padding:20px;"><div style="font-size:11px;color:#64748B;text-transform:uppercase;margin-bottom:8px;">Status</div><div style="font-size:22px;font-weight:700;color:{color};">{status}</div></div>
    <div style="border:1px solid #1E293B;border-radius:12px;padding:20px;"><div style="font-size:11px;color:#64748B;text-transform:uppercase;margin-bottom:8px;">Drift Score</div><div style="font-size:22px;font-weight:700;color:{color};">{drift}%</div></div>
    <div style="border:1px solid #1E293B;border-radius:12px;padding:20px;"><div style="font-size:11px;color:#64748B;text-transform:uppercase;margin-bottom:8px;">Regressions</div><div style="font-size:22px;font-weight:700;color:{'#F43F5E' if regressions else '#10B981'};">{len(regressions) if regressions else 0}</div></div>
    <div style="border:1px solid #1E293B;border-radius:12px;padding:20px;"><div style="font-size:11px;color:#64748B;text-transform:uppercase;margin-bottom:8px;">Suite</div><div style="font-size:16px;font-weight:600;">{run['suite_id']}</div></div>
  </div>
  <div style="font-size:12px;color:#64748B;margin-bottom:24px;">{ts} UTC</div>
  <h3 style="font-size:14px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;">Test Cases</h3>
  {test_cards}
</main></body></html>""")

except Exception as _startup_error:
    _tb = traceback.format_exc()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def startup_error(path: str = ""):
        return JSONResponse({"error": str(_startup_error), "traceback": _tb}, status_code=500)
