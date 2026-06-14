from agent.tools.duckduckgo_search import multi_search
import logging

logger = logging.getLogger(__name__)

async def jobs_node(state: dict) -> dict:
    logger.info(f"[JOBS NODE] Starting. Company name: {state.get('company_name', 'unknown')}")
    try:
        company = state["company_name"]
        # Improved queries for more relevant job results
        queries = [
            f"{company} software engineer intern",
            f"{company} data scientist internship",
            f"{company} product manager intern",
            f"{company} ux designer internship",
            f"{company} new graduate program 2026",
            f"{company} summer intern 2026"
        ]
        logger.info(f"[JOBS NODE] Generated queries: {queries}")
        results = await multi_search(queries, count_per_query=3)
        logger.info(f"[JOBS NODE] Completed. Found {len(results)} results")
        return {"job_postings": results}
    except Exception as e:
        logger.error(f"[JOBS NODE] Error: {e}")
        return {"job_postings": [], "error": str(e)}
