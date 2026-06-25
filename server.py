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
    body{background:#fafaf9;color:#1c1917;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;}
    a{text-decoration:none;color:inherit;}
    .nav-link{font-size:14px;color:#78716c;padding:6px 12px;border-radius:6px;transition:background 0.15s;}
    .nav-link:hover{background:#f5f5f4;color:#1c1917;}
    .btn-dark{display:inline-block;background:#1c1917;color:#fff;padding:11px 24px;border-radius:7px;font-size:14px;font-weight:600;transition:opacity 0.15s;}
    .btn-dark:hover{opacity:0.85;}
    .btn-outline{display:inline-block;background:transparent;color:#1c1917;padding:11px 24px;border-radius:7px;font-size:14px;font-weight:500;border:1.5px solid #d6d3d1;transition:border-color 0.15s;}
    .btn-outline:hover{border-color:#a8a29e;}
    section{padding:80px 0;}
  </style>
</head>
<body>

<!-- NAV -->
<header style="background:#fafaf9;border-bottom:1px solid #e7e5e4;position:sticky;top:0;z-index:50;">
  <div style="max-width:1100px;margin:0 auto;padding:0 40px;height:60px;display:flex;align-items:center;justify-content:space-between;">
    <div style="display:flex;align-items:center;gap:32px;">
      <div style="display:flex;align-items:center;gap:9px;">
        <div style="background:#f97316;color:#fff;border-radius:6px;padding:4px 9px;font-weight:800;font-size:13px;letter-spacing:-0.3px;">AP</div>
        <span style="font-weight:700;font-size:15px;color:#1c1917;">AgentProof</span>
      </div>
      <nav style="display:flex;gap:4px;">
        <a href="#how-it-works" class="nav-link">How it works</a>
        <a href="#demo" class="nav-link">Demo</a>
        <a href="/dashboard" class="nav-link">Dashboard</a>
      </nav>
    </div>
    <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" class="nav-link" style="display:flex;align-items:center;gap:6px;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>
      GitHub
    </a>
  </div>
</header>

<!-- HERO -->
<section style="padding:100px 0 80px;background:#fafaf9;">
  <div style="max-width:820px;margin:0 auto;padding:0 40px;">
    <div style="display:inline-block;background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;border-radius:20px;padding:4px 14px;font-size:12px;font-weight:600;letter-spacing:0.5px;margin-bottom:28px;">UiPath AgentHack 2025</div>
    <h1 style="font-size:52px;font-weight:800;line-height:1.1;letter-spacing:-1.5px;color:#1c1917;margin-bottom:24px;">Did your last prompt<br/>change break anything?</h1>
    <p style="font-size:18px;color:#57534e;max-width:580px;margin-bottom:16px;">You tweak the system prompt, swap the model, or clean up some wording. The agent still responds. But does it still <em>behave</em> the way it's supposed to?</p>
    <p style="font-size:18px;color:#57534e;max-width:580px;margin-bottom:40px;">AgentProof runs your agent through a set of behavioral contracts after every change and tells you exactly what regressed — before it reaches a real user.</p>
    <div style="display:flex;gap:12px;flex-wrap:wrap;">
      <a href="/dashboard" class="btn-dark">Open Dashboard</a>
      <a href="#how-it-works" class="btn-outline">See how it works</a>
    </div>
  </div>
</section>

<!-- DEMO -->
<section id="demo" style="padding:80px 0;background:#fff;border-top:1px solid #e7e5e4;border-bottom:1px solid #e7e5e4;">
  <div style="max-width:820px;margin:0 auto;padding:0 40px;">
    <p style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#a8a29e;margin-bottom:12px;">Live example</p>
    <h2 style="font-size:30px;font-weight:700;letter-spacing:-0.5px;margin-bottom:10px;">The prompt got "warmer". The behavior broke.</h2>
    <p style="font-size:15px;color:#78716c;margin-bottom:36px;">A ShopEasy refund agent was updated to sound more empathetic. Nobody noticed it stopped following 3 critical contracts.</p>

    <div style="border:1px solid #e7e5e4;border-radius:10px;overflow:hidden;">
      <div style="display:grid;grid-template-columns:1fr 1fr;">
        <div style="padding:24px 28px;border-right:1px solid #e7e5e4;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:18px;">
            <span style="width:8px;height:8px;background:#16a34a;border-radius:50%;display:inline-block;"></span>
            <span style="font-size:12px;font-weight:700;color:#15803d;text-transform:uppercase;letter-spacing:0.8px;">V1 — All contracts pass</span>
          </div>
          <div style="display:flex;flex-direction:column;gap:11px;">
            <div style="display:flex;gap:10px;align-items:flex-start;"><span style="color:#16a34a;font-weight:700;margin-top:1px;">✓</span><span style="font-size:14px;color:#44403c;">Confirms customer is eligible for a refund</span></div>
            <div style="display:flex;gap:10px;align-items:flex-start;"><span style="color:#16a34a;font-weight:700;margin-top:1px;">✓</span><span style="font-size:14px;color:#44403c;">Cites Return Policy Section 3.1 by name</span></div>
            <div style="display:flex;gap:10px;align-items:flex-start;"><span style="color:#16a34a;font-weight:700;margin-top:1px;">✓</span><span style="font-size:14px;color:#44403c;">Handles the request directly — no handoff</span></div>
            <div style="display:flex;gap:10px;align-items:flex-start;"><span style="color:#16a34a;font-weight:700;margin-top:1px;">✓</span><span style="font-size:14px;color:#44403c;">Response under 100 words</span></div>
          </div>
        </div>
        <div style="padding:24px 28px;background:#fffbf9;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:18px;">
            <span style="width:8px;height:8px;background:#dc2626;border-radius:50%;display:inline-block;"></span>
            <span style="font-size:12px;font-weight:700;color:#b91c1c;text-transform:uppercase;letter-spacing:0.8px;">V2 — 3 regressions</span>
          </div>
          <div style="display:flex;flex-direction:column;gap:11px;">
            <div style="display:flex;gap:10px;align-items:flex-start;"><span style="color:#dc2626;font-weight:700;margin-top:1px;">✗</span><span style="font-size:14px;color:#44403c;">No mention of refund eligibility</span></div>
            <div style="display:flex;gap:10px;align-items:flex-start;"><span style="color:#dc2626;font-weight:700;margin-top:1px;">✗</span><span style="font-size:14px;color:#44403c;">Policy never referenced</span></div>
            <div style="display:flex;gap:10px;align-items:flex-start;"><span style="color:#dc2626;font-weight:700;margin-top:1px;">✗</span><span style="font-size:14px;color:#44403c;">Tells the customer to contact support instead</span></div>
            <div style="display:flex;gap:10px;align-items:flex-start;"><span style="color:#16a34a;font-weight:700;margin-top:1px;">✓</span><span style="font-size:14px;color:#44403c;">Still sounds warm and friendly</span></div>
          </div>
        </div>
      </div>
      <div style="padding:14px 28px;background:#f5f5f4;border-top:1px solid #e7e5e4;display:flex;align-items:center;justify-content:space-between;">
        <span style="font-size:13px;color:#78716c;">AgentProof flagged this automatically. Drift score: <strong style="color:#c2410c;">75%</strong> — status: <strong style="color:#dc2626;">FAILED</strong></span>
        <a href="/dashboard" style="font-size:13px;color:#f97316;font-weight:600;">View in dashboard →</a>
      </div>
    </div>
  </div>
</section>

<!-- HOW IT WORKS -->
<section id="how-it-works" style="padding:80px 0;background:#fafaf9;">
  <div style="max-width:820px;margin:0 auto;padding:0 40px;">
    <p style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#a8a29e;margin-bottom:12px;">How it works</p>
    <h2 style="font-size:30px;font-weight:700;letter-spacing:-0.5px;margin-bottom:48px;">Three steps, no setup overhead</h2>
    <div style="display:flex;flex-direction:column;gap:0;">
      <div style="display:flex;gap:24px;padding-bottom:40px;border-bottom:1px solid #e7e5e4;">
        <div style="flex-shrink:0;width:36px;height:36px;border-radius:50%;background:#fff7ed;border:2px solid #fed7aa;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;color:#f97316;">1</div>
        <div style="padding-top:6px;">
          <h3 style="font-size:17px;font-weight:700;margin-bottom:8px;color:#1c1917;">Write behavioral contracts</h3>
          <p style="font-size:14px;color:#78716c;max-width:500px;">Define the rules your agent must follow — always cite this policy, never redirect to support for simple requests, respond in under 100 words. Plain language, stored in JSON test suites.</p>
        </div>
      </div>
      <div style="display:flex;gap:24px;padding:40px 0;border-bottom:1px solid #e7e5e4;">
        <div style="flex-shrink:0;width:36px;height:36px;border-radius:50%;background:#fff7ed;border:2px solid #fed7aa;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;color:#f97316;">2</div>
        <div style="padding-top:6px;">
          <h3 style="font-size:17px;font-weight:700;margin-bottom:8px;color:#1c1917;">Trigger from UiPath Orchestrator</h3>
          <p style="font-size:14px;color:#78716c;max-width:500px;">Run AgentProof as a native coded agent — pass your agent's endpoint and test suite ID. It calls the agent with each test scenario, collects responses, and evaluates each one against every contract using an LLM judge.</p>
        </div>
      </div>
      <div style="display:flex;gap:24px;padding-top:40px;">
        <div style="flex-shrink:0;width:36px;height:36px;border-radius:50%;background:#fff7ed;border:2px solid #fed7aa;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;color:#f97316;">3</div>
        <div style="padding-top:6px;">
          <h3 style="font-size:17px;font-weight:700;margin-bottom:8px;color:#1c1917;">See exactly what changed</h3>
          <p style="font-size:14px;color:#78716c;max-width:500px;">Results are compared against the last passing baseline. You get a drift score, a list of regressions with reasoning, and a per-contract breakdown — stored in the dashboard for every run.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<section style="padding:80px 0;background:#1c1917;border-top:1px solid #292524;">
  <div style="max-width:820px;margin:0 auto;padding:0 40px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:24px;">
    <div>
      <h2 style="font-size:26px;font-weight:700;color:#fafaf9;margin-bottom:8px;">See it in action</h2>
      <p style="font-size:15px;color:#a8a29e;">The dashboard has live results from the demo agent above.</p>
    </div>
    <div style="display:flex;gap:12px;flex-wrap:wrap;">
      <a href="/dashboard" style="display:inline-block;background:#f97316;color:#fff;padding:11px 24px;border-radius:7px;font-size:14px;font-weight:700;">Open Dashboard</a>
      <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" style="display:inline-block;background:transparent;color:#d6d3d1;padding:11px 24px;border-radius:7px;font-size:14px;font-weight:500;border:1.5px solid #44403c;">View Source</a>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer style="background:#fff;border-top:1px solid #e7e5e4;padding:28px 40px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
  <div style="display:flex;align-items:center;gap:8px;">
    <div style="background:#f97316;color:#fff;border-radius:5px;padding:3px 8px;font-weight:800;font-size:12px;">AP</div>
    <span style="font-size:13px;color:#a8a29e;">AgentProof · UiPath AgentHack 2025</span>
  </div>
  <div style="display:flex;gap:20px;">
    <a href="/dashboard" style="font-size:13px;color:#a8a29e;">Dashboard</a>
    <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" style="font-size:13px;color:#a8a29e;">GitHub</a>
    <a href="/health" style="font-size:13px;color:#a8a29e;">API</a>
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
