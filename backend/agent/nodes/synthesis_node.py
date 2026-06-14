import logging
from agent.state import ResearchState
from agent.llm import synthesise_research

logger = logging.getLogger(__name__)

async def synthesis_node(state: ResearchState) -> dict:
    logger.info(f"[SYNTHESIS NODE] Starting for company: {state['company_name']}")
    logger.info(f"[SYNTHESIS NODE] Inputs - news: {len(state.get('news_results', []))}, "
                f"jobs: {len(state.get('job_postings', []))}, "
                f"company_bg: {len(state.get('company_background', []))}, "
                f"competitors: {len(state.get('competitors', []))}")

    try:
        synthesis = await synthesise_research(
            company=state["company_name"],
            news=state["news_results"],
            jobs=state["job_postings"],
            company_bg=state["company_background"],
            competitors=state["competitors"]
        )
        logger.info("[SYNTHESIS NODE] Synthesis generated successfully")
        logger.info(f"[SYNTHESIS NODE] Synthesis length: {len(synthesis)} characters")
        return {"synthesis": synthesis}
    except Exception as e:
        logger.error(f"[SYNTHESIS NODE] Error: {e}")
        return {
            "synthesis": f"Research completed but synthesis failed: {str(e)}",
            "error": str(e)
        }