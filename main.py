from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from pydantic import BaseModel
import asyncio
import json

load_dotenv()

from agentproof.contracts import TestSuite, TestResult
from agentproof.runner import run_test_case
from agentproof.validator import evaluate_contracts, is_overall_pass
from agentproof.regression import compute_drift_score, get_status
from agentproof.db import save_run, get_baseline
# NOTE: agentproof.reporter (WeasyPrint) is imported lazily inside generate_pdf_report
# so the agent runs on the UiPath runtime even when system PDF libs are unavailable.


# ── UiPath required Input / Output models ──────────────────────────────────────

class Input(BaseModel):
    suite_id: str
    agent_endpoint: str

class Output(BaseModel):
    status: str
    drift_score: float
    regressions_count: int
    run_id: str
    report_path: str


# ── State ──────────────────────────────────────────────────────────────────────

class AgentProofState(TypedDict):
    suite_id: str
    agent_endpoint: str
    suite: Optional[dict]
    results: list
    baseline_results: list
    drift_score: float
    regressions: list
    status: str
    run_id: str
    report_path: str


# ── Nodes ──────────────────────────────────────────────────────────────────────

def load_suite(state: AgentProofState) -> AgentProofState:
    with open(f"test_suites/{state['suite_id']}.json") as f:
        state["suite"] = json.load(f)
    # Override endpoint if provided at runtime
    if state.get("agent_endpoint"):
        state["suite"]["agent_endpoint"] = state["agent_endpoint"]
    print(f"[load_suite] Loaded suite '{state['suite_id']}' with "
          f"{len(state['suite']['test_cases'])} test cases")
    return state


async def run_tests(state: AgentProofState) -> AgentProofState:
    suite = TestSuite(**state["suite"])
    results = []

    for test_case in suite.test_cases:
        print(f"[run_tests] Running: {test_case.test_id}")
        agent_response = await run_test_case(
            test_case,
            state["agent_endpoint"],
        )
        evaluations = evaluate_contracts(
            test_case.input,
            agent_response,
            test_case.contracts,
        )
        overall = is_overall_pass(evaluations, test_case.contracts)
        result_icon = "✓" if overall else "✗"
        print(f"[run_tests] {result_icon} {test_case.test_id}: {'PASS' if overall else 'FAIL'}")

        results.append(
            TestResult(
                test_id=test_case.test_id,
                test_name=test_case.name,
                severity=test_case.severity,
                agent_response=agent_response,
                contract_evaluations=evaluations,
                overall_pass=overall,
            )
        )

    state["results"] = results
    return state


def detect_regressions(state: AgentProofState) -> AgentProofState:
    try:
        baseline = get_baseline(state["suite_id"])
    except Exception as e:
        print(f"[detect_regressions] Baseline lookup skipped (DB unavailable): {e}")
        baseline = None
    state["baseline_results"] = baseline or []

    if not baseline:
        print("[detect_regressions] No baseline found — this run will become the baseline")

    drift_score, regressions = compute_drift_score(
        state["results"],
        state["baseline_results"],
    )
    state["drift_score"] = drift_score
    state["regressions"] = regressions
    state["status"] = get_status(drift_score)

    print(
        f"[detect_regressions] Drift score: {round(drift_score * 100, 1)}% | "
        f"Status: {state['status']} | Regressions: {len(regressions)}"
    )
    return state


def save_results(state: AgentProofState) -> AgentProofState:
    try:
        run_id = save_run(
            suite_id=state["suite_id"],
            results=state["results"],
            drift_score=state["drift_score"],
            status=state["status"],
            regressions=state["regressions"],
            agent_endpoint=state.get("agent_endpoint"),
            tenant_id=state.get("tenant_id"),
        )
        state["run_id"] = run_id
        print(f"[save_results] Run saved: {run_id}")
    except Exception as e:
        state["run_id"] = "unsaved"
        print(f"[save_results] Save skipped (DB unavailable): {e}")
    return state


