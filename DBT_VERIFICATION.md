# dbt Models Verification Guide

## Current dbt Project Structure ✅

### Sources (Raw Data)
Located in: `models/sources.yml`
- **DATAMIND_DB.RAW.ORDERS** - Raw orders from transactional system
- **DATAMIND_DB.RAW.CUSTOMERS** - Raw customer master data  
- **DATAMIND_DB.RAW.PRODUCTS** - Raw product catalogue

### Staging Models (Views)
Located in: `models/staging/`
1. **stg_customers.sql** - Cleaned customers with full_name, email normalization
2. **stg_orders.sql** - Cleaned orders with status normalization
3. **stg_products.sql** - Cleaned products with category info

### Mart Models (Tables)
Located in: `models/marts/`
1. **fct_orders.sql** - Order fact table joining orders + customers + products
2. **mart_revenue.sql** - Monthly revenue by region and customer segment

## Lineage Flow

```
RAW.ORDERS ──────┐
                 ├──> stg_orders ──┐
RAW.CUSTOMERS ───┼──> stg_customers├──> fct_orders ──> mart_revenue
                 │                 │
RAW.PRODUCTS ────┴──> stg_products─┘
```

## Configuration Check

### 1. profiles.yml ✅
```yaml
datamind_analytics:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: SE58322-FRA00296
      user: DATAMIND_USER
      password: "DataMind@2026!"
      role: DATAMIND_ROLE
      database: DATAMIND_DB
      warehouse: DATAMIND_WH
      schema: DBT_DEV
      threads: 2
```

### 2. dbt_project.yml ✅
- Project name: `datamind_analytics`
- Staging models: materialized as **views**
- Mart models: materialized as **tables**

## Verification Steps

### Step 1: Verify Raw Tables Exist in Snowflake
Run in Snowflake:
```sql
SELECT * FROM DATAMIND_DB.RAW.ORDERS LIMIT 5;
SELECT * FROM DATAMIND_DB.RAW.CUSTOMERS LIMIT 5;
SELECT * FROM DATAMIND_DB.RAW.PRODUCTS LIMIT 5;
```

### Step 2: Compile dbt Models
```bash
cd dbt_project
dbt compile
```
This should create `target/manifest.json`

### Step 3: Run dbt Models
```bash
dbt run
```
This will create:
- Views: `DBT_DEV.stg_customers`, `DBT_DEV.stg_orders`, `DBT_DEV.stg_products`
- Tables: `DBT_DEV.fct_orders`, `DBT_DEV.mart_revenue`

### Step 4: Ingest Metadata into Neo4j
```bash
cd ../datamind_knowledge_svc
python ingestion.py ../dbt_project/target/manifest.json
```

### Step 5: Verify in Neo4j Browser
Open http://localhost:7474 and run:
```cypher
// Count nodes
MATCH (n) RETURN labels(n) as type, count(*) as count

// View dbt models
MATCH (m:DbtModel) RETURN m.name, m.materialization

// View lineage
MATCH (m:DbtModel)-[r:DEPENDS_ON]->(d:DbtModel)
RETURN m.name, type(r), d.name

// View Snowflake tables
MATCH (t:SnowflakeTable) 
RETURN t.database, t.schema, t.name, t.row_count
LIMIT 20
```

## Common Issues & Fixes

### Issue 1: "Source not found"
**Problem:** Raw tables don't exist in Snowflake
**Fix:** Create the raw tables first or adjust `sources.yml` to match existing tables

### Issue 2: "Compilation failed"
**Problem:** profiles.yml not in correct location
**Fix:** Copy `dbt_project/profiles.yml` to `~/.dbt/profiles.yml`

### Issue 3: "No lineage found"
**Problem:** Manifest not ingested into Neo4j
**Fix:** Run `python ingestion.py ../dbt_project/target/manifest.json`

### Issue 4: "Database/Schema not found"
**Problem:** Target schema doesn't exist
**Fix:** Create schema in Snowflake:
```sql
CREATE SCHEMA IF NOT EXISTS DATAMIND_DB.DBT_DEV;
CREATE SCHEMA IF NOT EXISTS DATAMIND_DB.RAW;
```

## Testing Queries in DataMind Chat

Once everything is set up, try these in the Streamlit app:

1. **Discovery:** "Find tables related to orders"
2. **Lineage:** "Show lineage for fct_orders"
3. **Generation:** "Generate a dbt model for monthly revenue by product category"
4. **Cost:** "Which queries cost the most?"

## Expected Neo4j Node Counts

After successful ingestion:
- **DbtModel nodes:** 5 (stg_customers, stg_orders, stg_products, fct_orders, mart_revenue)
- **SnowflakeTable nodes:** Varies (depends on your Snowflake tables)
- **SnowflakeColumn nodes:** Varies (all columns from all tables)
- **DEPENDS_ON relationships:** 6 (model dependencies)
- **HAS_COLUMN relationships:** Many (table-to-column links)

## Next Steps

1. ✅ Verify raw tables exist in Snowflake
2. ✅ Run `dbt compile` to generate manifest
3. ✅ Run `dbt run` to create models
4. ✅ Run ingestion script to load into Neo4j
5. ✅ Start all 3 services (core, knowledge, frontend)
6. ✅ Test queries in the chat interface

---
**Note:** Your dbt models are well-structured and follow best practices! The issue is likely in the setup/ingestion steps, not the model definitions.