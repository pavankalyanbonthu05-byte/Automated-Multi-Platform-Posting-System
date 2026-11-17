import logging
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import posting_service
from app.config import settings

# Setup standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("automated_posting")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated Multi-Platform Posting System REST API built with FastAPI.",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """
    Format validation errors into clear, actionable responses.
    """
    errors = []
    for error in exc.errors():
        msg = error.get("msg", "Invalid input")
        # Clean up pydantic internal prefixes if present
        if msg.startswith("Value error, "):
            msg = msg.replace("Value error, ", "")
        errors.append({
            "loc": error.get("loc"),
            "message": msg,
            "type": error.get("type")
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "error_summary": errors[0]["message"] if errors else "Validation failed"
        }
    )


@app.get("/", tags=["Health"])
async def root():
    """Health check and API overview."""
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "posting_endpoint": "/posting"
    }


@app.post(
    "/posting",
    response_model=PostingResponse,
    status_code=status.HTTP_200_OK,
    summary="Publish short message across integrated platforms",
    description="Accepts a message (max 200 chars, exactly one valid CTA link) and broadcasts it across 5 third-party platforms.",
    tags=["Posting"]
)
async def publish_message(request: PostingRequest):
    """
    Executes automated publishing across 5 platforms:
    - Telegram
    - Discord
    - Slack
    - Mastodon
    - Dev.to
    """
    logger.info("Received posting request: %s", request.message)
    response = await posting_service.publish_message(request.message)
    return response
