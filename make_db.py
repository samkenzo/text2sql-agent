"""Create a small, reproducible shop database (shop.db)."""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

random.seed(42)  # same data every run, so eval answers stay stable
DB_PATH = Path(__file__).parent / "shop.db"

# Comments inside CREATE TABLE are stored by SQLite, so the LLM will see them.
SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    city        TEXT NOT NULL,
    country     TEXT NOT NULL,
    signup_date TEXT NOT NULL   -- ISO date 'YYYY-MM-DD'
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    category   TEXT NOT NULL,   -- Electronics, Books, Clothing, Home, Sports
    price      REAL NOT NULL    -- current list price in INR
);
CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date  TEXT NOT NULL,  -- ISO date 'YYYY-MM-DD'
    status      TEXT NOT NULL   -- completed, cancelled, refunded, pending
);
CREATE TABLE order_items (
    item_id    INTEGER PRIMARY KEY,
    order_id   INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity   INTEGER NOT NULL,
    unit_price REAL NOT NULL    -- price paid per unit at purchase time, INR
);
"""

FIRST = ["Aarav", "Diya", "Rohan", "Meera", "Kabir", "Ananya", "Vikram", "Isha", "Arjun", "Sara"]
LAST = ["Sharma", "Patel", "Khan", "Iyer", "Singh", "Das", "Reddy", "Gupta", "Joshi", "Nair"]
LOCATIONS = [("Mumbai", "India"), ("Delhi", "India"), ("Bengaluru", "India"),
             ("Pune", "India"), ("Chennai", "India"), ("Nagpur", "India"),
             ("New York", "USA"), ("Austin", "USA"), ("London", "UK")]

CATEGORIES = {  # category: (min price, max price, product names)
    "Electronics": (999, 29999, ["Wireless Earbuds", "Smartwatch", "Bluetooth Speaker",
                                 "Power Bank", "Webcam", "Mechanical Keyboard"]),
    "Books": (199, 1499, ["Python Crash Course", "Deep Learning Basics", "Data Science Handbook",
                          "Sci-Fi Anthology", "Cooking Made Easy", "Startup Playbook"]),
    "Clothing": (499, 3999, ["Cotton T-Shirt", "Denim Jacket", "Running Shorts",
                             "Wool Sweater", "Formal Shirt", "Rain Jacket"]),
    "Home": (299, 7999, ["Table Lamp", "Cushion Set", "Coffee Maker",
                         "Wall Clock", "Bedsheet Set", "Storage Box"]),
    "Sports": (199, 5999, ["Yoga Mat", "Dumbbell Set", "Cricket Bat",
                           "Football", "Skipping Rope", "Water Bottle"]),
}
STATUSES = ["completed"] * 6 + ["cancelled"] * 2 + ["refunded", "pending"]


def main():
    DB_PATH.unlink(missing_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    # 40 customers with unique names
    combos = random.sample([(f, l) for f in FIRST for l in LAST], 40)
    customers = []
    for i, (f, l) in enumerate(combos, start=1):
        city, country = random.choice(LOCATIONS)
        signup = date(2024, 1, 1) + timedelta(days=random.randint(0, 540))
        customers.append((i, f"{f} {l}", f"{f.lower()}.{l.lower()}{i}@example.com",
                          city, country, signup.isoformat()))

    # 30 products
    products, pid = [], 1
    for category, (lo, hi, names) in CATEGORIES.items():
        for name in names:
            products.append((pid, name, category, round(random.uniform(lo, hi), 2)))
            pid += 1

    # Only the first 35 customers order, and the last 4 products are never
    # ordered. This gives us "never ordered" questions with real answers.
    active_customers = customers[:35]
    orderable_products = products[:-4]
    signup_by_id = {c[0]: date.fromisoformat(c[5]) for c in customers}

    order_rows, item_rows = [], []
    for order_id in range(1, 201):
        cust = random.choice(active_customers)
        order_date = signup_by_id[cust[0]] + timedelta(days=random.randint(0, 500))
        order_rows.append((order_id, cust[0], order_date.isoformat(), random.choice(STATUSES)))
        for p in random.sample(orderable_products, random.randint(1, 4)):
            item_rows.append((None, order_id, p[0], random.randint(1, 3), p[3]))

    conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?)", customers)
    conn.executemany("INSERT INTO products VALUES (?,?,?,?)", products)
    conn.executemany("INSERT INTO orders VALUES (?,?,?,?)", order_rows)
    conn.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", item_rows)
    conn.commit()

    for t in ("customers", "products", "orders", "order_items"):
        print(t, conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0], "rows")
    conn.close()


if __name__ == "__main__":
    main()