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
