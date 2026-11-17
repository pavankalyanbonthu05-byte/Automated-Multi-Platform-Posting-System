import httpx
from datetime import datetime
from app.platforms.base import BasePlatform
from app.schemas import PlatformPostingResult
from app.config import settings


class MastodonPlatform(BasePlatform):
    """
    Mastodon REST API integration (Fediverse / Decentralized Social Network).
    API Docs: https://docs.joinmastodon.org/methods/statuses/#create
    Publishes a public status (toot).
    """

    def __init__(self):
        super().__init__(name="Mastodon", is_public=True)
        self.instance_url = settings.MASTODON_INSTANCE_URL.rstrip("/")
        self.access_token = settings.MASTODON_ACCESS_TOKEN

    async def post_message(self, message: str) -> PlatformPostingResult:
        if not self.access_token:
            if settings.DRY_RUN_MODE:
                now = datetime.now()
                simulated_url = f"{self.instance_url}/@bot/{int(now.timestamp())}"
                return self.create_success_result(posted_url=simulated_url, dt=now)
            return self.create_failed_result("Missing MASTODON_ACCESS_TOKEN in environment.")

        url = f"{self.instance_url}/api/v1/statuses"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "status": message,
            "visibility": "public"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code in (200, 201):
                    data = response.json()
                    posted_url = data.get("url") or f"{self.instance_url}/statuses/{data.get('id')}"
                    return self.create_success_result(posted_url=posted_url)
                else:
                    return self.create_failed_result(f"Mastodon API HTTP {response.status_code}: {response.text}")
        except Exception as exc:
            return self.create_failed_result(f"Mastodon connection error: {str(exc)}")
