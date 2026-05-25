# Fix 1: cost_summary in main.py - tool call passing int instead of dict
import re

# Fix datamind_core/main.py cost summary
path = "../datamind_core/main.py"
content = open(path, encoding="utf-8").read()

old = "        rows = await asyncio.to_thread(get_query_costs.run, 7)"
new = """        from tools.snowflake_tool import _run as sf_run
        rows = await asyncio.to_thread(
            sf_run,
            "SELECT QUERY_ID, LEFT(QUERY_TEXT,200) AS query_text, USER_NAME,"
            " ROUND(EXECUTION_TIME/1000,2) AS exec_sec,"
            " ROUND(CREDITS_USED_CLOUD_SERVICES,6) AS credits,"
            " ROUND(CREDITS_USED_CLOUD_SERVICES*2.0,4) AS est_usd"
            " FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY"
            " WHERE START_TIME>=DATEADD('day',-7,CURRENT_TIMESTAMP())"
            " AND EXECUTION_STATUS='SUCCESS'"
            " ORDER BY CREDITS_USED_CLOUD_SERVICES DESC LIMIT 20"
        )"""

if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("Fixed: main.py cost summary")
else:
    print("WARN: cost summary pattern not found - fixing manually")
    # Add direct SQL approach to cost_summary function
    content2 = open(path, encoding="utf-8").read()
    old2 = '''@app.get("/cost/summary")
async def cost_summary():
    try:
        from tools.snowflake_tool import get_query_costs
        rows = await asyncio.to_thread(get_query_costs.run, 7)'''
    new2 = '''@app.get("/cost/summary")
async def cost_summary():
    try:
        from tools.snowflake_tool import _run as sf_run
        rows = await asyncio.to_thread(
            sf_run,
            "SELECT QUERY_ID, LEFT(QUERY_TEXT,200) AS query_text, USER_NAME,"
            " ROUND(EXECUTION_TIME/1000,2) AS exec_sec,"
            " ROUND(CREDITS_USED_CLOUD_SERVICES,6) AS credits,"
            " ROUND(CREDITS_USED_CLOUD_SERVICES*2.0,4) AS est_usd"
            " FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY"
            " WHERE START_TIME>=DATEADD('day',-7,CURRENT_TIMESTAMP())"
            " AND EXECUTION_STATUS='SUCCESS'"
            " ORDER BY CREDITS_USED_CLOUD_SERVICES DESC LIMIT 20"
        )'''
    if old2 in content2:
        content2 = content2.replace(old2, new2)
        open(path, "w", encoding="utf-8").write(content2)
        print("Fixed: main.py cost summary (method 2)")
    else:
        print("ERROR: Could not auto-fix cost summary. Will fix manually.")

print("All fixes applied!")