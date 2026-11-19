import json
import time
from agent import answer_question
from db import get_readonly_connection, get_schema
from llm import MODEL
from questions import QUESTIONS


def normalize(rows, ordered):
    """Round floats, and ignore row order unless the question demands an order."""
    norm = [tuple(round(v, 2) if isinstance(v, float) else v for v in row) for row in rows]
    return norm if ordered else sorted(norm, key=repr)


def main():
    conn = get_readonly_connection()
    schema, tables = get_schema(conn)
    results = []

    for i, (question, gold_sql, ordered) in enumerate(QUESTIONS, start=1):
        gold_rows = conn.execute(gold_sql).fetchall()
        if not gold_rows:
            print(f"WARNING Q{i}: gold SQL returns nothing, so this is a weak test")

        out = answer_question(question, conn, schema, tables)
        ok = (out["error"] is None and
              normalize(out["rows"], ordered) == normalize(gold_rows, ordered))
        results.append({"n": i, "question": question, "ok": ok, "model_sql": out["sql"],
                        "gold_sql": gold_sql, "error": out["error"], "attempts": out["attempts"]})
        print(f"Q{i:02d} {'PASS' if ok else 'FAIL'}  {question}")
        if not ok:
            print("      model:", out["sql"])
            print("      error:", out["error"])
            print("      got  :", out["rows"][:3])
            print("      want :", gold_rows[:3])
        time.sleep(1)  # be kind to the free tier's rate limits

    total = sum(r["ok"] for r in results)
    print(f"\nModel: {MODEL}")
    print(f"Overall: {total}/{len(results)} = {100 * total / len(results):.0f}%")
    for name, (a, b) in {"easy": (0, 10), "medium": (10, 20), "hard": (20, 30)}.items():
        chunk = results[a:b]
        print(f"  {name}: {sum(r['ok'] for r in chunk)}/{len(chunk)}")

    with open("results.json", "w") as f:
        json.dump({"model": MODEL, "results": results}, f, indent=2)


if __name__ == "__main__":
    main()