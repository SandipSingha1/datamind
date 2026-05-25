import snowflake.connector
from langchain.tools import tool
from langfuse import observe
from dotenv import load_dotenv
import os

load_dotenv("../.env")

def _conn():
    return snowflake.connector.connect(
        account  = os.getenv("SF_ACCOUNT"),
        user     = os.getenv("SF_USER"),
        password = os.getenv("SF_PASSWORD"),
        warehouse= os.getenv("SF_WAREHOUSE", "COMPUTE_WH"),
        database = os.getenv("SF_DATABASE",  "DATAMIND_DB"),
        schema   = os.getenv("SF_SCHEMA",    "PUBLIC"),
        role     = os.getenv("SF_ROLE",      "DATAMIND_ROLE"),
    )

def _run(sql, params=()):
    c = _conn(); cur = c.cursor(); cur.execute(sql, params)
    cols = [d[0].lower() for d in cur.description] if cur.description else []
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    c.close(); return rows

def _scalar(sql, params=()):
    c = _conn(); cur = c.cursor(); cur.execute(sql, params)
    row = cur.fetchone(); c.close()
    return row[0] if row else None

@tool
@observe(name='discover_assets')
def discover_assets(search_term: str) -> list:
    """Find Snowflake tables/views matching a keyword in name or comment."""
    like = f"%{search_term}%"
    return _run(
        "SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE, "
        "COALESCE(ROW_COUNT,0) AS row_count, COALESCE(COMMENT,'') AS comment "
        "FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA') "
        "AND (LOWER(TABLE_NAME) LIKE LOWER(%s) OR LOWER(COMMENT) LIKE LOWER(%s)) "
        "ORDER BY TABLE_NAME LIMIT 20", (like, like))

@tool
@observe(name='snowflake_query')
def run_sf_query(sql: str) -> list:
    """Execute a read-only Snowflake SQL query. Returns rows as list of dicts."""
    return _run(sql)

@tool
@observe(name='cortex_complete')
def cortex_complete(prompt: str) -> str:
    """Ask Snowflake Cortex to answer a prompt using AI."""
    model = os.getenv("CORTEX_MODEL", "snowflake-arctic")
    return _scalar("SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s)", (model, prompt)) or ""

@tool
@observe(name='get_query_costs')
def get_query_costs(days: int = 7) -> list:
    """Return top 20 most expensive Snowflake queries in the last N days."""
    return _run(
        f"SELECT QUERY_ID, LEFT(QUERY_TEXT,200) AS query_text, USER_NAME, "
        f"ROUND(EXECUTION_TIME/1000,2) AS exec_sec, "
        f"ROUND(CREDITS_USED_CLOUD_SERVICES,6) AS credits, "
        f"ROUND(CREDITS_USED_CLOUD_SERVICES*2.0,4) AS est_usd "
        f"FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY "
        f"WHERE START_TIME >= DATEADD('day',{-days},CURRENT_TIMESTAMP()) "
        f"AND EXECUTION_STATUS = 'SUCCESS' "
        f"ORDER BY CREDITS_USED_CLOUD_SERVICES DESC LIMIT 20")
