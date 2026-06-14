from agent.tools.duckduckgo_search import multi_search
import logging

logger = logging.getLogger(__name__)

async def competitor_node(state: dict) -> dict:
    logger.info(f"[COMPETITOR NODE] Starting. Company name: {state.get('company_name', 'unknown')}")
    try:
        company = state["company_name"]
        # Improved queries for more relevant competitor results
        queries = [
            f"{company} vs apple microsoft amazon facebook",
            f"{company} competitors search advertising cloud",
            f"{company} market share search mobile advertising",
            f"{company} alphabet inc competition analysis",
            f"{company} youtube netflix tiktok streaming",
            f"{company} workspace microsoft office google docs"
        ]
        logger.info(f"[COMPETITOR NODE] Generated queries: {queries}")
        results = await multi_search(queries, count_per_query=3)
        logger.info(f"[COMPETITOR NODE] Completed. Found {len(results)} results")
        return {"competitors": results}
    except Exception as e:
        logger.error(f"[COMPETITOR NODE] Error: {e}")
        return {"competitors": [], "error": str(e)}
