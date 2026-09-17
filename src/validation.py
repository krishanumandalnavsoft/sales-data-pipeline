import pandas as pd

required_columns = ["transaction_id","customer_id","billing_date","store_id","region","item_id","item_name","category","quantity","unit_price","discount","total_amount"]

required_fields = ["transaction_id","customer_id","billing_date","store_id","region","item_id","item_name","quantity","unit_price","total_amount"]

def validate_data(df):
    validation_errors = []
    try:
        if not isinstance(df, pd.DataFrame):
            raise Exception("Invalid data frame")
        
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            validation_errors.append(f"Missing columns: {missing_columns}")
            
        for column in required_fields:
            null_data_count = df[column].isna().sum()
            if null_data_count > 0:
                validation_errors.append(f"{column} contains {null_data_count} null values")
                
        if (df["quantity"] <= 0).any():
            validation_errors.append("Quantity contains zero or negative values")

        if (df["unit_price"] <= 0).any():
            validation_errors.append("Unit price contains zero or negative values")
            
        return {"validation_errors":validation_errors,"status":1}
    except Exception as e:
        return {"validation_errors":validation_errors,"status":0,"message":str(e)}

    