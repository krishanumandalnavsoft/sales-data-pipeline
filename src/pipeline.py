import os

from extract import extract_data
from validation import validate_data
from transform import clean_data, create_daily_sales, create_monthly_sales, create_top_items
from load import get_connection, load_table


def run_pipeline():
    df = extract_data("data/raw/assignment_dataset.csv")
    data_validation = validate_data(df)
    if data_validation['status'] == 0:
        print(f"Error while validating the data set. Error: {data_validation['message']}")
        return False

    if data_validation['validation_errors']:
        print("Validation issues found:")
        for error in data_validation['validation_errors']:
            print(f"- {error}")

    cleaned_df = clean_data(df)
    daily_sales = create_daily_sales(cleaned_df)
    monthly_sales = create_monthly_sales(cleaned_df)
    top_items = create_top_items(cleaned_df)

    os.makedirs("data/processed", exist_ok=True)
    cleaned_df.to_csv("data/processed/sales.csv", index=False)
    daily_sales.to_csv("data/processed/daily_sales.csv", index=False)
    monthly_sales.to_csv("data/processed/monthly_sales.csv", index=False)
    top_items.to_csv("data/processed/top_items.csv", index=False)

    connection = get_connection()
    try:
        load_table(cleaned_df, "sales", connection)
        load_table(daily_sales, "daily_sales", connection)
        load_table(monthly_sales, "monthly_sales", connection)
        load_table(top_items, "top_items", connection)
    finally:
        connection.close()

    print("Pipeline completed successfully.")
    return True


if __name__ == "__main__":
    run_pipeline()