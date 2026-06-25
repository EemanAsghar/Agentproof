from pydantic import BaseModel
from typing import Literal, Optional


class BehavioralContract(BaseModel):
    contract_id: str
    type: Literal[
        "contains_intent",
        "does_not_contain",
        "sentiment",
        "response_length",
        "format_compliance",
        "safety",
    ]
    value: str
    threshold: float = 0.7
    required: bool = True
    severity: Literal["critical", "high", "medium", "low"] = "high"


class TestCase(BaseModel):
    test_id: str
    name: str
    input: str
    contracts: list[BehavioralContract]
    severity: Literal["critical", "high", "medium", "low"] = "high"


class TestSuite(BaseModel):
    suite_id: str
    agent_name: str
    agent_endpoint: str
    agent_auth_header: Optional[str] = None
    test_cases: list[TestCase]


class ContractEvaluation(BaseModel):
    contract_id: str
    passed: bool
    confidence: float
    reasoning: str


class TestResult(BaseModel):
    test_id: str
    test_name: str
    severity: str
    agent_response: str
    contract_evaluations: list[ContractEvaluation]
    overall_pass: bool
    flags: list[str] = []


if __name__ == "__main__":
    contract = BehavioralContract(
        contract_id="c1",
        type="contains_intent",
        value="confirms refund eligibility",
        threshold=0.8,
        required=True,
        severity="critical",
    )
    test_case = TestCase(
        test_id="t1",
        name="Refund eligibility",
        input="I bought this 3 weeks ago. Can I get a refund?",
        contracts=[contract],
        severity="critical",
    )
    print("contracts.py OK:", test_case.model_dump())
