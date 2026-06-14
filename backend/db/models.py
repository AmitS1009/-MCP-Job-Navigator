from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, index=True)
    query = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    synthesis = Column(Text, nullable=True)
    validation_passed = Column(Boolean, default=False, nullable=False)
    validation_issues = Column(JSON, nullable=False, default=list)
    retry_count = Column(Integer, default=0, nullable=False)
    news_results = Column(JSON, nullable=False, default=list)
    job_postings = Column(JSON, nullable=False, default=list)
    company_background = Column(JSON, nullable=False, default=list)
    competitors = Column(JSON, nullable=False, default=list)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)