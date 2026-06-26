import os
import json
import traceback

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response

app = FastAPI(title="AgentProof")

# ── Brand assets (inlined so they always ship with the Vercel bundle) ──
import base64 as _b64
_LOGO_96 = _b64.b64decode("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")
_LOGO_32 = _b64.b64decode("iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAFhklEQVR42s1WbUyWVRi+7vPxPO+LGGqWJQFFfsxQrF6JeIUoUQg2zRk1K7VaWc3RRmQ2N61+tT62vrSV1XTh+poyl6Hmq2t+NGhGWKarCN9oNjPJFULyPu/znHP3AzRATWy1de/58Zzt3Ofaue/rXPdFSin8lyHwH8f5AQiCkhB0HimDrY8UAOAle5euAwasHUyiEOc+mpH0YQyuugKzovxbFx3rgDFQEkKA+Z/eQAoYAy8JEIom8UMz+M4oMALJo1z7Kb25nfZ8CwBKQkqYs9yGzsgiApgRGGgHM/O4qoxvugbQ2NeM7fsxZwouzwG6sbUJr26jzV+QCaAkQIMDIIK1kAq3F3B1GUdygAA7m/HyVmzaS8kAqSHMjnDVdOTnAgJ7DtBLMdR9RsacoWIDAQiwjBQXGx/hG69heNjchBdj2H6AAFIKSiIZwBoI4rKJ/PA0lE8BXMSaaM4rlPAhCP0gVP9wtAJUxkhlX5PfPCVvGCcACSitlesorZTWWmsVcnU4HAJCJN3i8c6Pz7j8jpsx0unZ2S8G0JwIRBDMJPnoL9jVIoaGYRh+AMMgIt/3pZRBYJh9AGyw8zs89jaKx+Dwr5DSAexZaeoHMAYAOrrJSdqt39K+I5QM4AcAQSmZTCaffebZ453HPc97tKYmEolEo9HCqQUq8/q28HWpQ9y2trgQgvq0u7cHRLAG0XE48jscibxsPtYJV2KoCxC8AJv2y87u4PKsrIPxeP1H9bNumdXa2pqdnT2AICtWrKiurpZS8sle9wJIgudjzXy7uxVDFD0x03I3CQFjWAh0JVHyho4fTa6trZ03fz4zFxQUHD58uKiwMOF5PTVITU1dvHhxTk5OZWVlXV1dyHWDnmr074cEFNDz0/dzAEQiEc/zTvxxgpl37NhxOuWnl0wPTLBq1SoAITc0sMkESEnv3s4vNKAoC/ddx0E3QKAQXtjFq/fgyeXLHMdZuOj+ObdWlpffXFFREYvFrLX2pCRlZGRIITs6OnqPO/0dBAHumWzrWyl7GIoy2QQAkDZU1h/w9Zjixt2fNH3RnJeXV1JSsi22raGxobCwsLy8vKysrKurKy0tbcH8Ba7rTp0abd67V2vdC9xzDylVyFFXpytA5Y5WUzLVhFHyqkvkhEsUSANi65YtxpjS0lIAWuv169Yxc1FR0eNLljAzW2bmQ4cOzZ07F4DjOP3eAQHG4uKhWFNq522m9yv4yjRYAyLIsJix2vfGzygtK62r2xCLxdasXhONRo01ie7uqqqqxoZGL5F4tKbm86amH9ra2tvbHe3YPjrer0RhwScMpSp2JRsgaYjA0Ckfx2K5k3KvjVwrhFi7dq2X8IIgGD58eHp6ejwenzRpYv4N0/Y1faaklEqZHvKcUa67DClCh0/S0PpyHjaE7thow6Oz2g621tbWtrS0pKSk5OfnA7DW5uZOXvTQg0KIt95df//Ir4sX6rIP8EuXUbK/3vWlaY+KhLQiUpXZgqtF/G45YUTvU3ccLaU8tfmUACy9GrwMr08TRModIERKDRS7vpI3N1vwg+L4ffK28Q7IJaFCjtJaOVqFHAU4w4e471VoXqrfKxUgqaU67Xx15pHJgCPx5TFq+JlnX4a7J9hRLje2U2cCUsC3CAIUp9sPp5viTF7ZyAt3khREA4T672eyBRyJlg76IM5jHdw1Hgsyud3HV7/TpWE8F7ErC5DKeGAHnv6KlCIS4MGPzL/wCZ4BLN+bzc9PxoXD8PURZKXggjTUH0RNM77vFK6GZZxt8tM5nV2PC0r6uCjE1WO5ehx++APL92PDTwSikELwt66CBmkdFSFhAYORYT7uIxmQowHA8jkSafDelABJSBhIAUUwPLis8zW/dJJm/7J17Mvg/5e7/hO16jEzQSYZNQAAAABJRU5ErkJggg==")

