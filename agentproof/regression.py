from .contracts import TestResult

SEVERITY_WEIGHTS = {
    "critical": 3.0,
    "high": 2.0,
    "medium": 1.0,
    "low": 0.5,
}


def compute_drift_score(
    current_results: list[TestResult],
    baseline_results: list[TestResult],
) -> tuple[float, list[dict]]:
    if not baseline_results:
        return 0.0, []

    baseline_map = {r.test_id: r for r in baseline_results}
    total_weight = 0.0
    regression_weight = 0.0
    regressions = []

    for result in current_results:
        weight = SEVERITY_WEIGHTS.get(result.severity, 1.0)
        total_weight += weight
        baseline = baseline_map.get(result.test_id)

        if baseline and baseline.overall_pass and not result.overall_pass:
            regression_weight += weight
            regressions.append(
                {
                    "test_id": result.test_id,
                    "test_name": result.test_name,
                    "severity": result.severity,
                    "was": "PASS",
                    "now": "FAIL",
                    "agent_response": result.agent_response,
                    "failed_contracts": [
                        {
                            "contract_id": ev.contract_id,
                            "reasoning": ev.reasoning,
                        }
                        for ev in result.contract_evaluations
                        if not ev.passed
                    ],
                }
            )

    drift_score = (
        round(regression_weight / total_weight, 4) if total_weight > 0 else 0.0
    )
    return drift_score, regressions


def get_status(drift_score: float) -> str:
    if drift_score < 0.05:
        return "PASSED"
    elif drift_score < 0.15:
        return "DEGRADED"
    else:
        return "FAILED"


if __name__ == "__main__":
    from .contracts import TestResult, ContractEvaluation

    def _make_result(test_id, passed):
        return TestResult(
            test_id=test_id,
            test_name=f"Test {test_id}",
            severity="high",
            agent_response="mock response",
            contract_evaluations=[
                ContractEvaluation(
                    contract_id="c1",
                    passed=passed,
                    confidence=0.9,
                    reasoning="mock",
                )
            ],
            overall_pass=passed,
        )

    baseline = [_make_result("t1", True), _make_result("t2", True)]
    current = [_make_result("t1", False), _make_result("t2", True)]
    score, regressions = compute_drift_score(current, baseline)
    assert score == 0.5, f"Expected 0.5, got {score}"
    assert len(regressions) == 1
    assert get_status(0.0) == "PASSED"
    assert get_status(0.1) == "DEGRADED"
    assert get_status(0.3) == "FAILED"
    print("regression.py OK — drift score:", score, "status:", get_status(score))
