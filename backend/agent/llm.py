import logging
from groq import AsyncGroq
from config import GROQ_API_KEY, GROQ_MODEL
from langsmith import traceable

logger = logging.getLogger(__name__)
client = AsyncGroq(api_key=GROQ_API_KEY)

SYNTHESIS_SYSTEM_PROMPT = """You are a professional job research analyst.

Given raw web search results about a company, produce a structured
markdown report with EXACTLY these sections in this order:

## Company Overview

## Recent News and Developments

## Current Job Openings

## Culture and Work Environment

## Competitor Landscape

## Key Insights for Job Applicants

Rules:

- Only use information present in the provided search results

- If data is missing for a section, write exactly: "Insufficient data found"

- Never hallucinate funding numbers, team sizes, or job titles

- Max 100 words per section

- Be direct and useful for someone preparing a job application

- Do not add any sections beyond the 6 listed above"""

def format_results(results: list, label: str) -> str:
    logger.info(f"[FORMAT_RESULTS] Starting. Label: {label}, results count: {len(results)}")
    try:
        if not results:
            logger.info("[FORMAT_RESULTS] No results found")
            return f"{label}: No data found"
        items = []
        for r in results[:6]:
            title = r.get("title", "No title")
            desc = r.get("description", r.get("snippet", "No description"))
            url = r.get("url", r.get("href", ""))
            items.append(f"- {title}: {desc} ({url})")
        result_str = f"{label}:\n" + "\n".join(items)
        logger.info(f"[FORMAT_RESULTS] Completed. Returning string of length: {len(result_str)}")
        return result_str
    except Exception as e:
        logger.error(f"[FORMAT_RESULTS] Error: {e}")
        # Return a safe fallback
        return f"{label}: Error formatting results"

@traceable(name="synthesise_research")
async def synthesise_research(
    company: str,
    news: list,
    jobs: list,
    company_bg: list,
    competitors: list
) -> str:
    logger.info(f"[LLM] Starting synthesis for: {company}")
    logger.info(f"[LLM] Input sizes - news:{len(news)} jobs:{len(jobs)} "
                f"company:{len(company_bg)} competitors:{len(competitors)}")

    context = "\n\n".join([
        format_results(news, "NEWS AND UPDATES"),
        format_results(jobs, "JOB POSTINGS"),
        format_results(company_bg, "COMPANY BACKGROUND"),
        format_results(competitors, "COMPETITORS")
    ])

    user_prompt = f"""Research target company: {company}

Raw search data collected:

{context}

Write the structured research report now."""

    try:
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        result = response.choices[0].message.content
        logger.info(f"[LLM] Synthesis complete. Output length: {len(result)} chars")
        return result
    except Exception as e:
        logger.error(f"[LLM] Synthesis failed: {e}")
        return f"Synthesis failed due to error: {str(e)}"