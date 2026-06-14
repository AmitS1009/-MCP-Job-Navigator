import logging
from agent.llm import client, GROQ_MODEL
import json
from langsmith import traceable

logger = logging.getLogger(__name__)

REWRITE_SYSTEM_PROMPT = """You are a search query optimization expert. Your task is to produce an improved company name or search query that will yield better search results for job research.

You will be given:
- The original user query
- The current company name being used for search
- The validation issues (specific problems found in the synthesis)
- Optionally, the current synthesis (if available)

You must return a JSON object with an optimized company name or query that is likely to produce more relevant and accurate search results.

Respond ONLY with a JSON object in this exact format:
{
  "company_name": "optimized company name or query to use for search"
}

Guidelines:
- If the validation issues indicate the company name was ambiguous or incorrect, correct it
- If the issues suggest missing information, consider alternative names or subsidiaries
- Keep the company name concise and focused on the core entity
- Do not add extra instructions or commentary - only the JSON"""

@traceable(name="rewrite_node")
async def rewrite_node(state: dict) -> dict:
    logger.info(f"[REWRITE NODE] Starting rewrite for: {state.get('company_name', 'unknown')}")

    original_query = state.get("query", "")
    current_company = state.get("company_name", "")
    validation_issues = state.get("validation_issues", [])
    synthesis = state.get("synthesis", "")

    # Prepare context for the LLM
    issues_text = "\n".join(f"- {issue}" for issue in validation_issues) if validation_issues else "No specific issues provided"

    user_prompt = f"""Original user query: {original_query}
Current company name used for search: {current_company}
Validation issues found:
{issues_text}

Current synthesis (for reference):
{synthesis[:1000]}  # Limit length

Please provide an optimized company name or search query to improve search results."""

    try:
        logger.info("[REWRITE NODE] Calling Groq LLM for query rewrite")
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        result_text = response.choices[0].message.content.strip()
        logger.info(f"[REWRITE NODE] Raw LLM response: {result_text}")

        # Try to parse JSON
        try:
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = result_text[start:end]
                result = json.loads(json_str)
            else:
                result = json.loads(result_text)

            new_company_name = result.get("company_name", current_company)
            # Ensure it's a string
            if not isinstance(new_company_name, str):
                new_company_name = str(new_company_name)

            logger.info(f"[REWRITE NODE] Rewrote company name from '{current_company}' to '{new_company_name}'")
            return {
                "company_name": new_company_name,
                "retry_count": state.get("retry_count", 0) + 1,
                "synthesis": "",  # Clear old synthesis
                # Clear validation fields so they are recomputed
                "validation_passed": False,
                "validation_issues": []
            }
        except(json.JSONDecodeError, ValueError) as e:
            logger.error(f"[REWRITE NODE] Failed to parse JSON from LLM response: {e}")
            logger.error(f"[REWRITE NODE] Response was: {result_text}")
            # On parse failure, increment retry count and return unchanged company name (will cause loop to end after max retries)
            return {
                "retry_count": state.get("retry_count", 0) + 1,
                "synthesis": "",
                "validation_passed": False,
                "validation_issues": []
            }

    except Exception as e:
        logger.error(f"[REWRITE NODE] Error during rewrite: {e}")
        # On error, increment retry count and clear synthesis
        return {
            "retry_count": state.get("retry_count", 0) + 1,
            "synthesis": "",
            "validation_passed": False,
            "validation_issues": []
        }