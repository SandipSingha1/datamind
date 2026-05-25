from graph.state import DataMindState
from tools.snowflake_tool import _run as sf_run, cortex_complete
from langfuse import observe

@observe(name="cost_agent")
def cost_agent_node(state):
    query = state["user_query"]

    # Call Snowflake directly — bypass LangChain tool wrapper
    try:
        costs = sf_run(
            "SELECT QUERY_ID, LEFT(QUERY_TEXT,200) AS query_text, USER_NAME,"
            " ROUND(EXECUTION_TIME/1000,2) AS exec_sec,"
            " ROUND(CREDITS_USED_CLOUD_SERVICES,6) AS credits,"
            " ROUND(CREDITS_USED_CLOUD_SERVICES*2.0,4) AS est_usd"
            " FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY"
            " WHERE START_TIME>=DATEADD('day',-7,CURRENT_TIMESTAMP())"
            " AND EXECUTION_STATUS='SUCCESS'"
            " ORDER BY CREDITS_USED_CLOUD_SERVICES DESC LIMIT 20"
        )
    except Exception as e:
        costs = []

    if not costs:
        summary = "No query cost data found for the last 7 days."
    else:
        summary = "\n".join(
            f"{i+1}. [{r.get('exec_sec',0)}s | ${r.get('est_usd',0)}] {r.get('query_text','')[:80]}..."
            for i, r in enumerate(costs[:5])
        )

    tips = cortex_complete.run(
        f"Top expensive Snowflake queries:\n{summary}\n\n"
        f"Question: {query}\n\n"
        f"For each query: root cause and one specific optimization. Be concise."
    )

    answer = f"**Top costly queries — last 7 days:**\n\n{summary}\n\n**Optimization tips:**\n\n{tips}"
    return {**state, "cost_result": {"queries": costs, "tips": tips}, "answer": answer}