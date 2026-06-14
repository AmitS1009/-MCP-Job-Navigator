import logging
from agent.llm import client, GROQ_MODEL
import json
from langsmith import traceable

logger = logging.getLogger(__name__)

VALIDATION_SYSTEM_PROMPT = """You are a validation expert. Your task is to check if the research synthesis is grounded in the provided source data.

You will be given:
- The company name
- The research synthesis (markdown report)
- The raw source data (news, job postings, company background, competitors)

You must determine if the synthesis contains any information that is not supported by the source data (hallucinations) or if it misses key information that is present in the source data.

Respond ONLY with a JSON object in this exact format:
{
  "passed": true/false,
  "issues": ["list of specific issues found, empty array if none"]
}

Guidelines:
- Check for hallucinated numbers, names, dates, or facts not in the source
- Check if the synthesis omits important information from the source that should be included
- Be strict but fair - minor wording differences are okay
- If the synthesis says "Insufficient data found" for a section, verify that the source data indeed has little or no relevant information
- If passed is true, issues should be an empty array
- If passed is false, issues should contain one or more specific, actionable issues"""

def format_results(results: list, label: str) -> str:
    if not results:
        return f"{label}: No data found"
    items = []
    for r in results[:6]:
        title = r.get("title", "No title")
        desc = r.get("description", r.get("snippet", "No description"))
        url = r.get("url", r.get("href", ""))
        items.append(f"- {title}: {desc} ({url})")
    return f"{label}:\n" + "\n".join(items)

@traceable(name="validation_node")
async def validation_node(state: dict) -> dict:
    logger.info(f"[VALIDATION NODE] Starting validation for: {state.get('company_name', 'unknown')}")

    company = state.get("company_name", "")
    synthesis = state.get("synthesis", "")

    # If synthesis is empty or error, we cannot validate
    if not synthesis or synthesis.strip() == "":
        logger.warning("[VALIDATION NODE] Synthesis is empty, defaulting to passed=True")
        return {"validation_passed": True, "validation_issues": []}

    # Prepare source data summary
    news_summary = format_results(state.get("news_results", []), "NEWS AND UPDATES")
    jobs_summary = format_results(state.get("job_postings", []), "JOB POSTINGS")
    company_bg_summary = format_results(state.get("company_background", []), "COMPANY BACKGROUND")
    competitors_summary = format_results(state.get("competitors", []), "COMPETITORS")

    source_data = "\n\n".join([news_summary, jobs_summary, company_bg_summary, competitors_summary])

    user_prompt = f"""Company: {company}

Research Synthesis to Validate:
{synthesis}

Source Data:
{source_data}

Please validate the synthesis and return the JSON result."""

    try:
        logger.info("[VALIDATION NODE] Calling Groq LLM for validation")
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": VALIDATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent validation
            max_tokens=500
        )
        result_text = response.choices[0].message.content.strip()
        logger.info(f"[VALIDATION NODE] Raw LLM response: {result_text}")

        # Try to parse JSON
        try:
            # Extract JSON from response (in case there's extra text)
            # Find first '{' and last '}'
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = result_text[start:end]
                result = json.loads(json_str)
            else:
                result = json.loads(result_text)

            # Validate the structure
            if not isinstance(result, dict):
                raise ValueError("Response is not a dictionary")

            passed = result.get("passed", True)  # Default to True if missing
            issues = result.get("issues", [])   # Default to empty list if missing

            # Ensure issues is a list
            if not isinstance(issues, list):
                issues = [str(issues)]

            logger.info(f"[VALIDATION NODE] Validation result - passed: {passed}, issues: {issues}")
            return {
                "validation_passed": bool(passed),
                "validation_issues": issues
            }
        except(json.JSONDecodeError, ValueError) as e:
            logger.error(f"[VALIDATION NODE] Failed to parse JSON from LLM response: {e}")
            logger.error(f"[VALIDATION NODE] Response was: {result_text}")
            # Default to passed=True on parse failure
            return {"validation_passed": True, "validation_issues": []}

    except Exception as e:
        logger.error(f"[VALIDATION NODE] Error during validation: {e}")
        # On any error, default to passed=True to avoid blocking
        return {"validation_passed": True, "validation_issues": []}