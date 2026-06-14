import os
from dotenv import load_dotenv
load_dotenv()  # load .env file

# Set LangSmith environment variables
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
langchain_project = os.getenv("LANGCHAIN_PROJECT", "mcp-job-research-agent")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = langchain_api_key or ""
os.environ["LANGCHAIN_PROJECT"] = langchain_project or "mcp-job-research-agent"

import asyncio
import uuid
import logging
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.tools.duckduckgo_search import duckduckgo_search
from agent.graph import build_graph
from config import GROQ_API_KEY, LANGSMITH_API_KEY, DATABASE_URL
from db.database import init_db, AsyncSessionLocal
from db.models import ResearchSession
from sqlalchemy import select, desc
scores_path = Path(__file__).parent / "app/evaluation/scores.json"

# Configure logging to write to both stream and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# Log that LangSmith tracing is initialised with project name
logger.info(f"[APP] LangSmith tracing initialised - project: {os.environ['LANGCHAIN_PROJECT']}")

app = FastAPI(title="Job Research Agent", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ResearchRequest(BaseModel):
    query: str

# Build the graph once at startup
graph = build_graph()

# Startup event to initialize the database
@app.on_event("startup")
async def startup_event():
    logger.info("[APP] Starting up")
    await init_db()
    logger.info("[APP] Database ready")
    logger.info("[APP] Server ready at port 8000")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Job Research Agent"}

# Test search endpoint
@app.get("/search/test")
async def test_search(q: str):
    """Run a single duckduckgo search and return raw results."""
    try:
        results = await duckduckgo_search(q, count=5)
        return {"query": q, "results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error in test search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Main research endpoint
@app.post("/research")
async def research(request: ResearchRequest):
    """
    Perform company/job research using LangGraph with parallel nodes.
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Generate a session ID
    session_id = str(uuid.uuid4())
    logger.info(f"Starting research for query: {query} (session: {session_id})")

    # Initial state for the graph
    initial_state = {
        "query": query,
        "company_name": query,
        "news_results": [],
        "job_postings": [],
        "company_background": [],
        "competitors": [],
        "synthesis": "",
        "validation_passed": False,
        "validation_issues": [],
        "retry_count": 0,
        "session_id": session_id,
        "error": None
    }

    try:
        # Invoke the graph asynchronously
        start_time = asyncio.get_event_loop().time()
        result = await graph.ainvoke(initial_state)
        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time

        # Check if any node reported an error
        if result.get("error"):
            logger.error(f"Graph error: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])

        # Calculate total results
        total_results = (
            len(result["news_results"]) +
            len(result["job_postings"]) +
            len(result["company_background"]) +
            len(result["competitors"])
        )

        logger.info(f"Research completed in {elapsed:.2f}s. Total results: {total_results}")

        # Prepare response
        response = {
            "session_id": session_id,
            "company": request.query,
            "elapsed_seconds": elapsed,
            "synthesis": result.get("synthesis", ""),
            "news": result["news_results"],
            "jobs": result["job_postings"],
            "company_background": result["company_background"],
            "competitors": result["competitors"],
            "total_results": total_results,
            "error": result.get("error"),
            "validation_passed": result.get("validation_passed", False),
            "validation_issues": result.get("validation_issues", []),
            "retry_count": result.get("retry_count", 0)
        }

        # Save session to PostgreSQL
        try:
            async with AsyncSessionLocal() as session:
                db_session = ResearchSession(
                    id=session_id,
                    query=query,
                    company_name=result.get("company_name", query),
                    synthesis=result.get("synthesis"),
                    validation_passed=result.get("validation_passed", False),
                    validation_issues=result.get("validation_issues", []),
                    retry_count=result.get("retry_count", 0),
                    news_results=result.get("news_results", []),
                    job_postings=result.get("job_postings", []),
                    company_background=result.get("company_background", []),
                    competitors=result.get("competitors", []),
                    error=result.get("error")
                )
                session.add(db_session)
                await session.commit()
                logger.info(f"[DB] Session saved: {session_id}")
        except Exception as e:
            logger.error(f"[DB] Failed to save session {session_id}: {e}")
            # Do not fail the request

        return response

    except Exception as e:
        logger.error(f"Error during research: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# History endpoint
@app.get("/history")
async def get_history():
    """
    Fetch the last 20 research sessions.
    """
    try:
        async with AsyncSessionLocal() as session:
            # Query the last 20 sessions ordered by created_at descending
            from sqlalchemy import desc
            result = await session.execute(
                select(ResearchSession)
                .order_by(desc(ResearchSession.created_at))
                .limit(20)
            )
            sessions = result.scalars().all()

            # Convert to list of dictionaries with the required fields
            history = []
            for sess in sessions:
                history.append({
                    "session_id": sess.id,
                    "query": sess.query,
                    "synthesis": sess.synthesis,
                    "validation_passed": sess.validation_passed,
                    "retry_count": sess.retry_count,
                    "created_at": sess.created_at.isoformat() if sess.created_at else None
                })

            return {"history": history}
    except Exception as e:
        logger.error(f"[DB] Failed to fetch history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/traces")
async def get_traces():
    """Endpoint to verify LangSmith tracing configuration."""
    return {
        "status": "active",
        "project": os.environ["LANGCHAIN_PROJECT"],
        "dashboard": "https://smith.langchain.com"
    }


@app.get("/metrics")
async def get_metrics():
    logger.info("[METRICS] Fetching evaluation scores")
    try:
        if scores_path.exists():
            with open(scores_path) as f:
                scores = json.load(f)
            logger.info("[METRICS] Scores found and returned")
            return scores
        else:
            logger.info("[METRICS] scores.json not found")
            return {
                "status": "not_run", "message": "Run evaluation with: docker compose exec backend python -m app.evaluation.run_evaluation"
            }
    except Exception as e:
        logger.error(f"[METRICS] Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)