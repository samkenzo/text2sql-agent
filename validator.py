import sqlglot
from sqlglot import exp

# Node types that must never appear anywhere in the query tree.
# Compared by class name so this keeps working across sqlglot versions.
FORBIDDEN = {"Insert", "Update", "Delete", "Drop", "Create", "Alter", "Command",
             "Pragma", "Attach", "Detach", "Merge", "TruncateTable",
             "Transaction", "Commit", "Rollback"}


class UnsafeSQL(Exception):
    pass


def validate_sql(sql: str, allowed_tables: set[str]) -> str:
    """LAYER 2: raise UnsafeSQL unless this is one SELECT on allowed tables."""
    try:
        statements = sqlglot.parse(sql, read="sqlite")
    except sqlglot.errors.SqlglotError as e:
        raise UnsafeSQL(f"Could not parse SQL: {e}")

    statements = [s for s in statements if s is not None]
    if len(statements) != 1:
        raise UnsafeSQL("Exactly one SQL statement is allowed.")

    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Union)):
        raise UnsafeSQL("Only SELECT queries are allowed.")

    for node in tree.find_all(exp.Expression):
        if type(node).__name__ in FORBIDDEN:
            raise UnsafeSQL(f"Forbidden operation: {type(node).__name__}")

    # CTE names (WITH x AS ...) look like tables but aren't real ones.
    cte_names = {cte.alias_or_name for cte in tree.find_all(exp.CTE)}
    for table in tree.find_all(exp.Table):
        if table.name not in allowed_tables and table.name not in cte_names:
            raise UnsafeSQL(f"Table not allowed: {table.name}")

    return sql