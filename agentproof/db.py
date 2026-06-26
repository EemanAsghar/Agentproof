import os
import json
import uuid
import psycopg2
import psycopg2.extras
from datetime import datetime
from .contracts import TestResult


def get_connection():
    return psycopg2.connect(
        os.environ["DATABASE_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def save_run(
    suite_id: str,
    results: list[TestResult],
    drift_score: float,
    status: str,
    regressions: list,
    agent_endpoint: str | None = None,
) -> str:
    run_id = str(uuid.uuid4())

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO test_runs
                    (id, suite_id, timestamp, overall_status, drift_score, regressions, results, agent_endpoint)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    suite_id,
                    datetime.utcnow(),
                    status,
                    drift_score,
                    json.dumps(regressions),
                    json.dumps([r.model_dump() for r in results]),
                    agent_endpoint,
                ),
            )
        conn.commit()

    return run_id


def get_baseline(suite_id: str) -> list[TestResult] | None:
    """Returns results from the most recent PASSED run for this suite."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT results FROM test_runs
                WHERE suite_id = %s AND overall_status = 'PASSED'
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (suite_id,),
            )
            row = cur.fetchone()

    if not row:
        return None

    raw = row["results"]
    data = raw if isinstance(raw, list) else json.loads(raw)
    return [TestResult(**r) for r in data]


def get_run_history(suite_id: str) -> list:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, timestamp, overall_status, drift_score
                FROM test_runs
                WHERE suite_id = %s
                ORDER BY timestamp DESC
                LIMIT 20
                """,
                (suite_id,),
            )
            return cur.fetchall()


def get_all_runs() -> list:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, suite_id, timestamp, overall_status, drift_score, regressions, agent_endpoint
                FROM test_runs
                ORDER BY timestamp DESC
                LIMIT 50
                """
            )
            return cur.fetchall()


def get_run_by_id(run_id: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, suite_id, timestamp, overall_status, drift_score, regressions, results, agent_endpoint
                FROM test_runs
                WHERE id = %s
                """,
                (run_id,),
            )
            return cur.fetchone()


if __name__ == "__main__":
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("db.py OK — DATABASE_URL not set, skipping live connection test")
    else:
        try:
            conn = get_connection()
            conn.close()
            print("db.py OK — connected to Neon successfully")
        except Exception as e:
            print(f"db.py — connection failed: {e}")
