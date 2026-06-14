import asyncio
import logging
from typing import List, Dict
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

async def duckduckgo_search(query: str, count: int = 5) -> List[Dict]:
    """
    Perform a single DuckDuckGo search.

    Args:
        query: The search query string
        count: Number of results to return (max 50, but we'll limit to 10 for safety)

    Returns:
        List of dictionaries with keys: title, url, description
    """
    logger.info(f"[DUCKDUCKGO SEARCH] Starting. Query: '{query}', count: {count}")
    if count > 10:
        count = 10
        logger.info(f"[DUCKDUCKGO SEARCH] Adjusted count to {count} (max 10)")

    def _search():
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=count):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "description": r.get("body", "")
                })
            return results

    try:
        # Run the synchronous search in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _search)
        logger.info(f"[DUCKDUCKGO SEARCH] Completed. Found {len(results)} results for query: '{query}'")
        return results
    except Exception as e:
        logger.error(f"[DUCKDUCKGO SEARCH] Error performing DuckDuckGo search for query '{query}': {e}")
        return []

async def multi_search(queries: List[str], count_per_query: int = 3) -> List[Dict]:
    """
    Run multiple search queries concurrently and deduplicate by URL.

    Args:
        queries: List of search query strings
        count_per_query: Number of results per query

    Returns:
        Deduplicated list of search results
    """
    logger.info(f"[MULTI SEARCH] Starting. Number of queries: {len(queries)}, count_per_query: {count_per_query}")
    logger.info(f"[MULTI SEARCH] Queries: {queries}")
    # Run all queries concurrently
    tasks = [duckduckgo_search(query, count_per_query) for query in queries]
    results_lists = await asyncio.gather(*tasks)

    # Flatten and deduplicate by URL
    seen_urls = set()
    deduplicated_results = []

    for results in results_lists:
        for result in results:
            url = result.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduplicated_results.append(result)

    logger.info(f"[MULTI SEARCH] Completed. Returning {len(deduplicated_results)} deduplicated results")
    return deduplicated_results