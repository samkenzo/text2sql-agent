import sqlite3
import pytest
from db import get_readonly_connection
from validator import validate_sql, UnsafeSQL

TABLES = {"customers", "products", "orders", "order_items"}


def test_allows_simple_select():
    validate_sql("SELECT COUNT(*) FROM customers", TABLES)


def test_allows_cte():
    validate_sql("WITH t AS (SELECT * FROM orders) SELECT COUNT(*) FROM t", TABLES)


@pytest.mark.parametrize("sql", [
    "DELETE FROM orders",
    "DROP TABLE customers",
    "UPDATE products SET price = 0",
    "INSERT INTO customers VALUES (1)",
    "SELECT 1; DROP TABLE customers",
    "SELECT * FROM sqlite_master",
    "SELECT * FROM secrets",
    "PRAGMA table_info(customers)",
])
def test_blocks_bad_sql(sql):
    with pytest.raises(UnsafeSQL):
        validate_sql(sql, TABLES)


def test_readonly_connection_refuses_writes():
    # Layer 3 works even if layers 1 and 2 are bypassed.
    conn = get_readonly_connection()
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("DELETE FROM orders")