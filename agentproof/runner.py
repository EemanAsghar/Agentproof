import asyncio
import json

import httpx
from .contracts import TestCase


async def run_test_case(
    test_case: TestCase,
    agent_endpoint: str,
    auth_header: str | None = None,
) -> str:
    headers = {"Content-Type": "application/json"}
    if auth_header:
        headers["Authorization"] = auth_header

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            agent_endpoint,
            headers=headers,
            json={"message": test_case.input},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response") or data.get("message") or str(data)


def _parse_agent_output(out) -> str:
    """Extract a text reply from a UiPath job's OutputArguments."""
    if out is None:
        return ""
    if isinstance(out, str):
        s = out.strip()
        try:
            d = json.loads(s)
        except Exception:
            return s
    elif isinstance(out, dict):
        d = out
    else:
        return str(out)
    if isinstance(d, dict):
        return (d.get("response") or d.get("message") or d.get("output")
                or next((v for v in d.values() if isinstance(v, str) and v.strip()), str(d)))
    return str(d)


async def run_test_case_native(
    test_case: TestCase,
    target_agent: str,
    folder_path: str = "Shared",
    timeout_s: int = 240,
) -> str:
    """Validate a published UiPath agent by invoking it as a real Orchestrator job.

    AgentProof starts the target agent as a job, waits for it to finish, and reads
    its output — so both the validator and the agent under test run on UiPath.
    """
    from uipath.platform import UiPath

    sdk = UiPath()
    job = await sdk.processes.invoke_async(
        name=target_agent,
        input_arguments={"message": test_case.input},
        folder_path=folder_path,
    )
    job_key = getattr(job, "key", None) or getattr(job, "Key", None)

    waited = 0
    while waited < timeout_s:
        await asyncio.sleep(5)
        waited += 5
        j = await sdk.jobs.retrieve_async(job_key, folder_path=folder_path)
        state = str(getattr(j, "state", None) or getattr(j, "State", "")).lower()
        if "success" in state:
            out = await sdk.jobs.extract_output_async(j)
            return _parse_agent_output(out)
        if "fault" in state or "stop" in state:
            raise RuntimeError(f"Target agent job ended: {state}")
    raise RuntimeError(f"Target agent '{target_agent}' job timed out after {timeout_s}s")


if __name__ == "__main__":
    import asyncio
    from .contracts import BehavioralContract, TestCase

    tc = TestCase(
        test_id="t1",
        name="smoke",
        input="hello",
        contracts=[
            BehavioralContract(
                contract_id="c1",
                type="contains_intent",
                value="greeting",
                threshold=0.7,
            )
        ],
    )
    print("runner.py OK — TestCase built:", tc.test_id)
    print("(HTTP test skipped in smoke test — needs live endpoint)")
