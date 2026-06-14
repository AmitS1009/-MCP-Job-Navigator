from typing import TypedDict, Optional, List, Annotated
import operator

class ResearchState(TypedDict):
    query: str
    company_name: str
    news_results: Annotated[List[dict], operator.add]
    job_postings: Annotated[List[dict], operator.add]
    company_background: Annotated[List[dict], operator.add]
    competitors: Annotated[List[dict], operator.add]
    synthesis: str
    validation_passed: bool
    validation_issues: List[str]
    retry_count: int
    session_id: str
    error: Optional[str]