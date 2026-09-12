# Database setup notes

## Target

Databricks Community Edition (Hive metastore, Delta). No Unity Catalog catalog name is required.

## First-time setup

1. Create a cluster (runtime 13+ or whatever CE currently offers) or use the SQL warehouse for Gold queries.
2. Import this Git repo into Databricks Repos, **or** upload the project zip to Workspace.
3. Upload `data/customers.csv`, `data/orders.csv`, and `data/products.csv` to DBFS:

   ```
   /FileStore/medallion/raw/customers.csv
   /FileStore/medallion/raw/orders.csv
   /FileStore/medallion/raw/products.csv
   ```

   In the UI: Data → Upload, or:

   ```python
   dbutils.fs.cp("file:/Workspace/Repos/<email>/project/data/customers.csv",
                 "dbfs:/FileStore/medallion/raw/customers.csv")
   ```

4. Optional: run `database/schema.sql` in a SQL notebook. The Python jobs also `CREATE DATABASE IF NOT EXISTS` and overwrite tables.

5. In a Python notebook:

   ```python
   import os, sys
   os.environ["MEDALLION_DATABASE"] = "medallion_ecommerce"
   os.environ["MEDALLION_RAW_PATH"] = "/FileStore/medallion/raw"
   sys.path.append("/Workspace/Repos/<your-ttn-email>/project")  # adjust
   from src.bronze.ingest_all import main as bronze_main
   bronze_main()
   ```

   Equivalent: `%run` each script if you convert them to notebooks.

## Idempotency

Bronze, Silver, and Gold curated tables use Delta `overwrite`. Rerunning a layer replaces the table contents. `bronze_ingestion_log` **appends** so you keep an audit trail.

## Local Spark (optional)

If you have PySpark + Delta locally, point `MEDALLION_RAW_PATH` at the repo `data/` directory. Community Edition remains the supported dashboard environment.
