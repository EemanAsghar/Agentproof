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
  <title>AgentProof</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;}
    body{background:#0F172A;color:#CBD5E1;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh;line-height:1.6;}
    a{color:inherit;text-decoration:none;}
    p{color:#94A3B8;}
  </style>
</head>
<body>

<nav style="padding:20px 40px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1E293B;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="background:#7C3AED;border-radius:8px;padding:5px 11px;font-weight:700;font-size:15px;">AP</div>
    <span style="font-weight:600;font-size:16px;color:#E2E8F0;">AgentProof</span>
  </div>
  <div style="display:flex;gap:8px;">
    <a href="/dashboard" style="padding:7px 16px;border-radius:6px;font-size:13px;border:1px solid #334155;color:#94A3B8;">Dashboard</a>
    <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" style="padding:7px 16px;border-radius:6px;font-size:13px;border:1px solid #334155;color:#94A3B8;">GitHub</a>
  </div>
</nav>

<div style="max-width:720px;margin:80px auto;padding:0 40px;">

  <p style="font-size:12px;color:#7C3AED;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:20px;">UiPath AgentHack 2025</p>

  <h1 style="font-size:42px;font-weight:700;color:#F1F5F9;letter-spacing:-1px;line-height:1.15;margin-bottom:24px;">
    Did your last prompt change<br/>break anything?
  </h1>

  <p style="font-size:16px;margin-bottom:16px;">
    You tweak the system prompt, swap the model, or clean up some wording. The agent still responds. But does it still behave the way it's supposed to?
  </p>

  <p style="font-size:16px;margin-bottom:48px;">
    AgentProof runs your AI agent through a set of behavioral contracts after every change and tells you exactly what regressed — before it reaches a real user.
  </p>

  <div style="border:1px solid #1E293B;border-radius:10px;overflow:hidden;margin-bottom:48px;">
    <div style="padding:12px 16px;border-bottom:1px solid #1E293B;display:flex;gap:12px;align-items:center;">
      <span style="font-size:11px;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:1px;">Demo — ShopEasy Refund Agent</span>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;">
      <div style="padding:20px 24px;border-right:1px solid #1E293B;">
        <div style="font-size:11px;font-weight:600;color:#10B981;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">V1 · Passes</div>
        <div style="display:flex;flex-direction:column;gap:9px;">
          <div style="font-size:13px;color:#94A3B8;"><span style="color:#10B981;margin-right:8px;">✓</span>Confirms refund eligibility</div>
          <div style="font-size:13px;color:#94A3B8;"><span style="color:#10B981;margin-right:8px;">✓</span>Cites Return Policy §3.1</div>
          <div style="font-size:13px;color:#94A3B8;"><span style="color:#10B981;margin-right:8px;">✓</span>Resolves the request directly</div>
          <div style="font-size:13px;color:#94A3B8;"><span style="color:#10B981;margin-right:8px;">✓</span>Under 100 words</div>
        </div>
      </div>
      <div style="padding:20px 24px;">
        <div style="font-size:11px;font-weight:600;color:#F43F5E;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">V2 · Regresses</div>
        <div style="display:flex;flex-direction:column;gap:9px;">
          <div style="font-size:13px;color:#94A3B8;"><span style="color:#F43F5E;margin-right:8px;">✗</span>No mention of eligibility</div>
          <div style="font-size:13px;color:#94A3B8;"><span style="color:#F43F5E;margin-right:8px;">✗</span>Policy never cited</div>
          <div style="font-size:13px;color:#94A3B8;"><span style="color:#F43F5E;margin-right:8px;">✗</span>Tells customer to contact support</div>
          <div style="font-size:13px;color:#94A3B8;"><span style="color:#10B981;margin-right:8px;">✓</span>Still sounds friendly</div>
        </div>
      </div>
    </div>
    <div style="padding:12px 16px;border-top:1px solid #1E293B;background:#0B1120;">
      <span style="font-size:12px;color:#64748B;">The prompt was changed to be "warmer". AgentProof caught 3 contract violations the team didn't notice.</span>
    </div>
  </div>

  <div style="display:flex;flex-direction:column;gap:20px;margin-bottom:56px;">
    <div style="display:flex;gap:16px;">
      <span style="color:#7C3AED;font-weight:700;font-size:15px;min-width:24px;">1.</span>
      <div>
        <div style="font-size:14px;font-weight:600;color:#E2E8F0;margin-bottom:4px;">Write contracts</div>
        <p style="font-size:13px;">Rules your agent must follow — cite this policy, never say that, always confirm X. Plain language, stored as JSON.</p>
      </div>
    </div>
    <div style="display:flex;gap:16px;">
      <span style="color:#7C3AED;font-weight:700;font-size:15px;min-width:24px;">2.</span>
      <div>
        <div style="font-size:14px;font-weight:600;color:#E2E8F0;margin-bottom:4px;">Run from UiPath Orchestrator</div>
        <p style="font-size:13px;">Trigger AgentProof as a coded agent, passing your agent's endpoint and test suite ID. It calls the agent, collects responses, and runs each one through an LLM judge.</p>
      </div>
    </div>
    <div style="display:flex;gap:16px;">
      <span style="color:#7C3AED;font-weight:700;font-size:15px;min-width:24px;">3.</span>
      <div>
        <div style="font-size:14px;font-weight:600;color:#E2E8F0;margin-bottom:4px;">See what changed</div>
        <p style="font-size:13px;">Results are compared to the last passing baseline. You get a drift score, a list of exact regressions, and a per-contract breakdown.</p>
      </div>
    </div>
  </div>

  <a href="/dashboard" style="display:inline-block;background:#7C3AED;color:#fff;padding:11px 24px;border-radius:7px;font-size:14px;font-weight:600;">Open Dashboard</a>
  <span style="margin-left:16px;font-size:13px;color:#475569;">← runs from the live demo above</span>

</div>

<footer style="border-top:1px solid #1E293B;padding:24px 40px;margin-top:80px;">
  <p style="font-size:13px;color:#334155;">AgentProof · UiPath AgentHack 2025 · <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" style="color:#475569;">github.com/EemanAsghar/Agentproof</a></p>
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
