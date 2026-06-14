import sys
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

logger.info("Testing imports one by one")

try:
    import groq
    logger.info("groq import OK")
except Exception as e:
    logger.error(f"groq import FAILED: {e}")
    sys.exit(1)

try:
    from langchain_groq import ChatGroq
    logger.info("ChatGroq import OK")
except Exception as e:
    logger.error(f"ChatGroq import FAILED: {e}")
    sys.exit(1)

try:
    from ragas.llms import LangchainLLMWrapper
    logger.info("LangchainLLMWrapper import OK")
except Exception as e:
    logger.error(f"LangchainLLMWrapper import FAILED: {e}")
    sys.exit(1)

try:
    from ragas.metrics import faithfulness, answer_relevancy
    from ragas.metrics import context_precision, context_recall
    logger.info("ragas metrics import OK")
except Exception as e:
    logger.error(f"ragas metrics import FAILED: {e}")
    sys.exit(1)

try:
    from datasets import Dataset
    logger.info("datasets import OK")
except Exception as e:
    logger.error(f"datasets import FAILED: {e}")
    sys.exit(1)

try:
    import os
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        logger.error("GROQ_API_KEY is empty - check .env file")
        sys.exit(1)
    logger.info(f"GROQ_API_KEY found, length: {len(key)}")
except Exception as e:
    logger.error(f"env check FAILED: {e}")
    sys.exit(1)

try:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=key)
    wrapped = LangchainLLMWrapper(llm)
    logger.info("LLM wrapper creation OK")
except Exception as e:
    logger.error(f"LLM wrapper creation FAILED: {e}")
    sys.exit(1)

logger.info("ALL IMPORTS OK - safe to run evaluation")