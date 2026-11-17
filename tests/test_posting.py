import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import PostingRequest
from app.services.posting_service import PostingService
from app.platforms.base import BasePlatform
from app.schemas import PlatformPostingResult


client = TestClient(app)


# -------------------------------------------------------------
# Input Validation Unit Tests
# -------------------------------------------------------------

def test_valid_message_schema():
    """Test schema acceptance with a valid message and CTA."""
    valid_text = "Check out our latest business platform and grow your online visibility. https://example.com"
    req = PostingRequest(message=valid_text)
    assert req.message == valid_text


def test_validation_missing_url():
    """Test rejection when no CTA link is included."""
    with pytest.raises(ValueError, match="Exactly one CTA link must be included"):
        PostingRequest(message="Check out our platform without any link.")


def test_validation_multiple_urls():
    """Test rejection when multiple CTA links are included."""
    with pytest.raises(ValueError, match="Found 2 links"):
        PostingRequest(message="Visit https://example.com and also check https://example2.com for details.")


def test_validation_message_exceeds_200_chars():
    """Test rejection when message exceeds 200 characters."""
    long_msg = "A" * 180 + " https://example.com"  # 180 + 1 + 19 = 200 -> let's make it 210
    long_msg = "A" * 190 + " https://example.com"
    assert len(long_msg) > 200
    with pytest.raises(ValueError, match="Message exceeds maximum allowed length of 200 characters"):
        PostingRequest(message=long_msg)


def test_validation_invalid_url_scheme():
    """Test rejection when URL scheme is invalid (e.g. ftp or malformed)."""
    with pytest.raises(ValueError, match="Invalid URL host|Exactly one CTA link"):
        PostingRequest(message="Visit our ftp site ftp://example.com now!")


# -------------------------------------------------------------
# API Endpoint Integration Tests
# -------------------------------------------------------------

def test_api_root_endpoint():
    """Test the root health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "posting_endpoint" in data


def test_api_posting_success_dry_run():
    """Test the POST /posting endpoint under default dry-run mode."""
    payload = {
        "message": "Check out our latest business platform and grow your online visibility. https://example.com"
    }
    response = client.post("/posting", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["results"]) == 5

    platform_names = [item["platform"] for item in data["results"]]
    assert "Telegram" in platform_names
    assert "Discord" in platform_names
    assert "Slack" in platform_names
    assert "Mastodon" in platform_names
    assert "Dev.to" in platform_names

    # Check result item fields
    for item in data["results"]:
        assert item["status"] in ("success", "failed")
        assert "posted_url" in item
        assert "public_access" in item
        assert "date" in item
        assert "time" in item
        assert "error" in item


def test_api_posting_validation_error_too_long():
    """Test API response for message exceeding 200 characters."""
    payload = {
        "message": "This message is intentionally crafted to exceed the 200 characters limit enforced by the API schema validation rules. " * 3 + " https://example.com"
    }
    response = client.post("/posting", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "error_summary" in data


def test_api_posting_validation_error_no_cta():
    """Test API response when CTA URL is missing."""
    payload = {
        "message": "Just a plain message with no call to action link whatsoever."
    }
    response = client.post("/posting", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "Exactly one CTA link must be included" in str(data)


def test_api_posting_validation_error_multiple_ctas():
    """Test API response when multiple CTA links are supplied."""
    payload = {
        "message": "Check out https://first.com and also visit https://second.com for more info."
    }
    response = client.post("/posting", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "Found 2 links" in str(data)


# -------------------------------------------------------------
# Resilience and Error Isolation Test
# -------------------------------------------------------------

class MockFailingPlatform(BasePlatform):
    def __init__(self):
        super().__init__(name="Mock Fail", is_public=False)

    async def post_message(self, message: str) -> PlatformPostingResult:
        return self.create_failed_result("Simulated network outage")


class MockSucceedingPlatform(BasePlatform):
    def __init__(self):
        super().__init__(name="Mock Success", is_public=True)

    async def post_message(self, message: str) -> PlatformPostingResult:
        return self.create_success_result(posted_url="https://mock.com/post/1")


@pytest.mark.asyncio
async def test_posting_service_fault_isolation():
    """Ensure that if one platform fails, the others continue successfully."""
    service = PostingService(platforms=[MockFailingPlatform(), MockSucceedingPlatform()])
    res = await service.publish_message("Hello https://example.com")

    assert res.success is True
    assert len(res.results) == 2

    fail_res = next(r for r in res.results if r.platform == "Mock Fail")
    assert fail_res.status == "failed"
    assert fail_res.error == "Simulated network outage"
    assert fail_res.posted_url is None

    succ_res = next(r for r in res.results if r.platform == "Mock Success")
    assert succ_res.status == "success"
    assert succ_res.posted_url == "https://mock.com/post/1"
    assert succ_res.error is None
