# Sales Data Pipeline

Small ETL pipeline for the sales dataset assignment. Pulls the raw CSV, validates it, cleans it up, builds daily/monthly/top-item rollups, and pushes everything into Postgres.

## Layout

```
.
├── data/
│   ├── raw/            # source CSV (assignment_dataset.csv)
│   └── processed/      # cleaned + aggregated CSV output
├── sql/
│   └── schema.sql      # table definitions
├── src/
│   ├── extract.py      # reads the CSV
│   ├── validation.py   # data quality checks
│   ├── transform.py    # cleaning + aggregation
│   ├── load.py         # db connection + upsert loader
│   └── pipeline.py     # runs the whole thing
├── docker/
│   └── docker-compose.yml   # Postgres container
├── requirements.txt
└── .env.example
```

## Getting it running

Spin up Postgres first:

```bash
docker compose -f docker/docker-compose.yml up -d
```

That gives you Postgres on `localhost:5433` with a `sales_db` database (check `docker/docker-compose.yml` if you want to change the port/creds).

Then the usual venv + install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the env file and adjust it if you changed anything in `docker/docker-compose.yml`:

```bash
cp .env.example .env
```

Create the tables (this just runs `sql/schema.sql` against the db):

```bash
python src/load.py
```

Now run the pipeline:

```bash
python src/pipeline.py
```

If it worked you'll see `Pipeline completed successfully.` at the end. Along the way it also prints out any validation issues it found in the raw data (see below), writes the cleaned/aggregated tables to `data/processed/` as CSVs, and upserts them into Postgres.

## About the data validation

`validate_data()` in `src/validation.py` only reports problems, it doesn't fix or drop anything — the actual cleanup happens later in `clean_data()`. What it checks:

- all expected columns are present (`required_columns`)
- no nulls in the fields that actually matter — ids, date, quantity, price, etc. (`required_fields`)
- no zero/negative `quantity`
- no zero/negative `unit_price`

It returns `status: 1` even when it finds issues — those are just warnings that get logged. `status: 0` only happens if validation itself blew up (e.g. you didn't pass it a DataFrame), and that's the one case `pipeline.py` treats as fatal and stops the run.

A couple of things worth knowing about the raw dataset specifically:
- `billing_date` shows up in at least three different formats (`YYYY-MM-DD`, `YYYY/MM/DD`, `DD-MM-YYYY`) mixed in the same column. Parsing this with plain `pd.to_datetime()` silently locks onto one format and nulls out everything else — had to use `format="mixed"` to parse each row on its own.
- some `item_id`s show up with more than one `item_name` in the source data (looks like a data entry inconsistency). `create_top_items` groups by `item_id` only and just keeps whichever name comes first, since `item_id` is the actual primary key.

## Cleaning (`clean_data`)

- parses `billing_date`, drops rows that still don't parse
- fills missing `discount` with 0, missing `category` with "Unknown"
- drops rows with `quantity <= 0` or `unit_price <= 0`
- dedupes on `(transaction_id, customer_id, item_id)`, keeping the first row — matches the unique constraint on the `sales` table

## Loading

Everything goes in with `INSERT ... ON CONFLICT DO UPDATE`, so re-running the pipeline on the same data updates rows instead of erroring out on duplicates. Conflict key per table:

- `sales` → `transaction_id, customer_id, item_id`
- `daily_sales` → `billing_date`
- `monthly_sales` → `month`
- `top_items` → `item_id`
