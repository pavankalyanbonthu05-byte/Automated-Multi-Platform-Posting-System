import re
from typing import List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator


# Regular expression to extract URLs (handles http:// and https://)
URL_REGEX = re.compile(
    r'(https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*))'
)


class PostingRequest(BaseModel):
    message: str = Field(
        ...,
        description="The content message to publish. Must be <= 200 characters and contain exactly one valid CTA link.",
        json_schema_extra={
            "example": "Check out our latest business platform and grow your online visibility. https://example.com"
        }
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or only whitespace.")

        # 1. Message must not exceed 200 characters
        if len(v) > 200:
            raise ValueError(f"Message exceeds maximum allowed length of 200 characters (current length: {len(v)}).")

        # 2. Exactly one CTA link must be included
        found_urls = URL_REGEX.findall(v)
        if len(found_urls) == 0:
            raise ValueError("Exactly one CTA link must be included in the message. No link was found.")
        if len(found_urls) > 1:
            raise ValueError(
                f"Exactly one CTA link must be included in the message. Found {len(found_urls)} links: {', '.join(found_urls)}"
            )

        # 3. Validate the URL structure
        target_url = found_urls[0]
        parsed = urlparse(target_url)
        if not parsed.scheme or parsed.scheme.lower() not in ("http", "https"):
            raise ValueError(f"Invalid URL scheme '{parsed.scheme}'. Only 'http' and 'https' are allowed.")
        if not parsed.netloc or "." not in parsed.netloc:
            raise ValueError(f"Invalid URL host '{parsed.netloc}'. Must contain a valid domain name.")

        return v


class PlatformPostingResult(BaseModel):
    platform: str = Field(..., description="Platform name")
    status: str = Field(..., description="Success or failed", json_schema_extra={"example": "success"})
    posted_url: Optional[str] = Field(None, description="Published content URL", json_schema_extra={"example": "https://example.com/post/123"})
    public_access: bool = Field(..., description="Whether content is publicly accessible", json_schema_extra={"example": True})
    date: Optional[str] = Field(None, description="Posting date (YYYY-MM-DD)", json_schema_extra={"example": "2026-11-15"})
    time: Optional[str] = Field(None, description="Posting time (HH:MM:SS)", json_schema_extra={"example": "10:30:00"})
    error: Optional[str] = Field(None, description="Error details if applicable")


class PostingResponse(BaseModel):
    success: bool = Field(..., description="Whether at least one platform succeeded", json_schema_extra={"example": True})
    results: List[PlatformPostingResult] = Field(..., description="Posting results across all integrated platforms")
