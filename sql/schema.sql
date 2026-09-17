CREATE TABLE IF NOT EXISTS sales (
    transaction_id VARCHAR(100),
    customer_id VARCHAR(100),
    billing_date DATE,
    store_id VARCHAR(100),
    region VARCHAR(100),
    item_id VARCHAR(100),
    item_name VARCHAR(255),
    category VARCHAR(100),
    quantity INTEGER,
    unit_price NUMERIC(12, 2),
    discount NUMERIC(12, 2),
    total_amount NUMERIC(12, 2),

    UNIQUE (
        transaction_id,
        customer_id,
        item_id
    )
);


CREATE TABLE IF NOT EXISTS daily_sales (
    billing_date DATE PRIMARY KEY,
    total_quantity INTEGER,
    total_revenue NUMERIC(14, 2),
    total_transactions INTEGER
);


CREATE TABLE IF NOT EXISTS monthly_sales (
    month VARCHAR(7) PRIMARY KEY,
    total_quantity INTEGER,
    total_revenue NUMERIC(14, 2),
    total_transactions INTEGER
);


CREATE TABLE IF NOT EXISTS top_items (
    item_id VARCHAR(100) PRIMARY KEY,
    item_name VARCHAR(255),
    total_quantity INTEGER,
    total_revenue NUMERIC(14, 2),
    rank INTEGER
);