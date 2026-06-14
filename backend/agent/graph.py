from langgraph.graph import StateGraph, END
from agent.state import ResearchState
from agent.nodes.news_node import news_node
from agent.nodes.jobs_node import jobs_node
from agent.nodes.company_node import company_node
from agent.nodes.competitor_node import competitor_node
from agent.nodes.synthesis_node import synthesis_node
from agent.nodes.validation_node import validation_node
from agent.nodes.rewrite_node import rewrite_node
import logging

logger = logging.getLogger(__name__)

def build_graph():
    logger.info("[GRAPH] Building graph")
    graph = StateGraph(ResearchState)

    # Add all nodes
    graph.add_node("news_agent", news_node)
    graph.add_node("jobs_agent", jobs_node)
    graph.add_node("company_agent", company_node)
    graph.add_node("competitors_agent", competitor_node)
    graph.add_node("synthesis_agent", synthesis_node)
    graph.add_node("validation", validation_node)
    graph.add_node("rewrite", rewrite_node)

    # Start node that logs the start
    graph.add_node("start", lambda state: (
        logger.info(f"[GRAPH] Research started: {state['company_name']}") or state
    ))

    graph.set_entry_point("start")

    # All 4 nodes run in parallel from start
    graph.add_edge("start", "news_agent")
    graph.add_edge("start", "jobs_agent")
    graph.add_edge("start", "company_agent")
    graph.add_edge("start", "competitors_agent")

    # All 4 feed into synthesis
    graph.add_edge("news_agent", "synthesis_agent")
    graph.add_edge("jobs_agent", "synthesis_agent")
    graph.add_edge("company_agent", "synthesis_agent")
    graph.add_edge("competitors_agent", "synthesis_agent")

    # Synthesis feeds into validation
    graph.add_edge("synthesis_agent", "validation")

    # Conditional routing after validation
    def route_after_validation(state: ResearchState) -> str:
        logger.info(f"[ROUTER] Checking validation: passed={state.get('validation_passed')}, retry_count={state.get('retry_count', 0)}")
        validation_passed = state.get("validation_passed", False)
        retry_count = state.get("retry_count", 0)

        if validation_passed:
            logger.info("[ROUTER] Validation passed, ending pipeline")
            return "end"
        elif retry_count >= 2:
            logger.warning(f"[ROUTER] Validation failed and retry_count ({retry_count}) >= 2, ending pipeline with warning")
            return "end"
        else:
            logger.info("[ROUTER] Validation failed, retrying...")
            return "rewrite"

    graph.add_conditional_edges(
        "validation",
        route_after_validation,
        {
            "end": END,
            "rewrite": "rewrite"
        }
    )

    # Rewrite node feeds back into synthesis (loop)
    graph.add_edge("rewrite", "synthesis_agent")

    compiled = graph.compile()
    logger.info("[GRAPH] Graph compiled successfully")
    return compiled