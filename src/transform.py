import pandas as pd

def clean_data(df):
    validation_errors = []
    try:
        if not isinstance(df, pd.DataFrame):
            raise Exception("Invalid data frame")
        
        df["billing_date"] = pd.to_datetime(df["billing_date"], errors="coerce", format="mixed")
        df["discount"] = df["discount"].fillna(0)
        df["category"] = df["category"].fillna("Unknown")
        df = df[df["quantity"] > 0]
        df = df[df["unit_price"] > 0]
        df = df.dropna(subset=["billing_date"])
        df = df.drop_duplicates(subset=["transaction_id", "customer_id", "item_id"],keep="first")
        return df
    except Exception as e:
        print(f"Error. {str(e)}")
        return False

    
def create_daily_sales(df):
    try:
        if not isinstance(df, pd.DataFrame):
            raise Exception("Invalid data frame")
        daily_sales = (
            df.groupby("billing_date")
            .agg(
                total_quantity=("quantity", "sum"),
                total_revenue=("total_amount", "sum"),
                total_transactions=("transaction_id", "nunique"),
            )
            .reset_index()
        )
        return daily_sales
    except Exception as e:
        print(f"Error. {str(e)}")
        return False
    
def create_monthly_sales(df):
    try:
        if not isinstance(df, pd.DataFrame):
            raise Exception("Invalid data frame")
        month = df["billing_date"].dt.to_period("M").astype(str).rename("month")
        monthly_sales = (
            df.groupby(month)
            .agg(
                total_quantity=("quantity", "sum"),
                total_revenue=("total_amount", "sum"),
                total_transactions=("transaction_id", "nunique"),
            )
            .reset_index()
        )
        return monthly_sales
    except Exception as e:
        print(f"Error. {str(e)}")
        return False
    
def create_top_items(df):
    try:
        if not isinstance(df, pd.DataFrame):
            raise Exception("Invalid data frame")
        top_items = (
            df.groupby("item_id")
            .agg(
                item_name=("item_name", "first"),
                total_quantity=("quantity", "sum"),
                total_revenue=("total_amount", "sum"),
            )
            .reset_index()
            .sort_values(
                "total_revenue",
                ascending=False
            )
        )
        top_items["rank"] = (
            top_items["total_revenue"]
            .rank(method="dense", ascending=False)
            .astype(int)
        )
        return top_items
    except Exception as e:
        print(f"Error. {str(e)}")
        return False