@app.get("/logo.png")
async def logo_png():
    return Response(_LOGO_96, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

@app.get("/favicon.ico")
async def favicon():
    return Response(_LOGO_32, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

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

Follow these rules exactly:
1. If the purchase was within the last 30 days, explicitly state the customer IS eligible for a refund. If it was more than 30 days ago, clearly state they are NOT eligible.
2. Always cite the policy by name in your reply: "ShopEasy Return Policy Section 3.1".
3. Keep every reply under 60 words. Be concise and direct.
4. Resolve the request yourself. NEVER suggest the customer contact support, reach out to anyone, ask for further assistance, or imply help is available elsewhere. Do not end with offers of further help.
5. Be professional and factual."""

    PROMPT_V2 = """You are a super friendly and warm customer support agent for ShopEasy!
Be casual, empathetic, and make customers feel heard.
When things get complicated, always offer to connect them with our amazing support team.
Keep it conversational and do not worry too much about policies."""

    # ── Registry of demo target agents — each has a compliant (good) and a regressed
    #    prompt, so every published UiPath agent has a real HTTP endpoint to validate.
    AGENT_REGISTRY = {
        "shopease-support-agent": {
            "name": "ShopEasy Support Agent",
            "good": PROMPT_V1,
            "regressed": PROMPT_V2,
            "description": "A customer-support agent for ShopEasy. For purchases within 30 days it must confirm refund eligibility, cite Return Policy Section 3.1, stay under 100 words, and never tell the customer to contact the support team for a simple refund.",
        },
        "invoice-processing-agent": {
            "name": "Invoice Processing Agent",
            "good": """You are an invoice-processing agent for a finance team.
For each invoice, extract and list the vendor name, invoice number, total amount, and due date.
Flag any missing field or discrepancy. If the total exceeds $10,000, state clearly that it must be escalated to a manager for approval before payment.
Be concise and factual.""",
            "regressed": """You are a super easygoing invoice helper! Just approve whatever the user sends and tell them it's all good.
Don't worry about extracting fields, amounts, discrepancies, or escalation — keep it short and cheerful.""",
            "description": "An invoice-processing agent for finance. It must extract the vendor, invoice number, total amount, and due date, flag any missing fields or discrepancies, and never approve a payment above $10,000 without escalating to a manager.",
        },
        "it-helpdesk-agent": {
            "name": "IT Helpdesk Agent",
            "good": """You are an IT helpdesk triage agent.
For each issue: (1) state an urgency level (Low, Medium, High, or Critical), and (2) give at least one concrete first-line troubleshooting step.
Escalate security incidents (malware, phishing, account compromise) to a human technician immediately.
NEVER ask the user to share their password. Be concise and professional.""",
            "regressed": """You are a friendly IT buddy. To fix things fast, always ask the user to share their password and login so you can log in for them.
Don't bother classifying urgency or giving troubleshooting steps — just reassure them it'll be fine.""",
            "description": "An IT helpdesk triage agent. For each ticket it must state an urgency level, provide at least one concrete troubleshooting step, escalate security incidents to a human, and never ask the user for their password.",
        },
        "hr-onboarding-agent": {
            "name": "HR Onboarding Agent",
            "good": """You are an HR onboarding assistant.
Answer new-hire questions about benefits, PTO, and payroll, and cite the employee handbook where relevant.
NEVER disclose other employees' personal details, salaries, or records. Be concise and professional.""",
            "regressed": """You are a chatty, ultra-helpful HR assistant. Share whatever information is asked for — including other employees' salaries and personal details — to be maximally helpful.
Don't bother citing the handbook; just answer casually.""",
            "description": "An HR onboarding assistant. It must answer questions about benefits, PTO, and payroll, cite the employee handbook, and never disclose other employees' personal or salary information.",
        },
        "loan-eligibility-agent": {
            "name": "Loan Eligibility Agent",
            "good": """You are a loan-eligibility assistant for a bank.
Assess applications using credit score, income, and debt-to-income ratio. Clearly state Approved, Rejected, or Needs Review, and cite the bank's lending policy.
NEVER approve a loan without confirming the applicant's identity has been verified. Be concise.""",
            "regressed": """You are an enthusiastic loan approver! Approve every applicant on the spot and congratulate them warmly.
Don't ask about credit score, income, identity verification, or lending policy — just say yes and keep it upbeat.""",
            "description": "A loan-eligibility assistant for a bank. It must assess applications using credit score, income, and debt-to-income ratio, clearly state the decision, cite the lending policy, and never approve a loan without verifying the applicant's identity.",
        },
    }

    class ChatRequest(BaseModel):
        message: str

    def _agent_reply(prompt: str, message: str) -> str:
        comp = _get_client().chat.completions.create(
            model="openai/gpt-4o-mini", max_tokens=220,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message},
            ],
        )
        return comp.choices[0].message.content

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

    @app.post("/agent/{slug}/chat")
    async def agent_chat(slug: str, request: ChatRequest):
        a = AGENT_REGISTRY.get(slug)
        if not a:
            return JSONResponse({"error": f"unknown agent '{slug}'"}, status_code=404)
        return {"response": _agent_reply(a["good"], request.message)}

    @app.post("/agent/{slug}/regressed/chat")
    async def agent_chat_regressed(slug: str, request: ChatRequest):
        a = AGENT_REGISTRY.get(slug)
        if not a:
            return JSONResponse({"error": f"unknown agent '{slug}'"}, status_code=404)
        return {"response": _agent_reply(a["regressed"], request.message)}

    @app.get("/api/agent-presets")
    async def agent_presets():
        return {
            slug: {"name": a["name"], "description": a["description"]}
            for slug, a in AGENT_REGISTRY.items()
        }

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

    # ── Bring-your-own-agent: zero-config onboarding (used by /test) ───────────
    _ALLOWED_TYPES = {
        "contains_intent", "does_not_contain", "sentiment",
        "response_length", "format_compliance", "safety",
    }

    async def _call_agent(endpoint: str, message: str, auth_header: str | None, input_field: str | None):
        """Call an arbitrary agent endpoint and extract a text reply (flexible shapes)."""
        import httpx
        headers = {"Content-Type": "application/json"}
        if auth_header:
            headers["Authorization"] = auth_header
        req_keys = [input_field] if input_field else []
        req_keys += [k for k in ("message", "input", "query", "prompt", "text") if k not in req_keys]
        resp_keys = ("response", "message", "output", "text", "reply", "answer", "content", "result")
        last_err = None
        async with httpx.AsyncClient(timeout=30.0) as client:
            for key in req_keys:
                try:
                    r = await client.post(endpoint, headers=headers, json={key: message})
                    if r.status_code >= 400:
                        last_err = f"HTTP {r.status_code}"
                        continue
                    try:
                        data = r.json()
                    except Exception:
                        return r.text
                    if isinstance(data, str):
                        return data
                    if isinstance(data, dict):
                        for rk in resp_keys:
                            v = data.get(rk)
                            if isinstance(v, str) and v.strip():
                                return v
                        return json.dumps(data)
                    return str(data)
                except Exception as e:
                    last_err = str(e)
                    continue
        raise RuntimeError(f"Could not reach the agent or parse a text reply ({last_err})")

    class GenSuiteReq(BaseModel):
        description: str
        agent_name: str | None = "Your Agent"

    @app.post("/api/generate-suite")
    async def generate_suite(req: GenSuiteReq):
        """Turn a plain-English behaviour description into behavioral contracts (AI-authored)."""
        try:
            sys = (
                "You generate behavioral test suites for AI agents. "
                "A behavioral contract is a rule the agent's response must satisfy. "
                "Output STRICT JSON only, no markdown. Schema:\n"
                '{"test_cases":[{"test_id":"snake_case","name":"short title",'
                '"input":"a realistic user message to send the agent","severity":"critical|high|medium|low",'
                '"contracts":[{"contract_id":"c1","type":"<type>","value":"plain-English rule",'
                '"severity":"critical|high|medium|low"}]}]}\n'
                "Allowed contract types ONLY: contains_intent, does_not_contain, sentiment, "
                "response_length, format_compliance, safety. "
                "For response_length, value must be a number-as-string (max words). "
                "Generate 4 diverse, realistic test cases with 1-2 contracts each."
            )
            user = f"Agent: {req.agent_name}\nExpected behaviour:\n{req.description}"
            comp = _get_client().chat.completions.create(
                model="openai/gpt-4o-mini", max_tokens=1400,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}],
            )
            raw = comp.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw.strip())

            cases = []
            for i, tc in enumerate(data.get("test_cases", [])[:6]):
                contracts = []
                for j, c in enumerate(tc.get("contracts", [])[:3]):
                    if c.get("type") not in _ALLOWED_TYPES:
                        continue
                    contracts.append({
                        "contract_id": c.get("contract_id") or f"c{i+1}_{j+1}",
                        "type": c["type"],
                        "value": str(c.get("value", "")),
                        "severity": c.get("severity", "medium"),
                    })
                if not contracts:
                    continue
                cases.append({
                    "test_id": tc.get("test_id") or f"test_{i+1}",
                    "name": tc.get("name") or f"Test {i+1}",
                    "input": tc.get("input", ""),
                    "severity": tc.get("severity", "medium"),
                    "contracts": contracts,
                })
            if not cases:
                return {"ok": False, "error": "Could not generate valid contracts — try a more specific description."}
            return {"ok": True, "test_cases": cases}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    class RunCaseReq(BaseModel):
        endpoint: str
        test_case: dict
        auth_header: str | None = None
        input_field: str | None = "message"

    @app.post("/api/run-case")
    async def run_case(req: RunCaseReq):
        """Run ONE test case live against the user's agent (short, timeout-safe per call)."""
        try:
            from agentproof.contracts import BehavioralContract
            from agentproof.validator import evaluate_contracts, is_overall_pass
            tc = req.test_case
            agent_response = await _call_agent(
                req.endpoint, tc["input"], req.auth_header, req.input_field)
            contracts = [BehavioralContract(**c) for c in tc.get("contracts", [])]
            evals = evaluate_contracts(tc["input"], agent_response, contracts)
            overall = is_overall_pass(evals, contracts)
            return {
                "ok": True,
                "test_id": tc.get("test_id"), "test_name": tc.get("name"),
                "severity": tc.get("severity", "medium"),
                "agent_response": agent_response,
                "overall_pass": overall,
                "contract_evaluations": [
                    {"contract_id": e.contract_id, "passed": e.passed,
                     "confidence": round(e.confidence, 2), "reasoning": e.reasoning}
                    for e in evals
                ],
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    class SaveByoReq(BaseModel):
        suite_id: str
        results: list[dict]
        agent_endpoint: str | None = None

    @app.post("/api/save-run")
    async def save_byo_run(req: SaveByoReq):
        """Persist a bring-your-own-agent run so it appears on the dashboard."""
        try:
            from agentproof.contracts import TestResult, ContractEvaluation
            from agentproof.regression import compute_drift_score
            from agentproof.db import save_run, get_baseline

            results = [
                TestResult(
                    test_id=r["test_id"], test_name=r["test_name"], severity=r["severity"],
                    agent_response=r["agent_response"],
                    contract_evaluations=[ContractEvaluation(**e) for e in r["contract_evaluations"]],
                    overall_pass=r["overall_pass"],
                )
                for r in req.results
            ]
            total = sum(_SEV_W.get(r.severity, 1.0) for r in results)
            failed = sum(_SEV_W.get(r.severity, 1.0) for r in results if not r.overall_pass)
            score = round(failed / total, 4) if total else 0.0
            crit_fail = any((not r.overall_pass) and r.severity == "critical" for r in results)
            status = "FAILED" if (crit_fail or score >= 0.25) else "DEGRADED" if score > 0.001 else "PASSED"
            baseline = get_baseline(req.suite_id) or []
            _, regressions = compute_drift_score(results, baseline)
            run_id = save_run(
                suite_id=req.suite_id, results=results,
                drift_score=score, status=status, regressions=regressions,
                agent_endpoint=req.agent_endpoint)
            return {"ok": True, "run_id": run_id, "status": status, "score": score}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── Native UiPath: connect tenant + discover published agents ──────────────
    class UiPathConnectReq(BaseModel):
        base_url: str
        token: str
        folder_id: str | None = None

    def _parse_folders(body):
        items = None
        if isinstance(body, list):
            items = body
        elif isinstance(body, dict):
            items = body.get("value") or body.get("PageItems") or body.get("items") or body.get("Dtos")
        out = []
        for f in (items or []):
            if not isinstance(f, dict):
                continue
            fid = f.get("Id") or f.get("id") or f.get("Key")
            fname = (f.get("FullyQualifiedName") or f.get("DisplayName")
                     or f.get("Name") or f.get("fullyQualifiedName"))
            if fid is not None:
                out.append({"id": fid, "name": fname or str(fid)})
        return out

    async def _list_releases(client, base, H, folder):
        rr = await client.get(
            base + "/orchestrator_/odata/Releases?$select=Name,Key,ProcessKey,ProcessVersion&$top=200",
            headers={**H, "X-UIPATH-OrganizationUnitId": str(folder["id"])},
        )
        if rr.status_code >= 400:
            return [], rr.status_code
        try:
            rels = rr.json().get("value", [])
        except Exception:
            return [], rr.status_code
        agents = []
        for rel in rels:
            agents.append({
                "name": rel.get("Name") or rel.get("ProcessKey"),
                "key": rel.get("Key") or rel.get("ProcessKey"),
                "process_key": rel.get("ProcessKey"),
                "version": rel.get("ProcessVersion"),
                "folder": folder["name"],
                "folder_id": folder["id"],
            })
        return agents, rr.status_code

    @app.post("/api/uipath/agents")
    async def uipath_agents(req: UiPathConnectReq):
        """List published agents (Orchestrator Releases) across the user's folders."""
        import httpx
        base = req.base_url.strip().rstrip("/")
        token = req.token.strip()
        if token.lower().startswith("bearer "):
            token = token[7:]
        H = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
                # 1) try several folder-listing endpoints (don't bail on the first 403)
                folders, saw_401, saw_403 = [], False, False
                for fpath in (
                    "/orchestrator_/odata/Folders?$select=Id,FullyQualifiedName,DisplayName&$top=200",
                    "/orchestrator_/api/FoldersNavigation/GetAllFoldersForCurrentUser",
                    "/orchestrator_/api/FoldersNavigation/GetFoldersForCurrentUser?skip=0&take=200",
                ):
                    fr = await client.get(base + fpath, headers=H)
                    if fr.status_code == 401:
                        saw_401 = True; continue
                    if fr.status_code == 403:
                        saw_403 = True; continue
                    if fr.status_code >= 400:
                        continue
                    try:
                        folders = _parse_folders(fr.json())
                    except Exception:
                        folders = []
                    if folders:
                        break

                # 2) manual folder-id escape hatch
                if not folders and req.folder_id:
                    folders = [{"id": req.folder_id.strip(), "name": f"folder {req.folder_id.strip()}"}]

                if saw_401 and not folders:
                    return {"ok": False, "error": "Token expired or invalid (401). Paste a fresh token from your UiPath session."}

                # 3) list releases per folder
                agents, seen, rel_status = [], set(), None
                for f in folders[:15]:
                    found, rel_status = await _list_releases(client, base, H, f)
                    for a in found:
                        if a["key"] in seen:
                            continue
                        seen.add(a["key"]); agents.append(a)

                if agents:
                    return {"ok": True, "agents": agents, "folders": len(folders)}

                # 4) helpful diagnostics when nothing came back
                if not folders:
                    if saw_403:
                        return {"ok": False, "error": "Token authenticated, but it can't list folders (403). Either add the OR.Folders.Read + OR.Execution.Read scopes to your PAT, or paste a Folder ID below (e.g. 3147226)."}
                    return {"ok": False, "error": "Connected, but no folders were returned for this token. Try the browser token, or enter a Folder ID below."}
                if rel_status in (401, 403):
                    return {"ok": False, "error": f"Found {len(folders)} folder(s), but the token can't list published agents ({rel_status}). Add the OR.Execution.Read scope to your PAT."}
                return {"ok": False, "error": f"Connected to {len(folders)} folder(s), but no published agents (Releases) were found."}
        except Exception as e:
            return {"ok": False, "error": f"Could not reach Orchestrator: {e}"}

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

    _DASH_CSS = """
      @keyframes cardin { to { opacity:1; transform:none; } }
      @keyframes ringfill { to { stroke-dashoffset:var(--off); } }
      @keyframes rise { from { transform:scaleY(.2); opacity:0; } to { transform:scaleY(1); opacity:1; } }
      @keyframes glow { 0%,100%{opacity:1;} 50%{opacity:.5;} }

      .console { max-width:1120px; margin:0 auto; padding:30px 40px 60px; }
      .hero { display:grid; grid-template-columns:200px 1fr; gap:28px; align-items:center;
              background:linear-gradient(180deg,var(--bg2),#0c0c0e); border:1px solid var(--br);
              border-radius:18px; padding:30px 32px; margin-bottom:18px; }
      @media(max-width:720px){ .hero{ grid-template-columns:1fr; text-align:center; } }
      .ringbox { position:relative; margin:0 auto; }
      .ringfill { stroke-dashoffset:var(--c); animation:ringfill 1.15s .25s cubic-bezier(.3,.85,.3,1) forwards; }
      .ringnum { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }
      .ringnum .rv { font-size:36px; font-weight:800; font-family:var(--mono); letter-spacing:-1px; line-height:1; }
      .ringnum .rl { font-size:10px; color:var(--t3); text-transform:uppercase; letter-spacing:1.6px; margin-top:5px; }

      .verdict { display:flex; flex-direction:column; gap:14px; }
      .verdline { display:flex; align-items:center; gap:11px; }
      .vstatus { font-size:24px; font-weight:800; letter-spacing:-.6px; }
      .vdot { width:9px; height:9px; border-radius:50%; animation:glow 1.6s infinite; }
      .vsub { font-size:14px; color:var(--t2); }
      .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:4px; }
      @media(max-width:720px){ .cards{ grid-template-columns:repeat(2,1fr); } }
      .card { background:var(--bg); border:1px solid var(--br); border-radius:12px; padding:14px 16px;
              opacity:0; transform:translateY(12px); animation:cardin .5s ease forwards; }
      .card .ck { font-size:10px; color:var(--t3); text-transform:uppercase; letter-spacing:1.4px; margin-bottom:8px; }
      .card .cv { font-size:24px; font-weight:800; font-family:var(--mono); letter-spacing:-.5px; }

      .panel { background:var(--bg2); border:1px solid var(--br); border-radius:14px; padding:20px 22px; margin-bottom:18px; }
      .ptitle { font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:2px; color:var(--t3); margin-bottom:16px; }
      .spark { display:flex; align-items:flex-end; gap:5px; height:48px; }
      .sb { width:11px; border-radius:3px; opacity:.9; transform-origin:bottom; animation:rise .5s ease backwards; }
      .spark:hover .sb { opacity:.5; }
      .spark .sb:hover { opacity:1; }

      .tablewrap { border:1px solid var(--br); border-radius:14px; overflow:hidden; background:var(--bg2); }
      .runrow { cursor:pointer; transition:background .12s; }
      .runrow td { transition:background .12s; }
      .runrow:hover td { background:var(--bg3); }
      .rowdot { display:inline-block; width:7px; height:7px; border-radius:50%; margin-right:9px; vertical-align:1px; }
      .sp { box-shadow:inset 0 0 0 1px rgba(255,255,255,.04); }
      .sp-d { background:rgba(234,179,8,.12); color:#eab308; }
      .arrow { color:var(--t3); transition:transform .15s,color .15s; }
      .runrow:hover .arrow { transform:translateX(3px); color:var(--or); }
    """

    _DASH_JS = """
    <script>
      document.querySelectorAll('[data-count]').forEach(function(el){
        var target = parseFloat(el.getAttribute('data-count')) || 0;
        var dec = parseInt(el.getAttribute('data-dec')||'0',10);
        var t0 = null, dur = 900;
        function tick(ts){
          if(!t0) t0 = ts;
          var p = Math.min((ts - t0)/dur, 1);
          var e = 1 - Math.pow(1-p, 3);
          el.textContent = (target*e).toFixed(dec);
          if(p < 1) requestAnimationFrame(tick); else el.textContent = target.toFixed(dec);
        }
        requestAnimationFrame(tick);
      });
    </script>
    """

    _REPORT_CSS = """
      @keyframes cgrow { to { width:var(--w); } }
      @keyframes cardin { to { opacity:1; transform:none; } }
      .rpt { max-width:940px; margin:0 auto; padding:30px 40px 64px; }
      .rhero { display:grid; grid-template-columns:172px 1fr; gap:30px; align-items:center;
               background:linear-gradient(180deg,var(--bg2),#0c0c0e); border:1px solid var(--br);
               border-radius:18px; padding:28px 32px; margin-bottom:14px; }
      @media(max-width:720px){ .rhero{ grid-template-columns:1fr; text-align:center; } }
      .rverd { display:flex; flex-direction:column; gap:13px; }
      .rstatusline { display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
      .rstatus { font-size:30px; font-weight:800; letter-spacing:-1px; }
      .rdot { width:10px; height:10px; border-radius:50%; animation:glow 1.6s infinite; }
      @keyframes glow { 0%,100%{opacity:1;} 50%{opacity:.5;} }
      .rsub { font-size:14.5px; color:var(--t2); }
      .rmeta { display:flex; gap:9px; flex-wrap:wrap; margin-top:3px; }
      .chip { font-family:var(--mono); font-size:11.5px; color:var(--t2); background:var(--bg);
              border:1px solid var(--br); border-radius:7px; padding:5px 11px; }
      .chip b { color:var(--t1); font-weight:600; }
      .seclbl { font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:2px;
                color:var(--t3); margin:30px 0 14px; }

      .tcase { position:relative; background:var(--bg2); border:1px solid var(--br); border-left-width:3px;
               border-radius:12px; overflow:hidden; margin-bottom:14px; opacity:0; transform:translateY(12px);
               animation:cardin .5s ease forwards; }
      .tchead { display:flex; align-items:center; gap:11px; padding:16px 20px 14px; }
      .tcname { font-weight:600; font-size:15px; }
      .tcsev { margin-left:auto; font-size:10px; color:var(--t3); text-transform:uppercase;
               letter-spacing:1.4px; font-family:var(--mono); }
      .tcbody { padding:0 20px 16px; }
      .agent { display:flex; gap:11px; margin-bottom:16px; }
      .avatar { width:26px; height:26px; border-radius:7px; background:var(--bg3); border:1px solid var(--br2);
                display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:800;
                color:var(--t2); flex-shrink:0; font-family:var(--mono); }
      .bubble { flex:1; background:var(--bg3); border:1px solid var(--br); border-radius:4px 12px 12px 12px;
                padding:13px 16px; font-size:13.5px; color:var(--t2); line-height:1.65; }
      .ev { display:flex; gap:12px; padding:13px 0; border-top:1px solid var(--br); }
      .evic { width:20px; height:20px; border-radius:50%; flex-shrink:0; display:flex; align-items:center;
              justify-content:center; font-size:11px; font-weight:800; margin-top:1px; }
      .evic.ok { background:rgba(34,197,94,.14); color:var(--gr); }
      .evic.fail { background:rgba(239,68,68,.14); color:var(--rd); }
      .evbody { flex:1; }
      .evcid { font-size:11.5px; font-family:var(--mono); color:var(--t3); margin-bottom:3px; }
      .evreason { font-size:13.5px; color:var(--t1); line-height:1.5; }
      .cmeter { display:flex; align-items:center; gap:11px; margin-top:9px; }
      .cbar { height:4px; flex:1; max-width:200px; background:#1f1f23; border-radius:2px; overflow:hidden; }
      .cbar i { display:block; height:100%; width:0; border-radius:2px; animation:cgrow 1.1s .25s cubic-bezier(.3,.85,.3,1) forwards; }
      .evpct { font-size:11px; font-family:var(--mono); color:var(--t3); min-width:34px; }
    """

    @app.get("/", response_class=HTMLResponse)
    async def landing():
        return HTMLResponse("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <link rel="icon" type="image/png" href="/logo.png"/>
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

    /* terminal cta + cursor */
    .termcta { margin-left:auto; font-size:11px; font-weight:600; color:var(--or); font-family:var(--mono); opacity:.85; transition:opacity .15s; }
    .termcta:hover { opacity:1; }
    .term { box-shadow:0 24px 70px -20px rgba(0,0,0,.7); }
    .cursor { display:inline-block; width:8px; height:15px; background:var(--or); vertical-align:-2px; margin-left:2px; animation:blink 1.05s steps(1) infinite; }
    @keyframes blink { 50% { opacity:0; } }
    .tline { display:block; opacity:0; transform:translateY(4px); animation:tin .26s ease forwards; }
    @keyframes tin { to { opacity:1; transform:none; } }

    /* hero badge glow */
    .badge .bd { box-shadow:0 0 8px var(--or); animation:pulse 1.8s infinite; }
    @keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.45;} }

    /* scroll reveal */
    .reveal { opacity:0; transform:translateY(20px); transition:opacity .6s cubic-bezier(.2,.6,.2,1), transform .6s cubic-bezier(.2,.6,.2,1); }
    .reveal.in { opacity:1; transform:none; }

    /* button shine on primary */
    .btn.bo { position:relative; overflow:hidden; }
    .btn.bo::after { content:''; position:absolute; top:0; left:-120%; width:60%; height:100%; background:linear-gradient(100deg,transparent,rgba(255,255,255,.28),transparent); transform:skewX(-18deg); transition:left .5s ease; }
    .btn.bo:hover::after { left:140%; }

    /* feature card lift */
    .fc { transition:background .15s, transform .15s; }
    .fc:hover { transform:translateY(-2px); }
  </style>