def generate_pdf_report(state: AgentProofState) -> AgentProofState:
    try:
        from agentproof.reporter import generate_report  # lazy: WeasyPrint optional
        suite = TestSuite(**state["suite"])
        path = generate_report(
            suite_id=state["suite_id"],
            agent_name=suite.agent_name,
            status=state["status"],
            drift_score=state["drift_score"],
            results=state["results"],
            regressions=state["regressions"],
            run_id=state["run_id"],
        )
        state["report_path"] = path
        print(f"[generate_pdf_report] Report saved: {path}")
    except Exception as e:
        state["report_path"] = ""
        print(f"[generate_pdf_report] Report skipped: {e}")
    return state


def notify_if_failed(state: AgentProofState) -> AgentProofState:
    if state["status"] == "FAILED":
        import os
        import requests

        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if token and chat_id:
            regressions = state["regressions"]
            reg_text = "\n".join(
                f"  • {r['test_name']} ({r['severity']})"
                for r in regressions
            )
            msg = (
                f"\U0001f534 AgentProof — FAILED\n"
                f"Agent: {state['suite_id']}\n"
                f"Drift Score: {round(state['drift_score'] * 100, 1)}%\n"
                f"Regressions: {len(regressions)}\n\n"
                f"{reg_text}\n\n"
                f"Run ID: {state['run_id']}"
            )
            resp = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": msg},
                timeout=10,
            )
            if resp.ok:
                print("[notify_if_failed] Telegram notification sent")
            else:
                print(f"[notify_if_failed] Telegram error: {resp.text}")
        else:
            print("[notify_if_failed] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set — skipping notification")
    return state


# ── Graph ──────────────────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentProofState)

    graph.add_node("load_suite", load_suite)
    graph.add_node("run_tests", run_tests)
    graph.add_node("detect_regressions", detect_regressions)
    graph.add_node("save_results", save_results)
    graph.add_node("generate_pdf_report", generate_pdf_report)
    graph.add_node("notify_if_failed", notify_if_failed)

    graph.add_edge(START, "load_suite")
    graph.add_edge("load_suite", "run_tests")
    graph.add_edge("run_tests", "detect_regressions")
    graph.add_edge("detect_regressions", "save_results")
    graph.add_edge("save_results", "generate_pdf_report")
    graph.add_edge("generate_pdf_report", "notify_if_failed")
    graph.add_edge("notify_if_failed", END)

    return graph.compile()


# ── UiPath entry point ─────────────────────────────────────────────────────────

async def main(input: Input) -> Output:
    graph = build_graph()
    result = await graph.ainvoke(
        {
            "suite_id": input.suite_id,
            "agent_endpoint": input.agent_endpoint,
            "suite": None,
            "results": [],
            "baseline_results": [],
            "drift_score": 0.0,
            "regressions": [],
            "status": "",
            "run_id": "",
            "report_path": "",
        }
    )
    return Output(
        status=result["status"],
        drift_score=result["drift_score"],
        regressions_count=len(result["regressions"]),
        run_id=result["run_id"],
        report_path=result["report_path"],
    )


if __name__ == "__main__":
    import sys

    suite_id = sys.argv[1] if len(sys.argv) > 1 else "aria_customer_support"
    endpoint = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000/v1/chat"

    print(f"\nAgentProof — running suite '{suite_id}' against {endpoint}\n")
    result = asyncio.run(main(Input(suite_id=suite_id, agent_endpoint=endpoint)))

    print("\n" + "=" * 60)
    print(f"  Status:      {result.status}")
    print(f"  Drift Score: {round(result.drift_score * 100, 1)}%")
    print(f"  Regressions: {result.regressions_count}")
    print(f"  Run ID:      {result.run_id}")
    print(f"  Report:      {result.report_path}")
    print("=" * 60 + "\n")
