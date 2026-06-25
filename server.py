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
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --orange: #f97316;
      --orange-light: #fff7ed;
      --orange-border: #fed7aa;
      --green: #16a34a;
      --red: #dc2626;
      --ink: #111110;
      --ink-2: #3d3d3a;
      --ink-3: #6b6b66;
      --ink-4: #a3a39e;
      --bg: #ffffff;
      --bg-2: #f7f7f5;
      --bg-dark: #111110;
      --border: #e8e8e4;
      --radius: 8px;
      --radius-sm: 5px;
      --shadow-sm: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.06);
      --shadow: 0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.05);
    }

    body {
      background: var(--bg);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
      font-size: 16px;
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }
    a { text-decoration: none; color: inherit; }

    .container { max-width: 1000px; margin: 0 auto; padding: 0 48px; }
    .container-narrow { max-width: 760px; margin: 0 auto; padding: 0 48px; }

    /* Nav */
    header { background: rgba(255,255,255,0.94); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }
    .nav { height: 64px; display: flex; align-items: center; justify-content: space-between; }
    .nav-logo { display: flex; align-items: center; gap: 10px; }
    .nav-badge { background: var(--orange); color: #fff; border-radius: var(--radius-sm); padding: 3px 9px; font-weight: 800; font-size: 13px; letter-spacing: -0.2px; }
    .nav-name { font-weight: 700; font-size: 15px; color: var(--ink); }
    .nav-links { display: flex; align-items: center; gap: 2px; }
    .nav-link { font-size: 14px; color: var(--ink-3); padding: 6px 12px; border-radius: 6px; transition: background .15s, color .15s; }
    .nav-link:hover { background: var(--bg-2); color: var(--ink); }
    .nav-actions { display: flex; align-items: center; gap: 8px; }

    /* Buttons */
    .btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: var(--radius); font-size: 14px; font-weight: 600; cursor: pointer; transition: all .15s; white-space: nowrap; }
    .btn-primary { background: var(--ink); color: #fff; box-shadow: var(--shadow-sm); }
    .btn-primary:hover { background: #2a2a27; box-shadow: var(--shadow); }
    .btn-secondary { background: var(--bg); color: var(--ink); border: 1.5px solid var(--border); }
    .btn-secondary:hover { border-color: #c8c8c2; background: var(--bg-2); }
    .btn-orange { background: var(--orange); color: #fff; box-shadow: var(--shadow-sm); }
    .btn-orange:hover { background: #ea6c00; box-shadow: var(--shadow); }
    .btn-lg { padding: 13px 28px; font-size: 15px; border-radius: 9px; }

    /* Badge */
    .badge { display: inline-flex; align-items: center; gap: 6px; background: var(--orange-light); color: #c2410c; border: 1px solid var(--orange-border); border-radius: 20px; padding: 4px 14px; font-size: 12px; font-weight: 600; letter-spacing: 0.3px; }

    /* Divider */
    .divider { height: 1px; background: var(--border); }

    /* Check/cross */
    .pass { color: var(--green); font-weight: 700; }
    .fail { color: var(--red); font-weight: 700; }

    /* Step number */
    .step-num { flex-shrink: 0; width: 38px; height: 38px; border-radius: 50%; background: var(--orange-light); border: 2px solid var(--orange-border); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px; color: var(--orange); }
  </style>
</head>
<body>

<!-- NAV -->
<header>
  <div class="container nav">
    <div class="nav-logo">
      <span class="nav-badge">AP</span>
      <span class="nav-name">AgentProof</span>
      <div class="nav-links" style="margin-left:16px;">
        <a href="#how-it-works" class="nav-link">How it works</a>
        <a href="#demo" class="nav-link">Demo</a>
        <a href="/dashboard" class="nav-link">Dashboard</a>
      </div>
    </div>
    <div class="nav-actions">
      <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" class="btn btn-secondary" style="font-weight:500;">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" style="opacity:.7"><path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>
        GitHub
      </a>
    </div>
  </div>
</header>

<!-- HERO -->
<section style="padding:96px 0 80px; background:var(--bg);">
  <div class="container-narrow">
    <span class="badge" style="margin-bottom:28px; display:inline-flex;">UiPath AgentHack 2025</span>
    <h1 style="font-size:54px; font-weight:800; line-height:1.1; letter-spacing:-2px; color:var(--ink); margin-bottom:22px;">
      Did your last prompt<br>change break anything?
    </h1>
    <p style="font-size:18px; color:var(--ink-3); max-width:560px; line-height:1.7; margin-bottom:14px;">
      You tweak the system prompt, swap the model, or clean up some wording. The agent still responds. But does it still <em>behave</em> the way it's supposed to?
    </p>
    <p style="font-size:18px; color:var(--ink-3); max-width:560px; line-height:1.7; margin-bottom:40px;">
      AgentProof runs your agent through a set of behavioral contracts after every change and surfaces exactly what regressed — before it reaches a real user.
    </p>
    <div style="display:flex; gap:12px; flex-wrap:wrap;">
      <a href="/dashboard" class="btn btn-primary btn-lg">Open Dashboard</a>
      <a href="#how-it-works" class="btn btn-secondary btn-lg">How it works</a>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- DEMO -->
<section id="demo" style="padding:80px 0; background:var(--bg-2);">
  <div class="container-narrow">
    <p style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1.8px; color:var(--ink-4); margin-bottom:10px;">Live example</p>
    <h2 style="font-size:32px; font-weight:700; letter-spacing:-0.8px; color:var(--ink); margin-bottom:10px;">The prompt got "warmer". The behavior broke.</h2>
    <p style="font-size:15px; color:var(--ink-3); margin-bottom:36px; max-width:540px;">A ShopEasy refund agent was updated to sound more empathetic. Nobody noticed it stopped following 3 critical contracts.</p>

    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; overflow:hidden; box-shadow:var(--shadow);">
      <div style="display:grid; grid-template-columns:1fr 1fr;">
        <!-- V1 -->
        <div style="padding:28px 32px; border-right:1px solid var(--border);">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:20px;">
            <span style="width:7px; height:7px; background:var(--green); border-radius:50%; display:inline-block;"></span>
            <span style="font-size:11px; font-weight:700; color:var(--green); text-transform:uppercase; letter-spacing:1px;">V1 — All contracts pass</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:12px;">
            <div style="display:flex; gap:10px;"><span class="pass">✓</span><span style="font-size:14px; color:var(--ink-2);">Confirms customer is eligible for a refund</span></div>
            <div style="display:flex; gap:10px;"><span class="pass">✓</span><span style="font-size:14px; color:var(--ink-2);">Cites Return Policy Section 3.1 by name</span></div>
            <div style="display:flex; gap:10px;"><span class="pass">✓</span><span style="font-size:14px; color:var(--ink-2);">Resolves the request directly, no handoff</span></div>
            <div style="display:flex; gap:10px;"><span class="pass">✓</span><span style="font-size:14px; color:var(--ink-2);">Response under 100 words</span></div>
          </div>
        </div>
        <!-- V2 -->
        <div style="padding:28px 32px; background:#fffcfa;">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:20px;">
            <span style="width:7px; height:7px; background:var(--red); border-radius:50%; display:inline-block;"></span>
            <span style="font-size:11px; font-weight:700; color:var(--red); text-transform:uppercase; letter-spacing:1px;">V2 — 3 regressions detected</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:12px;">
            <div style="display:flex; gap:10px;"><span class="fail">✗</span><span style="font-size:14px; color:var(--ink-2);">No mention of refund eligibility</span></div>
            <div style="display:flex; gap:10px;"><span class="fail">✗</span><span style="font-size:14px; color:var(--ink-2);">Policy never referenced</span></div>
            <div style="display:flex; gap:10px;"><span class="fail">✗</span><span style="font-size:14px; color:var(--ink-2);">Tells the customer to contact support instead</span></div>
            <div style="display:flex; gap:10px;"><span class="pass">✓</span><span style="font-size:14px; color:var(--ink-2);">Still sounds warm and friendly</span></div>
          </div>
        </div>
      </div>
      <div style="padding:14px 32px; background:var(--bg-2); border-top:1px solid var(--border); display:flex; align-items:center; justify-content:space-between;">
        <span style="font-size:13px; color:var(--ink-3);">Drift score: <strong style="color:#c2410c;">75%</strong> &nbsp;·&nbsp; Status: <strong style="color:var(--red);">FAILED</strong></span>
        <a href="/dashboard" style="font-size:13px; color:var(--orange); font-weight:600;">View full report →</a>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- HOW IT WORKS -->
<section id="how-it-works" style="padding:80px 0; background:var(--bg);">
  <div class="container-narrow">
    <p style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1.8px; color:var(--ink-4); margin-bottom:10px;">How it works</p>
    <h2 style="font-size:32px; font-weight:700; letter-spacing:-0.8px; color:var(--ink); margin-bottom:52px;">Three steps, no setup overhead</h2>

    <div style="display:flex; flex-direction:column; gap:40px;">
      <div style="display:flex; gap:24px; align-items:flex-start;">
        <div class="step-num">1</div>
        <div>
          <h3 style="font-size:17px; font-weight:700; color:var(--ink); margin-bottom:8px;">Write behavioral contracts</h3>
          <p style="font-size:15px; color:var(--ink-3); max-width:520px; line-height:1.7;">Define the rules your agent must follow — always cite this policy, never redirect to support for simple requests, respond in under 100 words. Plain language, stored in JSON test suites alongside your code.</p>
        </div>
      </div>
      <div style="display:flex; gap:24px; align-items:flex-start;">
        <div class="step-num">2</div>
        <div>
          <h3 style="font-size:17px; font-weight:700; color:var(--ink); margin-bottom:8px;">Trigger from UiPath Orchestrator</h3>
          <p style="font-size:15px; color:var(--ink-3); max-width:520px; line-height:1.7;">Run AgentProof as a native coded agent — pass your agent's endpoint and test suite ID. It calls the agent with each scenario, collects every response, and runs each one through an LLM judge that evaluates it against every contract.</p>
        </div>
      </div>
      <div style="display:flex; gap:24px; align-items:flex-start;">
        <div class="step-num">3</div>
        <div>
          <h3 style="font-size:17px; font-weight:700; color:var(--ink); margin-bottom:8px;">See exactly what changed</h3>
          <p style="font-size:15px; color:var(--ink-3); max-width:520px; line-height:1.7;">Results are compared to the last passing baseline. You get a drift %, a list of regressions with LLM reasoning, and a per-contract breakdown — every run persisted to the dashboard.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- CTA -->
<section style="padding:72px 0; background:var(--bg-dark);">
  <div class="container-narrow" style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:28px;">
    <div>
      <h2 style="font-size:28px; font-weight:700; color:#fff; letter-spacing:-0.5px; margin-bottom:8px;">See it running live</h2>
      <p style="font-size:15px; color:#78716c;">The dashboard shows real results from the demo above.</p>
    </div>
    <div style="display:flex; gap:10px; flex-wrap:wrap;">
      <a href="/dashboard" class="btn btn-orange btn-lg">Open Dashboard</a>
      <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" class="btn btn-lg" style="background:transparent; color:#a8a29e; border:1.5px solid #292524;">View Source</a>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer style="background:var(--bg); border-top:1px solid var(--border); padding:24px 0;">
  <div class="container" style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
    <div style="display:flex; align-items:center; gap:8px;">
      <span class="nav-badge" style="font-size:12px; padding:2px 8px;">AP</span>
      <span style="font-size:13px; color:var(--ink-4);">AgentProof &nbsp;·&nbsp; UiPath AgentHack 2025</span>
    </div>
    <div style="display:flex; gap:24px;">
      <a href="/dashboard" style="font-size:13px; color:var(--ink-4);">Dashboard</a>
      <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" style="font-size:13px; color:var(--ink-4);">GitHub</a>
      <a href="/health" style="font-size:13px; color:var(--ink-4);">API Status</a>
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
