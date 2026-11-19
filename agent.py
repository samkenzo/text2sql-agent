import re
import sqlite3
from db import get_readonly_connection, get_schema, run_query
from llm import ask_llm
from validator import validate_sql, UnsafeSQL

# Business definitions the schema can't express. Without these, "revenue"
# is ambiguous and the model will guess differently each time.
RULES = """- Revenue = SUM(order_items.quantity * order_items.unit_price), counting ONLY orders whose status is 'completed'.
- Dates are ISO text 'YYYY-MM-DD'; use SQLite functions like strftime('%Y', order_date).
- 'Order value' means the total of an order's line items (quantity * unit_price)."""

SYSTEM_TEMPLATE = """You are an expert at writing SQLite queries.
Translate the user's question into ONE SQLite SELECT query.

Database schema:
{schema}

Business rules:
{rules}

Output rules:
- Return ONLY the SQL. No explanation, no markdown.
- Use only tables and columns that exist in the schema.
- Return only the columns the question asks for, in the order they are mentioned.
- Never write INSERT, UPDATE, DELETE, DROP or anything that changes data."""


def clean_sql(text: str) -> str:
    """Models sometimes wrap SQL in markdown fences or <think> blocks. Strip them."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1)
    return text.strip().rstrip(";").strip()


def answer_question(question, conn, schema, tables, max_retries=2):
    system = SYSTEM_TEMPLATE.format(schema=schema, rules=RULES)
    user = f"Question: {question}"
    sql, error = "", None

    for attempt in range(max_retries + 1):
        sql = clean_sql(ask_llm(system, user))
        try:
            validate_sql(sql, tables)               # layer 2: parser
            columns, rows = run_query(conn, sql)    # layer 3: read-only connection
            return {"sql": sql, "columns": columns, "rows": rows,
                    "error": None, "attempts": attempt + 1}
        except UnsafeSQL as e:
            error = f"Rejected by safety check: {e}"
        except sqlite3.Error as e:
            error = f"SQLite error: {e}"
        # The "agent" part: show the model its own mistake and let it fix it.
        user = (f"Question: {question}\n\nYour previous SQL:\n{sql}\n\n"
                f"It failed: {error}\nWrite a corrected query.")

    return {"sql": sql, "columns": [], "rows": [], "error": error,
            "attempts": max_retries + 1}


def main():
    conn = get_readonly_connection()
    schema, tables = get_schema(conn)
    print("Ask your database. Type 'quit' to exit.")
    while True:
        question = input("\n> ").strip()
        if question.lower() in {"quit", "exit", ""}:
            break
        out = answer_question(question, conn, schema, tables)
        print(f"\nSQL: {out['sql']}  (attempts: {out['attempts']})")
        if out["error"]:
            print("Failed:", out["error"])
        else:
            print(out["columns"])
            for row in out["rows"]:
                print(row)


if __name__ == "__main__":
    main()