import httpx
from datetime import datetime
from app.platforms.base import BasePlatform
from app.schemas import PlatformPostingResult
from app.config import settings


class SlackPlatform(BasePlatform):
    """
    Slack Incoming Webhook API integration.
    API Docs: https://api.slack.com/messaging/webhooks
    Posts structured content into a Slack channel.
    """

    def __init__(self):
        # Slack workspaces are usually private/authenticated access
        super().__init__(name="Slack", is_public=False)
        self.webhook_url = settings.SLACK_WEBHOOK_URL

    async def post_message(self, message: str) -> PlatformPostingResult:
        if not self.webhook_url:
            if settings.DRY_RUN_MODE:
                now = datetime.now()
                simulated_url = f"https://app.slack.com/client/T00000000/C00000000/p{int(now.timestamp())}000"
                return self.create_success_result(posted_url=simulated_url, dt=now)
            return self.create_failed_result("Missing SLACK_WEBHOOK_URL in environment.")

        payload = {"text": message}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                if response.status_code == 200 and response.text.strip().lower() == "ok":
                    return self.create_success_result(posted_url=self.webhook_url)
                else:
                    return self.create_failed_result(f"Slack API HTTP {response.status_code}: {response.text}")
        except Exception as exc:
            return self.create_failed_result(f"Slack connection error: {str(exc)}")
