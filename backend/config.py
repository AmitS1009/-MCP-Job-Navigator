import os
import logging
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "mcp-job-research-agent")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# For backward compatibility, expose LANGSMITH_API_KEY
LANGSMITH_API_KEY = LANGCHAIN_API_KEY

# Check for missing Groq API key (required)
if not GROQ_API_KEY:
    raise ValueError("Missing environment variable: GROQ_API_KEY. Please check your .env file.")

# Log warning if LangSmith API key is not set
if not LANGCHAIN_API_KEY:
    logger = logging.getLogger(__name__)
    logger.warning("LANGCHAIN_API_KEY not set in environment. LangSmith tracing will be disabled.")

# Log warning if DATABASE_URL is using the default (i.e., not set in environment)
if not os.getenv("DATABASE_URL"):
    logger = logging.getLogger(__name__)
    logger.warning("DATABASE_URL not set in environment, using default: %s", DATABASE_URL)

# Export the variables
__all__ = ["GROQ_API_KEY", "GROQ_MODEL", "LANGSMITH_API_KEY", "LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT", "DATABASE_URL"]