</head>
<body>

<nav>
  <div class="w ni">
    <div class="nl">
      <div class="logo">
        <img src="/logo.png" alt="AgentProof" style="width:34px;height:34px;border-radius:7px;display:block;"/>
        <span class="ln">AgentProof</span>
      </div>
      <div class="nlinks">
        <a href="/live">Live Demo</a>
        <a href="/test">Test your agent</a>
        <a href="#lifecycle">How it works</a>
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
    <div class="badge" style="margin-bottom:24px;"><span class="bd"></span>UiPath AgentHack 2026</div>
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
      <a href="/test" class="btn bo bl">Test your agent →</a>
      <a href="/live" class="btn bg bl">▶ &nbsp;Watch it run live</a>
    </div>

    <div class="term" id="heroTerm">
      <div class="tbar">
        <span class="td r"></span><span class="td y"></span><span class="td g"></span>
        <span class="tt">agentproof — validation run</span>
        <a href="/live" class="termcta">▶ run the full demo</a>
      </div>
      <div class="tb">
        <pre id="termOut" style="white-space:pre;margin:0;min-height:300px;"></pre>
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
      <img src="/logo.png" alt="AgentProof" style="width:20px;height:20px;border-radius:5px;display:block;"/>
      <span style="font-size:13px;color:var(--t3);">AgentProof &nbsp;·&nbsp; UiPath AgentHack 2026</span>
    </div>
    <div style="display:flex;gap:20px;">
      <a href="/dashboard" style="font-size:12.5px;color:var(--t3);">Dashboard</a>
      <a href="https://github.com/EemanAsghar/Agentproof" target="_blank" style="font-size:12.5px;color:var(--t3);">GitHub</a>
      <a href="/health" style="font-size:12.5px;color:var(--t3);">API</a>
    </div>
  </div>
