from agent.tools.duckduckgo_search import multi_search
import logging

logger = logging.getLogger(__name__)

async def news_node(state: dict) -> dict:
    logger.info(f"[NEWS NODE] Starting. Company name: {state.get('company_name', 'unknown')}")
    try:
        company = state["company_name"]
        # Improved queries for more consistent, relevant news results
        queries = [
            f"{company} I/O 2026",
            f"{company} AI announcement 2026",
            f"{company} product launch 2026",
            f"{company} blog post june 2026",
            f"{company} press release may 2026",
            f"{company} latest developments"
        ]
        logger.info(f"[NEWS NODE] Generated queries: {queries}")
        results = await multi_search(queries, count_per_query=4)
        logger.info(f"[NEWS NODE] Completed. Found {len(results)} results")
        return {"news_results": results}
    except Exception as e:
        logger.error(f"[NEWS NODE] Error: {e}")
        return {"news_results": [], "error": str(e)}
