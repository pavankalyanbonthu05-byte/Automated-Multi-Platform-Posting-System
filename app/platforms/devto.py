import httpx
from datetime import datetime
from app.platforms.base import BasePlatform
from app.schemas import PlatformPostingResult
from app.config import settings


class DevtoPlatform(BasePlatform):
    """
    Dev.to (Forem API) integration.
    API Docs: https://developers.forem.com/api/v1#tag/articles/operation/createArticle
    Publishes a developer micro-post / article to Dev.to.
    """

    def __init__(self):
        super().__init__(name="Dev.to", is_public=True)
        self.api_key = settings.DEVTO_API_KEY

    async def post_message(self, message: str) -> PlatformPostingResult:
        if not self.api_key:
            if settings.DRY_RUN_MODE:
                now = datetime.now()
                simulated_url = f"https://dev.to/user/post-{int(now.timestamp())}"
                return self.create_success_result(posted_url=simulated_url, dt=now)
            return self.create_failed_result("Missing DEVTO_API_KEY in environment.")

        url = "https://dev.to/api/articles"
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        # Create a brief publication title from the first sentence or first 50 chars
        title_snippet = message.split(".")[0][:50].strip() or "Automated Business Update"
        payload = {
            "article": {
                "title": title_snippet,
                "published": True,
                "body_markdown": message,
                "tags": ["tech", "business", "updates"]
            }
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code in (200, 201):
                    data = response.json()
                    posted_url = data.get("url")
                    return self.create_success_result(posted_url=posted_url)
                else:
                    return self.create_failed_result(f"Dev.to API HTTP {response.status_code}: {response.text}")
        except Exception as exc:
            return self.create_failed_result(f"Dev.to connection error: {str(exc)}")
