from agent.tools.duckduckgo_search import multi_search
import logging

logger = logging.getLogger(__name__)

async def company_node(state: dict) -> dict:
    logger.info(f"[COMPANY NODE] Starting. Company name: {state.get('company_name', 'unknown')}")
    try:
        company = state["company_name"]
        # Improved queries for more relevant company background results
        queries = [
            f"{company} about google company information",
            f"{company} history founded 1998 larry page sergey brin",
            f"{company} ceo sundar pichai biography",
            f"{company} executive team leadership",
            f"{company} revenue profit financial report",
            f"{company} employee count statistics workforce",
            f"{company} alphabet inc investor relations",
            f"{company} headquarters mountain view california"
        ]
        logger.info(f"[COMPANY NODE] Generated queries: {queries}")
        results = await multi_search(queries, count_per_query=3)
        logger.info(f"[COMPANY NODE] Completed. Found {len(results)} results")
        return {"company_background": results}
    except Exception as e:
        logger.error(f"[COMPANY NODE] Error: {e}")
        return {"company_background": [], "error": str(e)}
