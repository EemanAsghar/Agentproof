import sys
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
      <tbody>{rows if rows else '<tr><td colspan="6" style="padding:40px;text-align:center;color:#475569;">No runs yet.</td></tr>'}</tbody>
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
  <a href="/" style="background:#1E293B;border-radius:8px;padding:6px 14px;font-size:13px;color:#94A3B8;text-decoration:none;">← Back</a>
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
