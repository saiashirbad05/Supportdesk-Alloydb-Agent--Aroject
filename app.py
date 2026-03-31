import os

from flask import Flask, jsonify, request
import psycopg2
import psycopg2.extras


app = Flask(__name__)

DB_HOST = os.environ.get("INSTANCE_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "supportdesk")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "")
NL_CONFIG_ID = os.environ.get("NL_CONFIG_ID", "supportdesk_cfg")


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=10,
    )


@app.get("/")
def root():
    return jsonify(
        {
            "service": "supportdesk-nl-api",
            "status": "running",
            "endpoints": [
                "/health",
                "/healthz",
                "/demo/payments-open",
                "/demo/unresolved-by-service",
                "/demo/critical-auth",
                "/ask",
            ],
        }
    )


@app.get("/health")
@app.get("/healthz")
def health():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT current_database(), now()")
        row = cur.fetchone()
        cur.close()
        conn.close()
        return (
            jsonify(
                {
                    "status": "healthy",
                    "database": row[0],
                    "timestamp": str(row[1]),
                    "db_host": DB_HOST,
                }
            ),
            200,
        )
    except Exception as exc:
        return jsonify({"status": "unhealthy", "error": str(exc)}), 500


@app.get("/demo/payments-open")
def demo_payments_open():
    sql = """
        SELECT ticket_id, customer_name, service_name, priority, status,
               created_at::text AS created_at, assigned_engineer
        FROM app.support_tickets
        WHERE service_name = 'payments'
          AND status = 'Open'
          AND priority IN ('High', 'Critical')
          AND created_at >= TIMESTAMP '2026-03-01 00:00:00'
        ORDER BY created_at ASC
    """
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        rows = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(
            {
                "query": "Show open high or critical tickets for payments service created on or after 2026-03-01.",
                "count": len(rows),
                "results": rows,
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/demo/unresolved-by-service")
def demo_unresolved_by_service():
    sql = """
        SELECT service_name, COUNT(*) AS unresolved_count
        FROM app.support_tickets
        WHERE status IN ('Open', 'In Progress')
        GROUP BY service_name
        ORDER BY unresolved_count DESC, service_name ASC
    """
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        rows = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(
            {
                "query": "Unresolved tickets by service",
                "count": len(rows),
                "results": rows,
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/demo/critical-auth")
def demo_critical_auth():
    sql = """
        SELECT assigned_engineer, ticket_id, issue_summary
        FROM app.support_tickets
        WHERE service_name = 'auth'
          AND priority = 'Critical'
          AND status = 'Open'
    """
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        rows = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(
            {
                "query": "Critical open auth tickets",
                "count": len(rows),
                "results": rows,
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/ask")
def ask():
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Missing JSON field: question"}), 400

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT alloydb_ai_nl.get_sql(%s, %s) ->> 'sql'",
            (NL_CONFIG_ID, question),
        )
        row = cur.fetchone()
        generated_sql = row[0] if row else None

        if not generated_sql:
            cur.close()
            conn.close()
            return jsonify({"question": question, "error": "No SQL was generated."}), 500

        if not generated_sql.lstrip().lower().startswith("select"):
            cur.close()
            conn.close()
            return (
                jsonify(
                    {
                        "question": question,
                        "generated_sql": generated_sql,
                        "error": "Only SELECT statements are allowed.",
                    }
                ),
                400,
            )

        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        dict_cur.execute(generated_sql)
        rows = [dict(result) for result in dict_cur.fetchall()]
        dict_cur.close()
        cur.close()
        conn.close()

        return jsonify(
            {
                "question": question,
                "generated_sql": generated_sql,
                "row_count": len(rows),
                "results": rows,
            }
        )
    except Exception as exc:
        return jsonify({"question": question, "error": str(exc)}), 500


@app.errorhandler(404)
def not_found(_exc):
    return (
        jsonify(
            {
                "error": "Not found",
                "available_routes": [
                    "/",
                    "/health",
                    "/healthz",
                    "/demo/payments-open",
                    "/demo/unresolved-by-service",
                    "/demo/critical-auth",
                    "/ask",
                ],
            }
        ),
        404,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)
