import os

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


load_dotenv()

CONFLICT_KEYS = {
    "sales": ["transaction_id", "customer_id", "item_id"],
    "daily_sales": ["billing_date"],
    "monthly_sales": ["month"],
    "top_items": ["item_id"],
}


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def load_table(df, table_name, connection):
    if df.empty:
        return

    columns = list(df.columns)
    conflict_keys = CONFLICT_KEYS[table_name]
    update_columns = [column for column in columns if column not in conflict_keys]

    insert_sql = f"""
        INSERT INTO {table_name} ({", ".join(columns)})
        VALUES %s
        ON CONFLICT ({", ".join(conflict_keys)})
        DO UPDATE SET {", ".join(f"{column} = EXCLUDED.{column}" for column in update_columns)}
    """

    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]

    with connection.cursor() as cursor:
        execute_values(cursor, insert_sql, rows)

    connection.commit()


def create_tables():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            with open("sql/schema.sql", "r") as file:
                schema = file.read()

            cursor.execute(schema)

        connection.commit()

        print("Tables created successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()