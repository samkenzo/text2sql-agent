REV = "oi.quantity * oi.unit_price"

QUESTIONS = [
    # ---------- Easy: single table ----------
    ("How many customers are there?",
     "SELECT COUNT(*) FROM customers", False),
    ("How many products are in the Electronics category?",
     "SELECT COUNT(*) FROM products WHERE category = 'Electronics'", False),
    ("List the names of customers who live in Pune.",
     "SELECT name FROM customers WHERE city = 'Pune'", False),
    ("What is the name and price of the most expensive product?",
     "SELECT name, price FROM products ORDER BY price DESC LIMIT 1", False),
    ("How many orders have the status cancelled?",
     "SELECT COUNT(*) FROM orders WHERE status = 'cancelled'", False),
    ("How many customers are from India?",
     "SELECT COUNT(*) FROM customers WHERE country = 'India'", False),
    ("What is the average product price, rounded to 2 decimals?",
     "SELECT ROUND(AVG(price), 2) FROM products", False),
    ("How many orders were placed in 2026?",
     "SELECT COUNT(*) FROM orders WHERE strftime('%Y', order_date) = '2026'", False),
    ("List all distinct product categories.",
     "SELECT DISTINCT category FROM products", False),
    ("How many customers signed up in 2025?",
     "SELECT COUNT(*) FROM customers WHERE strftime('%Y', signup_date) = '2025'", False),

    # ---------- Medium: joins and grouping ----------
    ("How many customers does each country have? Return country and count.",
     "SELECT country, COUNT(*) FROM customers GROUP BY country", False),
    ("List the names of customers who have at least one cancelled order.",
     "SELECT DISTINCT c.name FROM customers c JOIN orders o ON o.customer_id = c.customer_id "
     "WHERE o.status = 'cancelled'", False),
    ("What is the total quantity of items sold in completed orders?",
     "SELECT SUM(oi.quantity) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id "
     "WHERE o.status = 'completed'", False),
    ("What is the total revenue, rounded to 2 decimals?",
     f"SELECT ROUND(SUM({REV}), 2) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id "
     "WHERE o.status = 'completed'", False),
    ("What is the revenue per product category, highest first? Return category and revenue rounded to 2 decimals.",
     f"SELECT p.category, ROUND(SUM({REV}), 2) AS revenue FROM order_items oi "
     "JOIN orders o ON o.order_id = oi.order_id JOIN products p ON p.product_id = oi.product_id "
     "WHERE o.status = 'completed' GROUP BY p.category ORDER BY revenue DESC", True),
    ("Who are the top 3 customers by revenue? Return name and revenue rounded to 2 decimals.",
     f"SELECT c.name, ROUND(SUM({REV}), 2) AS revenue FROM customers c "
     "JOIN orders o ON o.customer_id = c.customer_id JOIN order_items oi ON oi.order_id = o.order_id "
     "WHERE o.status = 'completed' GROUP BY c.customer_id ORDER BY revenue DESC LIMIT 3", True),
    ("Which products have never been ordered? Return the product names.",
     "SELECT p.name FROM products p LEFT JOIN order_items oi ON oi.product_id = p.product_id "
     "WHERE oi.item_id IS NULL", False),
    ("Which customers have never placed an order? Return their names.",
     "SELECT name FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM orders)", False),
    ("How many orders are there for each status? Return status and count.",
     "SELECT status, COUNT(*) FROM orders GROUP BY status", False),
    ("What is the average order value for completed orders, rounded to 2 decimals?",
     f"SELECT ROUND(AVG(order_total), 2) FROM (SELECT SUM({REV}) AS order_total FROM orders o "
     "JOIN order_items oi ON oi.order_id = o.order_id WHERE o.status = 'completed' "
     "GROUP BY o.order_id)", False),

    # ---------- Hard: subqueries, dates, multi-join ----------
    ("What was the revenue for each month of 2026? Return month as YYYY-MM and revenue rounded to 2 decimals, ordered by month.",
     f"SELECT strftime('%Y-%m', o.order_date) AS month, ROUND(SUM({REV}), 2) AS revenue "
     "FROM orders o JOIN order_items oi ON oi.order_id = o.order_id "
     "WHERE o.status = 'completed' AND strftime('%Y', o.order_date) = '2026' "
     "GROUP BY month ORDER BY month", True),
    ("Which country has the highest revenue? Return country and revenue rounded to 2 decimals.",
     f"SELECT c.country, ROUND(SUM({REV}), 2) AS revenue FROM customers c "
     "JOIN orders o ON o.customer_id = c.customer_id JOIN order_items oi ON oi.order_id = o.order_id "
     "WHERE o.status = 'completed' GROUP BY c.country ORDER BY revenue DESC LIMIT 1", False),
    ("Which customers have ordered products from more than 2 different categories (any order status)? Return names.",
     "SELECT c.name FROM customers c JOIN orders o ON o.customer_id = c.customer_id "
     "JOIN order_items oi ON oi.order_id = o.order_id JOIN products p ON p.product_id = oi.product_id "
     "GROUP BY c.customer_id HAVING COUNT(DISTINCT p.category) > 2", False),
    ("Which product generated the most revenue? Return name and revenue rounded to 2 decimals.",
     f"SELECT p.name, ROUND(SUM({REV}), 2) AS revenue FROM products p "
     "JOIN order_items oi ON oi.product_id = p.product_id JOIN orders o ON o.order_id = oi.order_id "
     "WHERE o.status = 'completed' GROUP BY p.product_id ORDER BY revenue DESC LIMIT 1", False),
    ("How many customers placed more than 5 orders (any status)?",
     "SELECT COUNT(*) FROM (SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) > 5)", False),
    ("What percentage of all orders are cancelled, rounded to 1 decimal?",
     "SELECT ROUND(100.0 * SUM(status = 'cancelled') / COUNT(*), 1) FROM orders", False),
    ("Which products cost more than the average price of their own category? Return names.",
     "SELECT p.name FROM products p WHERE p.price > "
     "(SELECT AVG(price) FROM products WHERE category = p.category)", False),
    ("For each category, how many distinct customers bought from it in completed orders? Return category and count.",
     "SELECT p.category, COUNT(DISTINCT o.customer_id) FROM order_items oi "
     "JOIN orders o ON o.order_id = oi.order_id JOIN products p ON p.product_id = oi.product_id "
     "WHERE o.status = 'completed' GROUP BY p.category", False),
    ("How many orders contain more than 3 line items?",
     "SELECT COUNT(*) FROM (SELECT order_id FROM order_items GROUP BY order_id HAVING COUNT(*) > 3)", False),
    ("Which cities have more than 3 customers? Return city and customer count.",
     "SELECT city, COUNT(*) FROM customers GROUP BY city HAVING COUNT(*) > 3", False),
]