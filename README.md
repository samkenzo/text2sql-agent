# Text-to-SQL Agent

Ask a SQLite database questions in English. An LLM writes the SQL, which is
validated and run on a read-only connection.

## How it works
question → LLM (schema + rules in prompt) → sqlglot validation → read-only execution → result
On error, the failure message goes back to the LLM for up to 2 retries.

## Safety layers
1. Prompt instructs SELECT-only (not relied on)
2. sqlglot parser: single statement, SELECT only, table allowlist
3. Read-only SQLite connection + row cap + 5s timeout
Tested in `test_validator.py`.

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
python make_db.py
python agent.py
```

## Evaluation
30 questions with gold SQL (easy/medium/hard), scored by comparing result rows.
`python run_eval.py`

| Version | Model | Easy | Medium | Hard | Overall |
|---|---|---|---|---|---|
| Baseline | ... | /10 | /10 | /10 | /30 |
| + business rules | ... | | | | |

## What failed and why
(2-3 honest examples)

## Limitations
- Strict result matching; only one database; no conversation memory