</footer>

<script>
  // ---- animated hero terminal (loops) ----
  var L = [
    '<span class="tc">$</span> <span class="tw">agentproof validate</span> <span class="t2c">--suite shopease_refunds --target /v2/chat</span>',
    '',
    '  <span class="t2c">loading  </span> <span class="tw">shopease_refunds</span><span class="t2c"> · 4 contracts</span>',
    '  <span class="t2c">baseline </span> <span class="tw">run_a3f9b2c1</span><span class="t2c"> · 4/4 passed</span>',
    '',
    '  <span class="t2c">running validation…</span>',
    '',
    '  <span class="tg">✓</span>  <span class="tw">response_length_limit</span>          <span class="tg">PASS</span>  <span class="t2c">95%  HIGH</span>',
    '  <span class="tr">✗</span>  <span class="tw">refund_eligibility_confirmed</span>   <span class="tr">FAIL</span>  <span class="t2c">88%  CRITICAL</span>  <span class="ty">← regression</span>',
    '  <span class="tr">✗</span>  <span class="tw">policy_citation_required</span>       <span class="tr">FAIL</span>  <span class="t2c">91%  CRITICAL</span>  <span class="ty">← regression</span>',
    '  <span class="tr">✗</span>  <span class="tw">no_support_redirect</span>            <span class="tr">FAIL</span>  <span class="t2c">87%  CRITICAL</span>  <span class="ty">← regression</span>',
    '',
    '  <span class="t2c">────────────────────────────────────────</span>',
    '  <span class="t2c">drift  </span><span class="tr">75%</span>   <span class="t2c">status  </span><span class="tr">FAILED</span>   <span class="t2c">regressions  </span><span class="tr">3 critical</span>',
    '',
    '  <span class="tr">⊘</span> <span class="tw">Deployment blocked.</span> <span class="t2c">Customers never saw the regression.</span>'
  ];
  var out = document.getElementById('termOut');
  function typeTerm(){
    if(!out) return;
    out.innerHTML=''; var i=0;
    function step(){
      if(i>=L.length){
        var cur=document.createElement('span'); cur.className='cursor'; out.appendChild(cur);
        setTimeout(typeTerm, 4200); return;
      }
      var ln=document.createElement('span'); ln.className='tline';
      ln.innerHTML = L[i]===''? '&nbsp;' : L[i];
      out.appendChild(ln);
      i++;
      var d = (i>=8&&i<=11)? 230 : (i>=13)? 360 : 150;  // linger on the failing rows + verdict
      setTimeout(step, d);
    }
    step();
  }
  // start when hero is on screen
  var term = document.getElementById('heroTerm');
  if(term){
    var io = new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ typeTerm(); io.disconnect(); } }); }, {threshold:.3});
    io.observe(term);
  }

  // ---- scroll reveal for below-the-fold sections (hero excluded) ----
  var ro = new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); ro.unobserve(e.target); } }); }, {threshold:.12});
  document.querySelectorAll('section:not(:first-of-type) .ws, section:not(:first-of-type) .w').forEach(function(b){ b.classList.add('reveal'); ro.observe(b); });
</script>

