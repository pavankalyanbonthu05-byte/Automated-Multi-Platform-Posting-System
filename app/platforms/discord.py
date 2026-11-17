import httpx
from datetime import datetime
from app.platforms.base import BasePlatform
from app.schemas import PlatformPostingResult
from app.config import settings


class DiscordPlatform(BasePlatform):
    """
    Discord Webhook API integration.
    API Docs: https://discord.com/developers/docs/resources/webhook#execute-webhook
    Executes an incoming webhook with ?wait=true to retrieve message details.
    """

    def __init__(self):
        # Discord channel messages can be publicly readable if channel is community/public
        super().__init__(name="Discord", is_public=True)
        self.webhook_url = settings.DISCORD_WEBHOOK_URL

    async def post_message(self, message: str) -> PlatformPostingResult:
        if not self.webhook_url:
            if settings.DRY_RUN_MODE:
                now = datetime.now()
                simulated_url = f"https://discord.com/channels/123456789/987654321/{int(now.timestamp())}"
                return self.create_success_result(posted_url=simulated_url, dt=now)
            return self.create_failed_result("Missing DISCORD_WEBHOOK_URL in environment.")

        # Appending wait=true instructs Discord to return the full message payload with channel_id and message id
        target_url = self.webhook_url
        if "?" in target_url:
            target_url += "&wait=true"
        else:
            target_url += "?wait=true"

        payload = {"content": message}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(target_url, json=payload)
                if response.status_code in (200, 204):
                    if response.status_code == 200:
                        data = response.json()
                        channel_id = data.get("channel_id")
                        message_id = data.get("id")
                        posted_url = f"https://discord.com/channels/@me/{channel_id}/{message_id}"
                    else:
                        posted_url = self.webhook_url
                    return self.create_success_result(posted_url=posted_url)
                else:
                    return self.create_failed_result(f"Discord API HTTP {response.status_code}: {response.text}")
        except Exception as exc:
            return self.create_failed_result(f"Discord connection error: {str(exc)}")
