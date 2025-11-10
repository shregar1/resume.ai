"""
Main FastAPI application entry point. Sets up middleware, routers,
and configuration for the RESUME.AI API.
"""
import os
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from http import HTTPStatus
from loguru import logger

from constants.default import Default
from controllers.apis import router as APISRouter

app = FastAPI()

load_dotenv()
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Handle validation errors and return a structured JSON response.
    """
    logger.error(f"Request validation error for urn={request.state.urn}: {exc.errors()}", exc_info=True)
    for error in exc.errors():
        if "ctx" in error:
            error.pop("ctx")
    response_payload: dict = {
        "transactionUrn": request.state.urn,
        "responseMessage": "Bad or missing input.",
        "responseKey": "error_bad_input",
        "errors": exc.errors(),
    }
    logger.debug(f"Returning validation error response for urn={request.state.urn}")
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=response_payload,
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    logger.info("Health check endpoint called")
    return {"status": "ok"}

logger.info("Initialising middleware stack")
app.add_middleware(middleware_class=TrustedHostMiddleware, allowed_hosts=["*"])
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
logger.info("Initialised middleware stack")

logger.info("Initialising routers")
# APIS ROUTER
app.include_router(APISRouter)
logger.info("Initialised routers")


@app.on_event("startup")
async def on_startup():
    """
    Application startup event handler.
    """
    logger.info("=== FastAPI Application Startup ===")
    logger.info(f"Application Name: {os.getenv('APP_NAME', 'resume.ai')}")
    logger.info(f"Host: {HOST}, Port: {PORT}")
    logger.info("Application startup event triggered")


@app.on_event("shutdown")
async def on_shutdown():
    """
    Application shutdown event handler.
    """
    logger.info("Application shutdown event triggered")
    logger.info("=== FastAPI Application Shutdown ===")

if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)
