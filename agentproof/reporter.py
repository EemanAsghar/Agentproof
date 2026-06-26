import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from .contracts import TestResult

STATUS_COLORS = {
    "PASSED": "#10B981",
    "DEGRADED": "#F59E0B",
    "FAILED": "#F43F5E",
}


def render_html_report(
    suite_id: str,
    agent_name: str,
    status: str,
    drift_score: float,
    results: list[TestResult],
    regressions: list,
    run_id: str,
) -> str:
    """Render the report as an HTML string (pure Jinja2 — no system libraries).

    Works on the UiPath runtime, unlike PDF generation which needs WeasyPrint's
    system dependencies.
    """
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)))
    template = env.get_template("report.html")

    return template.render(
        run_id=run_id,
        suite_id=suite_id,
        agent_name=agent_name,
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        status=status,
        status_color=STATUS_COLORS.get(status, "#6B7280"),
        drift_score=drift_score,
        drift_percent=round(drift_score * 100, 1),
        total_tests=len(results),
        passed_tests=sum(1 for r in results if r.overall_pass),
        failed_tests=sum(1 for r in results if not r.overall_pass),
        regressions=regressions,
        results=results,
    )


def generate_report(
    suite_id: str,
    agent_name: str,
    status: str,
    drift_score: float,
    results: list[TestResult],
    regressions: list,
    run_id: str,
) -> str:
    """Render the report to a PDF file (local use — requires WeasyPrint)."""
    from weasyprint import HTML  # lazy: needs system libs not present on UiPath runtime

    html_content = render_html_report(
        suite_id, agent_name, status, drift_score, results, regressions, run_id)
    output_path = f"/tmp/agentproof_report_{run_id}.pdf"
    HTML(string=html_content).write_pdf(output_path)
    return output_path


if __name__ == "__main__":
    print("reporter.py OK — imports successful")
