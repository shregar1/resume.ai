"""
Startup utilities for CalCount: loads configuration, environment variables,
and initializes core services (DB, Redis, LLM, logging).
"""
import os
from typing import Any
import redis
import sys

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger

from configurations.cache import CacheConfiguration, CacheConfigurationDTO
from configurations.db import DBConfiguration, DBConfigurationDTO

from constants.default import Default


"""In-memory storage for job results."""
job_store: dict = {}

logger.remove(0)
logger.add(
    sys.stderr,
    colorize=True,
    format=(
        "<green>{time:MMMM-D-YYYY}</green> | <black>{time:HH:mm:ss}</black> | "
        "<level>{level}</level> | <cyan>{message}</cyan> | "
        "<magenta>{name}:{function}:{line}</magenta> | "
        "<yellow>{extra}</yellow>"
    ),
)

# Load environment variables from .env file
logger.info("Loading .env file and environment variables")
load_dotenv()

logger.info("Loading Configurations")
cache_configuration: CacheConfigurationDTO = CacheConfiguration().get_config()
db_configuration: DBConfigurationDTO = DBConfiguration().get_config()
logger.info("Loaded Configurations")

# Access environment variables
logger.info("Loading environment variables")
APP_NAME: str = os.environ.get("APP_NAME")
SECRET_KEY: str = os.getenv("SECRET_KEY")
ALGORITHM: str = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        Default.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
)
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
TEMP_DIRECTORY: str = os.getenv("TEMP_DIRECTORY")
RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(
    os.getenv(
        "RATE_LIMIT_REQUESTS_PER_MINUTE",
        Default.RATE_LIMIT_REQUESTS_PER_MINUTE,
    )
)
RATE_LIMIT_REQUESTS_PER_HOUR: int = int(
    os.getenv(
        "RATE_LIMIT_REQUESTS_PER_HOUR",
        Default.RATE_LIMIT_REQUESTS_PER_HOUR,
    )
)
RATE_LIMIT_WINDOW_SECONDS: int = int(
    os.getenv(
        "RATE_LIMIT_WINDOW_SECONDS",
        Default.RATE_LIMIT_WINDOW_SECONDS,
    )
)
RATE_LIMIT_BURST_LIMIT: int = int(
    os.getenv(
        "RATE_LIMIT_BURST_LIMIT",
        Default.RATE_LIMIT_BURST_LIMIT,
    )
)
logger.info("Loaded environment variables")

logger.info("Initializing Redis database connection")
redis_session = redis.Redis(
    host=cache_configuration.host,
    port=cache_configuration.port,
    password=cache_configuration.password,
)
if not redis_session:
    logger.error("No Redis session available")
    raise RuntimeError("No Redis session available")
logger.info("Initialized Redis database connection")

logger.info("Initializing LLM (Google Gemini) if API key is present")
if GOOGLE_API_KEY:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
    )
    logger.info("Initialized Google Gemini LLM")
else:
    llm = None
    logger.info("No Google API key found; LLM not initialized")

logger.info("Initializing Embedding LLM (Google Gemini) if API key is present")
if GOOGLE_API_KEY:
    embedding_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
    )
    logger.info("Initialized Google Gemini LLM")
else:
    embedding_llm = None
    logger.info("No Google API key found; LLM not initialized")

unprotected_routes: set[Any] = {
    "/health",
    "/user/login",
    "/user/register",
    "/docs",
    "/redoc",
}
callback_routes: set[Any] = set()
