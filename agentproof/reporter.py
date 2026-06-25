import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from .contracts import TestResult

STATUS_COLORS = {
    "PASSED": "#10B981",
    "DEGRADED": "#F59E0B",
    "FAILED": "#F43F5E",
}


def generate_report(
    suite_id: str,
    agent_name: str,
    status: str,
    drift_score: float,
    results: list[TestResult],
    regressions: list,
    run_id: str,
) -> str:
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)))
    template = env.get_template("report.html")

    status_color = STATUS_COLORS.get(status, "#6B7280")

    html_content = template.render(
        run_id=run_id,
        suite_id=suite_id,
        agent_name=agent_name,
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        status=status,
        status_color=status_color,
        drift_score=drift_score,
        drift_percent=round(drift_score * 100, 1),
        total_tests=len(results),
        passed_tests=sum(1 for r in results if r.overall_pass),
        failed_tests=sum(1 for r in results if not r.overall_pass),
        regressions=regressions,
        results=results,
    )

    output_path = f"/tmp/agentproof_report_{run_id}.pdf"
    HTML(string=html_content).write_pdf(output_path)
    return output_path


if __name__ == "__main__":
    print("reporter.py OK — imports successful")
    print("(PDF generation skipped in smoke test — needs live template + WeasyPrint)")