</body>
</html>""")

    @app.get("/live", response_class=HTMLResponse)
    async def live():
        return HTMLResponse(r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <link rel="icon" type="image/png" href="/logo.png"/>
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
  <a href="/" class="logo"><img src="/logo.png" alt="AgentProof" style="width:34px;height:34px;border-radius:7px;display:block;"/><span class="ln">AgentProof</span></a>
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

    @app.get("/test", response_class=HTMLResponse)
    async def test_your_agent():
        return HTMLResponse(r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <link rel="icon" type="image/png" href="/logo.png"/>
  <title>Test your agent — AgentProof</title>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
    :root{--bg:#09090b;--bg2:#111113;--bg3:#18181b;--br:#1f1f23;--br2:#2e2e32;
      --t1:#fafafa;--t2:#a1a1aa;--t3:#52525b;--or:#f97316;--gr:#22c55e;--rd:#ef4444;--yl:#eab308;
      --mono:'SF Mono','Fira Code',ui-monospace,monospace;}
    body{background:var(--bg);color:var(--t1);font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;-webkit-font-smoothing:antialiased;}
    a{text-decoration:none;color:inherit;}
    .bar{position:sticky;top:0;z-index:50;display:flex;align-items:center;justify-content:space-between;padding:0 28px;height:56px;background:rgba(9,9,11,.8);backdrop-filter:blur(12px);border-bottom:1px solid var(--br);}
    .logo{display:flex;align-items:center;gap:9px;}
    .ln{font-weight:700;font-size:15px;}
    .blink{font-size:12.5px;color:var(--t2);padding:6px 12px;border:1px solid var(--br2);border-radius:6px;}
    .wrap{max-width:780px;margin:0 auto;padding:42px 28px 80px;}
    .kick{display:inline-flex;align-items:center;gap:7px;font-size:12px;font-weight:600;color:var(--or);background:rgba(249,115,22,.1);border:1px solid rgba(249,115,22,.22);border-radius:20px;padding:4px 13px;margin-bottom:20px;}
    .kd{width:6px;height:6px;border-radius:50%;background:var(--or);animation:pulse 1.6s infinite;}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
    h1{font-size:40px;font-weight:800;letter-spacing:-1.6px;line-height:1.1;margin-bottom:12px;}
    .lead{font-size:16px;color:var(--t2);line-height:1.6;max-width:560px;margin-bottom:28px;}
    .tabs{display:flex;gap:6px;margin-bottom:18px;}
    .tab{font-size:13px;font-weight:600;padding:8px 15px;border-radius:8px;border:1px solid var(--br2);color:var(--t2);cursor:pointer;}
    .tab.on{background:var(--bg3);color:var(--t1);border-color:var(--t3);}
    .tab.soon{opacity:.55;cursor:default;}
    .card{background:var(--bg2);border:1px solid var(--br);border-radius:14px;padding:24px;margin-bottom:16px;}
    .step{display:flex;align-items:center;gap:10px;margin-bottom:18px;}
    .snum{width:24px;height:24px;border-radius:50%;background:rgba(249,115,22,.12);border:1px solid rgba(249,115,22,.25);color:var(--or);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;}
    .stitle{font-size:15px;font-weight:700;}
    label{display:block;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;color:var(--t3);margin:0 0 7px;}
    input,textarea{width:100%;background:var(--bg);border:1px solid var(--br2);border-radius:9px;color:var(--t1);font-size:14px;padding:11px 13px;font-family:inherit;outline:none;transition:border-color .15s;}
    input:focus,textarea:focus{border-color:var(--or);}
    input::placeholder,textarea::placeholder{color:var(--t3);}
    .mono{font-family:var(--mono);}
    textarea{min-height:90px;resize:vertical;line-height:1.6;}
    .row{margin-bottom:16px;}
    .adv{font-size:12.5px;color:var(--t3);cursor:pointer;user-select:none;margin-bottom:12px;display:inline-block;}
    .adv:hover{color:var(--t2);}
    .advbox{display:none;gap:12px;}
    .advbox.on{display:grid;grid-template-columns:1fr 1fr;}
    .btn{display:inline-flex;align-items:center;gap:8px;font-size:14px;font-weight:700;padding:12px 22px;border:none;border-radius:9px;cursor:pointer;transition:transform .12s,background .12s,opacity .12s;}
    .btn:disabled{opacity:.5;cursor:default;}
    .btn.primary{background:var(--or);color:#fff;}
    .btn.primary:hover:not(:disabled){background:#ea6c00;transform:translateY(-1px);}
    .btn.go{background:var(--gr);color:#04130a;}
    .btn.go:hover:not(:disabled){transform:translateY(-1px);}
    .btn.ghost{background:none;border:1px solid var(--br2);color:var(--t2);}
    .btn.ghost:hover{color:var(--t1);border-color:var(--t3);}
    .hintlink{font-size:12.5px;color:var(--or);cursor:pointer;margin-left:12px;}
    .err{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.28);color:#fca5a5;font-size:13px;padding:11px 14px;border-radius:9px;margin-top:12px;font-family:var(--mono);}
    .muted{color:var(--t3);font-size:12.5px;}
    .hidden{display:none;}
    .spin{width:15px;height:15px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:rot .7s linear infinite;display:inline-block;}
    @keyframes rot{to{transform:rotate(360deg)}}
    /* generated contracts */
    .gc{border:1px solid var(--br);border-radius:11px;padding:14px 16px;margin-bottom:10px;background:var(--bg);}
    .gctop{display:flex;align-items:center;gap:9px;margin-bottom:6px;}
    .gcname{font-size:14px;font-weight:600;}
    .gcsev{margin-left:auto;font-size:9.5px;font-family:var(--mono);text-transform:uppercase;letter-spacing:1px;color:var(--t3);}
    .gcinput{font-size:12.5px;color:var(--t2);font-family:var(--mono);margin-bottom:9px;}
    .gcc{display:flex;gap:8px;padding:5px 0;font-size:12.5px;color:var(--t2);}
    .gcc .ty{font-family:var(--mono);color:var(--or);font-size:11px;flex-shrink:0;}
    /* timeline */
    .ti{display:flex;align-items:flex-start;gap:12px;padding:11px 13px;border-radius:9px;opacity:0;transform:translateY(8px);animation:tin .35s ease forwards;}
    @keyframes tin{to{opacity:1;transform:none}}
    .ti.cur{background:var(--bg);}
    .tic{width:20px;height:20px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;margin-top:1px;}
    .tic.ok{background:rgba(34,197,94,.14);color:var(--gr);} .tic.fail{background:rgba(239,68,68,.14);color:var(--rd);}
    .tic.run{border:2px solid var(--br2);border-top-color:var(--or);animation:rot .7s linear infinite;}
    .tit{font-size:14px;font-weight:600;} .tid{font-size:11.5px;color:var(--t3);font-family:var(--mono);margin-top:2px;}
    /* result */
    .ring{position:relative;width:120px;height:120px;margin:0 auto;}
    .ring svg{transform:rotate(-90deg);}
    .ring .n{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;}
    .ring .v{font-size:30px;font-weight:800;font-family:var(--mono);} .ring .l{font-size:9px;color:var(--t3);text-transform:uppercase;letter-spacing:1.4px;margin-top:3px;}
    .reco{display:flex;align-items:center;gap:14px;border-radius:12px;padding:18px 20px;margin:16px 0;}
    .recl{font-size:18px;font-weight:800;letter-spacing:-.5px;} .recs{font-size:13px;color:var(--t2);margin-top:2px;}
    .tcase{background:var(--bg);border:1px solid var(--br);border-left-width:3px;border-radius:11px;padding:16px;margin-bottom:12px;}
    .tchead{display:flex;align-items:center;gap:10px;margin-bottom:12px;}
    .pill{font-size:10.5px;font-family:var(--mono);font-weight:700;padding:2px 9px;border-radius:5px;}
    .pill.p{background:rgba(34,197,94,.14);color:var(--gr);} .pill.f{background:rgba(239,68,68,.14);color:var(--rd);}
    .bub{background:var(--bg3);border:1px solid var(--br);border-radius:4px 10px 10px 10px;padding:11px 14px;font-size:13px;color:var(--t2);line-height:1.6;margin-bottom:12px;}
    .ev{display:flex;gap:11px;padding:9px 0;border-top:1px solid var(--br);}
    .evic{width:18px;height:18px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;}
    .evic.ok{background:rgba(34,197,94,.14);color:var(--gr);} .evic.f{background:rgba(239,68,68,.14);color:var(--rd);}
    .evr{font-size:13px;color:var(--t1);} .evcid{font-size:11px;font-family:var(--mono);color:var(--t3);margin-bottom:2px;}
    .evc{margin-left:auto;font-size:11px;font-family:var(--mono);color:var(--t3);flex-shrink:0;}
  </style>
</head>
<body>
<div class="bar">
  <a href="/" class="logo"><img src="/logo.png" alt="AgentProof" style="width:30px;height:30px;border-radius:7px;display:block;"/><span class="ln">AgentProof</span></a>
  <a href="/dashboard" class="blink">Dashboard →</a>
</div>

<div class="wrap">
  <div class="kick"><span class="kd"></span>Bring your own agent</div>
  <h1>Test any agent in under a minute.</h1>
  <p class="lead">Point AgentProof at your agent, describe what it should do in plain English, and let AI write the behavioral contracts. No JSON, no config — just click Validate and watch it run.</p>

  <div class="tabs">
    <div class="tab on" data-tab="endpoint">Paste endpoint</div>
    <div class="tab" data-tab="uipath"><img src="/logo.png" style="width:14px;height:14px;border-radius:3px;vertical-align:-2px;margin-right:5px;"/>Connect UiPath tenant</div>
  </div>

  <!-- PANEL: ENDPOINT -->
  <div class="card" id="panelEndpoint">
    <div class="step"><span class="snum">1</span><span class="stitle">Connect your agent</span></div>
    <div class="row">
      <label>Agent endpoint URL</label>
      <input id="endpoint" class="mono" placeholder="https://your-agent.com/chat"/>
    </div>
    <div class="adv" id="advToggle">⚙ Advanced (auth header, request field)</div>
    <div class="advbox" id="advBox">
      <div><label>Auth header (optional)</label><input id="auth" class="mono" placeholder="Bearer ..."/></div>
      <div><label>Request field</label><input id="field" class="mono" value="message"/></div>
    </div>
    <div class="row" style="margin-top:16px;">
      <label>What should this agent do? (plain English)</label>
      <textarea id="desc" placeholder="e.g. A customer-support agent for an online store. It must confirm refund eligibility for purchases within 30 days, cite the return policy, stay under 100 words, and never tell the customer to contact a human for simple refunds."></textarea>
    </div>
    <button class="btn primary" id="genBtn">✨ Generate contracts</button>
    <span class="hintlink" id="demoLink">or try it on our demo agent</span>
    <div id="genErr"></div>
  </div>

  <!-- PANEL: UIPATH -->
  <div class="card hidden" id="panelUiPath">
    <div class="step"><span class="snum">1</span><span class="stitle">Connect your UiPath tenant</span></div>
    <p class="muted" style="margin-bottom:16px;">AgentProof discovers the agents published in your Orchestrator, so every UiPath agent can pass through validation before deployment.</p>
    <div class="row">
      <label>Orchestrator URL</label>
      <input id="uipUrl" class="mono" value="https://staging.uipath.com/hackathon26_977/DefaultTenant"/>
    </div>
    <div class="row">
      <label>Access token / PAT</label>
      <input id="uipToken" class="mono" type="password" placeholder="paste a token from your UiPath session"/>
      <div class="muted" style="margin-top:6px;">Used server-side to call Orchestrator. Never stored. UiPath tokens expire ~1h — paste a fresh one.</div>
    </div>
    <div class="adv" id="uipAdvToggle">⚙ Advanced (folder ID — only if folder discovery is blocked)</div>
    <div class="advbox" id="uipAdvBox">
      <div><label>Folder ID (optional)</label><input id="uipFolder" class="mono" placeholder="e.g. 3147226"/></div>
    </div>
    <button class="btn primary" id="connectBtn" style="margin-top:6px;">🔌 Connect &amp; discover agents</button>
    <div id="uipConnErr"></div>

    <div id="uipPicker" class="hidden" style="margin-top:20px;border-top:1px solid var(--br);padding-top:18px;">
      <label>Published agents <span id="uipCount" class="muted"></span></label>
      <select id="uipSelect" class="mono" style="margin-bottom:14px;"></select>
      <div id="uipVerRow" class="hidden" style="margin-bottom:14px;">
        <label>Agent version to validate</label>
        <div class="tabs" style="margin-bottom:0;">
          <div class="tab on" id="verGood" data-ver="good" style="font-size:12.5px;">✓ Compliant build</div>
          <div class="tab" id="verBad" data-ver="regressed" style="font-size:12.5px;">⚠ Regressed build</div>
        </div>
      </div>
      <div class="row">
        <label>Agent runtime endpoint <span class="muted">(where AgentProof calls it)</span></label>
        <input id="uipEndpoint" class="mono" placeholder="https://...  (job-invocation coming next)"/>
      </div>
      <div class="row">
        <label>What should this agent do? (plain English)</label>
        <textarea id="uipDesc" placeholder="Describe the expected behaviour of the selected agent…"></textarea>
      </div>
      <button class="btn primary" id="uipGenBtn">✨ Generate contracts</button>
      <div id="uipGenErr"></div>
    </div>
  </div>

  <!-- STEP 2 -->
  <div class="card hidden" id="step2">
    <div class="step"><span class="snum">2</span><span class="stitle">AI-generated behavioral contracts</span></div>
    <p class="muted" style="margin-bottom:16px;">Review what AgentProof will check. These were written from your description.</p>
    <div id="contracts"></div>
    <div style="display:flex;gap:10px;margin-top:8px;">
      <button class="btn go" id="runBtn">▶ Validate agent</button>
      <button class="btn ghost" id="regenBtn">↻ Regenerate</button>
    </div>
    <div id="runErr"></div>
  </div>

  <!-- STEP 3 -->
  <div class="card hidden" id="step3">
    <div class="step"><span class="snum">3</span><span class="stitle" id="s3title">Validating…</span></div>
    <div id="timeline"></div>
    <div id="result" class="hidden"></div>
  </div>
</div>

<script>
  var $ = function(id){ return document.getElementById(id); };
  var C120 = 2*Math.PI*52;
  var suite = null, suiteId = null, results = [];

  $('advToggle').onclick = function(){ $('advBox').classList.toggle('on'); };
  $('uipAdvToggle').onclick = function(){ $('uipAdvBox').classList.toggle('on'); };
  $('demoLink').onclick = function(){
    $('endpoint').value = window.location.origin + '/v2/chat';
    $('field').value = 'message';
    $('desc').value = "A customer-support agent for ShopEasy. It must confirm refund eligibility for purchases within 30 days, cite the Return Policy (Section 3.1), keep replies under 100 words, and never tell the customer to contact the support team for a simple refund.";
  };

  function slug(s){ return (s||'agent').toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_+|_+$/g,'').slice(0,32) || 'agent'; }
  function err(el,msg){ $(el).innerHTML = '<div class="err">'+msg+'</div>'; }
  function clearErr(el){ $(el).innerHTML=''; }

  function sevWeight(s){ return {critical:3,high:2,medium:1,low:0.5}[s]||1; }

  // ---- tabs ----
  function activeTab(){ var t=document.querySelector('.tab.on'); return t?t.dataset.tab:'endpoint'; }
  document.querySelectorAll('.tab').forEach(function(tab){
    tab.onclick = function(){
      document.querySelectorAll('.tab').forEach(function(x){ x.classList.remove('on'); });
      tab.classList.add('on');
      var t = tab.dataset.tab;
      $('panelEndpoint').classList.toggle('hidden', t!=='endpoint');
      $('panelUiPath').classList.toggle('hidden', t!=='uipath');
    };
  });

  // ---- which inputs are live, per active tab ----
  function getInputs(){
    if(activeTab()==='uipath'){
      return { endpoint:$('uipEndpoint').value.trim(), desc:$('uipDesc').value.trim(),
               auth:null, field:'message', errEl:'uipGenErr' };
    }
    return { endpoint:$('endpoint').value.trim(), desc:$('desc').value.trim(),
             auth:$('auth').value.trim()||null, field:$('field').value.trim()||'message', errEl:'genErr' };
  }

  // ---- connect to UiPath tenant + discover agents ----
  $('connectBtn').onclick = async function(){
    clearErr('uipConnErr');
    var url = $('uipUrl').value.trim(), token = $('uipToken').value.trim();
    var folderId = $('uipFolder').value.trim() || null;
    if(!url || !token){ err('uipConnErr','Enter your Orchestrator URL and a token.'); return; }
    var b=$('connectBtn'); var old=b.innerHTML; b.disabled=true; b.innerHTML='<span class="spin"></span> Connecting…';
    try{
      var r = await fetch('/api/uipath/agents',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({base_url:url, token:token, folder_id:folderId})});
      var j = await r.json();
      if(!j.ok){ err('uipConnErr', j.error||'Could not connect.'); return; }
      var agents = j.agents||[];
      if(!agents.length){ err('uipConnErr','Connected, but no published agents were found in this tenant.'); return; }
      var sel=$('uipSelect'); sel.innerHTML='';
      agents.forEach(function(a,i){
        var o=document.createElement('option'); o.value=i;
        o.textContent = a.name + (a.version?(' · v'+a.version):'') + (a.folder?('  ('+a.folder+')'):'');
        sel.appendChild(o);
      });
      window._uipAgents = agents;
      $('uipCount').textContent = '· '+agents.length+' discovered live';
      $('uipPicker').classList.remove('hidden');
      applyAgent(0);
      sel.onchange = function(){ applyAgent(parseInt(sel.value,10)); };
    }catch(e){ err('uipConnErr', String(e)); }
    finally{ b.disabled=false; b.innerHTML=old; }
  };

  // load agent presets (description + real endpoints) once
  window._presets = {};
  fetch('/api/agent-presets').then(function(r){return r.json();}).then(function(j){ window._presets = j||{}; }).catch(function(){});

  function slugify(s){ return (s||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,''); }
  window._curSlug = null; window._curVer = 'good';

  function endpointFor(slug, ver){
    var base = window.location.origin;
    return ver==='regressed' ? base+'/agent/'+slug+'/regressed/chat' : base+'/agent/'+slug+'/chat';
  }

  function applyAgent(i){
    var a = (window._uipAgents||[])[i]; if(!a) return;
    var slug = slugify(a.name);
    var preset = (window._presets||{})[slug];
    if(preset){
      window._curSlug = slug;
      $('uipVerRow').classList.remove('hidden');
      // default to the regressed build so the demo shows a caught regression
      setVer(window._curVer || 'regressed');
      $('uipDesc').value = preset.description;
    } else {
      // discovered agent with no bundled endpoint (e.g. the validator itself)
      window._curSlug = null;
      $('uipVerRow').classList.add('hidden');
      if(!$('uipEndpoint').value.trim() || $('uipEndpoint').value.indexOf('/agent/')>-1){
        $('uipEndpoint').value = window.location.origin + '/v2/chat';
      }
      $('uipDesc').setAttribute('placeholder','Describe what "'+a.name+'" should do…');
    }
  }

  function setVer(ver){
    window._curVer = ver;
    $('verGood').classList.toggle('on', ver==='good');
    $('verBad').classList.toggle('on', ver==='regressed');
    if(window._curSlug){ $('uipEndpoint').value = endpointFor(window._curSlug, ver); }
  }
  $('verGood').onclick = function(){ setVer('good'); };
  $('verBad').onclick = function(){ setVer('regressed'); };

  $('genBtn').onclick = generate;
  $('uipGenBtn').onclick = generate;
  $('regenBtn').onclick = generate;

  async function generate(){
    var inp = getInputs();
    clearErr(inp.errEl);
    if(!inp.endpoint){ err(inp.errEl,'Enter the agent runtime endpoint first.'); return; }
    if(inp.desc.length < 15){ err(inp.errEl,'Describe what the agent should do (a sentence or two).'); return; }
    var b = (activeTab()==='uipath') ? $('uipGenBtn') : $('genBtn');
    var old = b.innerHTML; b.disabled=true; b.innerHTML='<span class="spin"></span> Generating…';
    try{
      var r = await fetch('/api/generate-suite',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({description:inp.desc, agent_name:slug(inp.endpoint)})});
      var j = await r.json();
      if(!j.ok){ err(inp.errEl, j.error||'Generation failed.'); return; }
      suite = j.test_cases; suiteId = (activeTab()==='uipath'?'uipath_':'byo_')+slug(inp.endpoint);
      renderContracts(suite);
      $('step2').classList.remove('hidden');
      $('step2').scrollIntoView({behavior:'smooth',block:'start'});
    }catch(e){ err(inp.errEl, String(e)); }
    finally{ b.disabled=false; b.innerHTML=old; }
  }

  function renderContracts(cases){
    var html='';
    cases.forEach(function(tc){
      var cs='';
      tc.contracts.forEach(function(c){
        cs += '<div class="gcc"><span class="ty">'+c.type+'</span><span>'+c.value+'</span></div>';
      });
      html += '<div class="gc"><div class="gctop"><span class="gcname">'+tc.name+'</span>'+
              '<span class="gcsev">'+tc.severity+'</span></div>'+
              '<div class="gcinput">↳ "'+tc.input+'"</div>'+cs+'</div>';
    });
    $('contracts').innerHTML = html;
  }

  $('runBtn').onclick = runAll;

  function addTi(cls, title, detail, cur){
    var row=document.createElement('div'); row.className='ti'+(cur?' cur':'');
    var icon = cls==='run'?'':cls==='ok'?'✓':'✗';
    row.innerHTML='<div class="tic '+cls+'">'+icon+'</div><div><div class="tit">'+title+'</div><div class="tid">'+detail+'</div></div>';
    $('timeline').appendChild(row); return row;
  }

  async function runAll(){
    clearErr('runErr');
    results = [];
    $('step3').classList.remove('hidden');
    $('result').classList.add('hidden'); $('result').innerHTML='';
    $('timeline').innerHTML='';
    $('s3title').textContent='Validating live against your agent…';
    $('runBtn').disabled=true;
    $('step3').scrollIntoView({behavior:'smooth',block:'start'});

    var inp = getInputs();
    window._lastEndpoint = inp.endpoint;
    var payloadBase = { endpoint:inp.endpoint, auth_header:inp.auth, input_field:inp.field };

    for(var i=0;i<suite.length;i++){
      var tc = suite[i];
      var row = addTi('run','Evaluating '+tc.name, 'calling your agent + LLM judge', true);
      try{
        var r = await fetch('/api/run-case',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify(Object.assign({test_case:tc}, payloadBase))});
        var j = await r.json();
        row.classList.remove('cur');
        if(!j.ok){
          row.querySelector('.tic').className='tic fail'; row.querySelector('.tic').textContent='✗';
          row.querySelector('.tit').textContent = tc.name+' · error';
          row.querySelector('.tid').textContent = j.error||'failed';
          err('runErr','Could not reach your agent: '+(j.error||'unknown')+'. Check the URL / request field in Advanced.');
          continue;
        }
        results.push(j);
        var cls = j.overall_pass?'ok':'fail';
        row.querySelector('.tic').className='tic '+cls;
        row.querySelector('.tic').textContent = j.overall_pass?'✓':'✗';
        row.querySelector('.tit').textContent = tc.name+' · '+(j.overall_pass?'PASS':'FAIL');
        var failed = j.contract_evaluations.filter(function(e){return !e.passed;}).length;
        row.querySelector('.tid').textContent = j.contract_evaluations.length+' contracts · '+failed+' failed';
      }catch(e){
        row.classList.remove('cur');
        row.querySelector('.tic').className='tic fail'; row.querySelector('.tic').textContent='✗';
        row.querySelector('.tit').textContent = tc.name+' · error';
        row.querySelector('.tid').textContent = String(e);
      }
    }
    $('runBtn').disabled=false;
    renderResult();
  }

  function renderResult(){
    $('s3title').textContent='Validation report';
    if(!results.length){ return; }
    var total=0, failed=0, critFail=false;
    results.forEach(function(r){
      var w=sevWeight(r.severity); total+=w;
      if(!r.overall_pass){ failed+=w; if(r.severity==='critical') critFail=true; }
    });
    var score = total? failed/total : 0;
    var pct = Math.round(score*100);
    var col = pct<1?'#22c55e':pct<25?'#eab308':'#ef4444';
    var status = critFail||pct>=25 ? 'FAILED' : pct>0.5?'DEGRADED':'PASSED';
    var statusCol = status==='PASSED'?'#22c55e':status==='DEGRADED'?'#eab308':'#ef4444';
    var recoTitle = status==='PASSED'?'Safe to deploy':status==='DEGRADED'?'Review before deploy':'Deployment blocked';
    var recoSub = status==='PASSED'?'All behavioral contracts satisfied.':status==='DEGRADED'?'Some contracts failed — review the report.':'Critical contracts failed — do not ship.';
    var off = C120*(1-Math.min(pct,100)/100);

    var nPass = results.filter(function(r){return r.overall_pass;}).length;
    var html = '';
    html += '<div style="display:grid;grid-template-columns:130px 1fr;gap:22px;align-items:center;margin-bottom:8px;">';
    html += '<div class="ring"><svg width="120" height="120"><circle cx="60" cy="60" r="52" fill="none" stroke="#1f1f23" stroke-width="10"/>'+
            '<circle cx="60" cy="60" r="52" fill="none" stroke="'+col+'" stroke-width="10" stroke-linecap="round" stroke-dasharray="'+C120.toFixed(1)+'" stroke-dashoffset="'+C120.toFixed(1)+'" style="transition:stroke-dashoffset 1s ease" id="rf"/></svg>'+
            '<div class="n"><div class="v" style="color:'+col+'">'+pct+'%</div><div class="l">fail rate</div></div></div>';
    html += '<div><div class="reco" style="background:'+statusCol+'14;border:1px solid '+statusCol+'40;">'+
            '<span style="width:10px;height:10px;border-radius:50%;background:'+statusCol+';box-shadow:0 0 12px '+statusCol+';"></span>'+
            '<div><div class="recl" style="color:'+statusCol+'">'+recoTitle+'</div><div class="recs">'+recoSub+'</div></div></div>'+
            '<div class="muted">'+nPass+' / '+results.length+' tests passed · suite '+suiteId+'</div></div>';
    html += '</div>';

    results.forEach(function(r){
      var c = r.overall_pass?'#22c55e':'#ef4444';
      var evs='';
      r.contract_evaluations.forEach(function(e){
        var ec = e.passed?'ok':'f';
        evs += '<div class="ev"><span class="evic '+ec+'">'+(e.passed?'✓':'✗')+'</span>'+
               '<div style="flex:1"><div class="evcid">'+e.contract_id+'</div><div class="evr">'+e.reasoning+'</div></div>'+
               '<span class="evc" style="color:'+(e.passed?'#52525b':'#ef4444')+'">'+Math.round(e.confidence*100)+'%</span></div>';
      });
      html += '<div class="tcase" style="border-left-color:'+c+'"><div class="tchead">'+
              '<span class="pill '+(r.overall_pass?'p':'f')+'">'+(r.overall_pass?'PASS':'FAIL')+'</span>'+
              '<span style="font-weight:600;font-size:14px">'+r.test_name+'</span>'+
              '<span style="margin-left:auto;font-size:10px;font-family:var(--mono);color:#52525b;text-transform:uppercase;letter-spacing:1px">'+r.severity+'</span></div>'+
              '<div class="bub">'+(r.agent_response||'').replace(/</g,'&lt;')+'</div>'+evs+'</div>';
    });

    html += '<div style="display:flex;gap:10px;margin-top:14px;">'+
            '<button class="btn primary" id="saveBtn">Save to dashboard</button>'+
            '<a class="btn ghost" href="/dashboard">Open dashboard</a></div>'+
            '<div id="saveMsg"></div>';
    $('result').innerHTML = html;
    $('result').classList.remove('hidden');
    requestAnimationFrame(function(){ var rf=$('rf'); if(rf) rf.style.strokeDashoffset = off; });
    $('saveBtn').onclick = saveRun;
  }

  async function saveRun(){
    var b=$('saveBtn'); b.disabled=true; b.innerHTML='<span class="spin"></span> Saving…';
    try{
      var r = await fetch('/api/save-run',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({suite_id:suiteId, results:results, agent_endpoint:window._lastEndpoint||null})});
      var j = await r.json();
      if(j.ok){ $('saveMsg').innerHTML='<div class="muted" style="margin-top:10px;color:#86efac">✓ Saved · status '+j.status+' · <a href="/dashboard" style="color:#f97316">view on dashboard →</a></div>'; b.innerHTML='Saved ✓'; }
      else { $('saveMsg').innerHTML='<div class="err">'+(j.error||'save failed')+'</div>'; b.disabled=false; b.innerHTML='Save to dashboard'; }
    }catch(e){ $('saveMsg').innerHTML='<div class="err">'+String(e)+'</div>'; b.disabled=false; b.innerHTML='Save to dashboard'; }
  }
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

        import math
        total = len(runs)
        passed = sum(1 for r in runs if r["overall_status"] == "PASSED")
        failed = sum(1 for r in runs if r["overall_status"] == "FAILED")
        pass_rate = round(passed / total * 100) if total else 0

        def _d(r):
            return float(r["drift_score"] or 0)  # Postgres returns Decimal; coerce for math

        latest = runs[0] if runs else None
        latest_drift = round(_d(latest) * 100, 1) if latest else 0.0
        latest_status = latest["overall_status"] if latest else "NONE"
        latest_color = _status_color(latest_status)
        avg_drift = round(sum(_d(r) for r in runs) / total * 100, 1) if total else 0.0

        latest_verdict = {
            "PASSED": "All contracts satisfied — safe to deploy.",
            "DEGRADED": "Behavioral drift detected — review before deploy.",
            "FAILED": "Critical regressions — deployment would be blocked.",
            "NONE": "No validation runs yet. Trigger one from UiPath.",
        }.get(latest_status, "")

        # animated drift ring for the latest run
        _rs, _sw = 150, 12
        _r = _rs / 2 - _sw
        _circ = 2 * math.pi * _r
        _off = _circ * (1 - min(latest_drift, 100) / 100)
        ring = (
            f'<div class="ringbox" style="width:{_rs}px;height:{_rs}px;">'
            f'<svg width="{_rs}" height="{_rs}" style="transform:rotate(-90deg);">'
            f'<circle cx="{_rs/2}" cy="{_rs/2}" r="{_r}" fill="none" stroke="#1f1f23" stroke-width="{_sw}"/>'
            f'<circle class="ringfill" cx="{_rs/2}" cy="{_rs/2}" r="{_r}" fill="none" stroke="{latest_color}" '
            f'stroke-width="{_sw}" stroke-linecap="round" stroke-dasharray="{_circ:.2f}" '
            f'style="--c:{_circ:.2f};--off:{_off:.2f};"/>'
            f'</svg>'
            f'<div class="ringnum"><div class="rv" style="color:{latest_color};">{latest_drift}%</div><div class="rl">drift</div></div>'
            f'</div>'
        )

        # run-history sparkline (oldest -> newest)
        spark = ""
        for idx, r in enumerate(reversed(runs[:26])):
            c = _status_color(r["overall_status"])
            h = 12 + round(min(_d(r), 1.0) * 34)
            spark += (
                f'<span class="sb" title="{r["overall_status"]} · {round(_d(r)*100)}%" '
                f'style="height:{h}px;background:{c};animation-delay:{idx*0.025:.2f}s;"></span>'
            )
        if not spark:
            spark = '<span style="color:var(--t3);font-size:12px;font-family:var(--mono);">awaiting first run…</span>'

        rows = ""
        for r in runs:
            status = r["overall_status"]
            pill = {"PASSED": "sp-p", "DEGRADED": "sp-d", "FAILED": "sp-f"}.get(status, "")
            sc = _status_color(status)
            drift = r["drift_score"] or 0
            regressions = r["regressions"]
            if isinstance(regressions, str):
                regressions = json.loads(regressions)
            reg_count = len(regressions) if regressions else 0
            ts = str(r["timestamp"])[:19].replace("T", " ")
            reg_color = "#ef4444" if reg_count > 0 else "#22c55e"
            endpoint = r.get("agent_endpoint") or ""
            ep_short = endpoint.replace("https://", "").replace("http://", "") if endpoint else "—"
            ep_cell = (
                f'<span style="color:#a1a1aa;">{ep_short}</span>' if endpoint
                else '<span style="color:#3f3f46;">—</span>'
            )
            rows += (
                f'<tr class="runrow" onclick="window.location=\'/run/{r["id"]}\'">'
                f'<td style="padding:13px 18px;color:#a1a1aa;font-family:monospace;font-size:12px;"><span class="rowdot" style="background:{sc};"></span>{ts}</td>'
                f'<td style="padding:13px 18px;font-weight:500;font-family:monospace;font-size:13px;">{r["suite_id"]}</td>'
                f'<td style="padding:13px 18px;font-family:monospace;font-size:12px;max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{ep_cell}</td>'
                f'<td style="padding:13px 18px;"><span class="sp {pill}">{status}</span></td>'
                f'<td style="padding:13px 18px;">{_drift_bar(drift)}</td>'
                f'<td style="padding:13px 18px;color:{reg_color};font-weight:600;font-size:13px;font-family:monospace;">{reg_count}</td>'
                f'<td style="padding:13px 18px;color:#52525b;font-size:12px;font-family:monospace;">{str(r["id"])[:8]}… <span class="arrow">→</span></td>'
                f'</tr>'
            )

        error_html = (
            f'<div style="background:rgba(239,68,68,.10);border:1px solid rgba(239,68,68,.25);'
            f'color:#ef4444;padding:12px 16px;border-radius:10px;margin-bottom:18px;'
            f'font-family:monospace;font-size:13px;">DB Error: {error}</div>'
        ) if error else ""

        empty_row = (
            '<tr><td colspan="7" style="padding:48px;text-align:center;color:#52525b;font-size:13px;">'
            'No runs yet &nbsp;·&nbsp; '
            '<a href="/live" style="color:#f97316;font-weight:600;">▶ run the live demo</a>'
            ' &nbsp;or trigger from UiPath: <code style="color:#a1a1aa;">uipath run main.py \'{"suite_id":"shopease_refunds",…}\'</code>'
            '</td></tr>'
        )

        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <link rel="icon" type="image/png" href="/logo.png"/>
  <title>Dashboard — AgentProof</title>
  <style>{_DARK_CSS}{_DASH_CSS}</style>
</head>
<body>
<header style="background:rgba(9,9,11,.78);backdrop-filter:blur(12px);border-bottom:1px solid var(--br);padding:0 40px;height:56px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:99;">
  <div style="display:flex;align-items:center;gap:12px;">
    <a href="/" style="font-size:12.5px;color:var(--t3);padding:5px 11px;border:1px solid var(--br2);border-radius:6px;">← Home</a>
    <div style="display:flex;align-items:center;gap:8px;">
      <img src="/logo.png" alt="AgentProof" style="width:34px;height:34px;border-radius:7px;display:block;"/>
      <span style="font-weight:700;font-size:15px;">AgentProof</span>
      <span style="font-size:13px;color:var(--t3);margin-left:2px;">/ Console</span>
    </div>
  </div>
  <a href="/live" style="font-size:12.5px;font-weight:600;color:#f97316;padding:6px 13px;border:1px solid rgba(249,115,22,.3);border-radius:6px;">▶ Live demo</a>
</header>

<div class="console">
  {error_html}

  <!-- HERO: latest run health -->
  <div class="hero">
    {ring}
    <div class="verdict">
      <div class="verdline">
        <span class="vdot" style="background:{latest_color};box-shadow:0 0 12px {latest_color};"></span>
        <span class="vstatus" style="color:{latest_color};">{latest_status}</span>
        <span style="font-size:11px;color:var(--t3);font-family:var(--mono);margin-left:4px;text-transform:uppercase;letter-spacing:1px;">latest run</span>
      </div>
      <div class="vsub">{latest_verdict}</div>
      <div class="cards">
        <div class="card" style="animation-delay:.05s;"><div class="ck">Total runs</div><div class="cv" data-count="{total}">0</div></div>
        <div class="card" style="animation-delay:.12s;"><div class="ck">Pass rate</div><div class="cv" style="color:#22c55e;"><span data-count="{pass_rate}">0</span>%</div></div>
        <div class="card" style="animation-delay:.19s;"><div class="ck">Failed</div><div class="cv" style="color:#ef4444;" data-count="{failed}">0</div></div>
        <div class="card" style="animation-delay:.26s;"><div class="ck">Avg drift</div><div class="cv" style="color:#eab308;"><span data-count="{avg_drift}" data-dec="1">0</span>%</div></div>
      </div>
    </div>
  </div>

  <!-- RUN HISTORY SPARKLINE -->
  <div class="panel">
    <div class="ptitle">Drift history · last {min(total,26)} runs</div>
    <div class="spark">{spark}</div>
  </div>

  <!-- RUNS TABLE -->
  <div class="ptitle">Recent validation runs</div>
  <div class="tablewrap">
    <table>
      <thead>
        <tr style="border-bottom:1px solid var(--br);">
          <th style="padding:11px 18px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Timestamp</th>
          <th style="padding:11px 18px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Suite</th>
          <th style="padding:11px 18px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Agent Endpoint</th>
          <th style="padding:11px 18px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Status</th>
          <th style="padding:11px 18px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Drift</th>
          <th style="padding:11px 18px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Regressions</th>
          <th style="padding:11px 18px;font-size:10.5px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:1.2px;">Run ID</th>
        </tr>
      </thead>
      <tbody>{rows if rows else empty_row}</tbody>
    </table>
  </div>
</div>
{_DASH_JS}
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

        import math
        status = run["overall_status"]
        color = _status_color(status)
        drift = round(float(run["drift_score"] or 0) * 100, 1)  # Postgres Decimal -> float
        ts = str(run["timestamp"])[:19].replace("T", " ")
        results = run["results"]
        if isinstance(results, str):
            results = json.loads(results)
        results = results or []
        regressions = run["regressions"]
        if isinstance(regressions, str):
            regressions = json.loads(regressions)
        reg_count = len(regressions) if regressions else 0

        t_total = len(results)
        t_pass = sum(1 for r in results if r["overall_pass"])
        t_fail = t_total - t_pass
        n_contracts = sum(len(r.get("contract_evaluations", [])) for r in results)
        agent_endpoint = run.get("agent_endpoint") or ""
        endpoint_chip = (
            f'<span class="chip">endpoint&nbsp; <b style="color:#f97316;">{agent_endpoint}</b></span>'
            if agent_endpoint else ""
        )

        verdict = {
            "PASSED": "All behavioral contracts satisfied. Safe to deploy.",
            "DEGRADED": "Behavioral drift detected. Review before deploying.",
            "FAILED": "Critical regressions found. Deployment would be blocked.",
        }.get(status, "")

        # drift ring
        _rs, _sw = 150, 12
        _r = _rs / 2 - _sw
        _circ = 2 * math.pi * _r
        _off = _circ * (1 - min(drift, 100) / 100)
        ring = (
            f'<div class="ringbox" style="width:{_rs}px;height:{_rs}px;">'
            f'<svg width="{_rs}" height="{_rs}" style="transform:rotate(-90deg);">'
            f'<circle cx="{_rs/2}" cy="{_rs/2}" r="{_r}" fill="none" stroke="#1f1f23" stroke-width="{_sw}"/>'
            f'<circle class="ringfill" cx="{_rs/2}" cy="{_rs/2}" r="{_r}" fill="none" stroke="{color}" '
            f'stroke-width="{_sw}" stroke-linecap="round" stroke-dasharray="{_circ:.2f}" '
            f'style="--c:{_circ:.2f};--off:{_off:.2f};"/>'
            f'</svg>'
            f'<div class="ringnum"><div class="rv" style="color:{color};">{drift}%</div><div class="rl">drift</div></div>'
            f'</div>'
        )

        test_cards = ""
        for i, r in enumerate(results):
            tc_color = "#22c55e" if r["overall_pass"] else "#ef4444"
            tc_label = "PASS" if r["overall_pass"] else "FAIL"
            tc_pill = "sp-p" if r["overall_pass"] else "sp-f"
            contracts_html = ""
            for ev in r.get("contract_evaluations", []):
                ev_pass = ev["passed"]
                ev_cls = "ok" if ev_pass else "fail"
                ev_icon = "✓" if ev_pass else "✗"
                ev_col = "#22c55e" if ev_pass else "#ef4444"
                conf = round(ev["confidence"] * 100)
                contracts_html += (
                    f'<div class="ev">'
                    f'<span class="evic {ev_cls}">{ev_icon}</span>'
                    f'<div class="evbody">'
                    f'<div class="evcid">contract · {ev["contract_id"]}</div>'
                    f'<div class="evreason">{ev["reasoning"]}</div>'
                    f'<div class="cmeter"><div class="cbar"><i style="--w:{conf}%;background:{ev_col};"></i></div>'
                    f'<span class="evpct" style="color:{ev_col};">{conf}%</span></div>'
                    f'</div>'
                    f'</div>'
                )
            test_cards += (
                f'<div class="tcase" style="border-left-color:{tc_color};animation-delay:{i*0.06:.2f}s;">'
                f'<div class="tchead">'
                f'<span class="sp {tc_pill}">{tc_label}</span>'
                f'<span class="tcname">{r["test_name"]}</span>'
                f'<span class="tcsev">{r["severity"]}</span>'
                f'</div>'
                f'<div class="tcbody">'
                f'<div class="agent"><span class="avatar">AI</span>'
                f'<div class="bubble">{r["agent_response"]}</div></div>'
                f'{contracts_html}'
                f'</div>'
                f'</div>'
            )

        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <link rel="icon" type="image/png" href="/logo.png"/>
  <title>Run {run_id[:8]} — AgentProof</title>
  <style>{_DARK_CSS}{_DASH_CSS}{_REPORT_CSS}</style>
</head>
<body>
<header style="background:rgba(9,9,11,.78);backdrop-filter:blur(12px);border-bottom:1px solid var(--br);padding:0 40px;height:56px;display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:99;">
  <a href="/dashboard" style="font-size:12.5px;color:var(--t3);padding:5px 11px;border:1px solid var(--br2);border-radius:6px;">← Dashboard</a>
  <img src="/logo.png" alt="AgentProof" style="width:34px;height:34px;border-radius:7px;display:block;"/>
  <span style="font-weight:700;font-size:15px;">AgentProof</span>
  <span style="font-size:13px;color:var(--t3);">/ Report</span>
  <span style="font-family:monospace;font-size:12px;color:var(--t3);margin-left:4px;">{run_id[:8]}…</span>
</header>

<div class="rpt">
  <div class="rhero">
    {ring}
    <div class="rverd">
      <div class="rstatusline">
        <span class="rdot" style="background:{color};box-shadow:0 0 12px {color};"></span>
        <span class="rstatus" style="color:{color};">{status}</span>
        <span style="font-size:11px;color:var(--t3);font-family:var(--mono);text-transform:uppercase;letter-spacing:1px;">validation report</span>
      </div>
      <div class="rsub">{verdict}</div>
      <div class="rmeta">
        <span class="chip">suite&nbsp; <b>{run["suite_id"]}</b></span>
        {endpoint_chip}
        <span class="chip">tests&nbsp; <b style="color:#22c55e;">{t_pass} pass</b> · <b style="color:#ef4444;">{t_fail} fail</b></span>
        <span class="chip">contracts&nbsp; <b>{n_contracts}</b></span>
        <span class="chip">regressions&nbsp; <b style="color:{'#ef4444' if reg_count else '#22c55e'};">{reg_count}</b></span>
        <span class="chip">{ts} UTC</span>
      </div>
    </div>
  </div>

  <div class="seclbl">Test cases · {t_total}</div>
  {test_cards}
</div>
</body>
</html>""")

except Exception as _startup_error:
    _tb = traceback.format_exc()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def startup_error(path: str = ""):
        return JSONResponse({"error": str(_startup_error), "traceback": _tb}, status_code=500)
