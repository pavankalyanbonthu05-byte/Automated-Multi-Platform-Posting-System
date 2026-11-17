import httpx
from datetime import datetime
from app.platforms.base import BasePlatform
from app.schemas import PlatformPostingResult
from app.config import settings


class TelegramPlatform(BasePlatform):
    """
    Telegram Bot API integration.
    API Docs: https://core.telegram.org/bots/api#sendmessage
    Posts message directly to a public or private Telegram Channel / Supergroup.
    """

    def __init__(self):
        super().__init__(name="Telegram", is_public=True)
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    async def post_message(self, message: str) -> PlatformPostingResult:
        if not self.bot_token or not self.chat_id:
            if settings.DRY_RUN_MODE:
                # Dry run simulation mode
                now = datetime.now()
                simulated_url = f"https://t.me/example_channel/{int(now.timestamp()) % 10000}"
                return self.create_success_result(posted_url=simulated_url, dt=now)
            return self.create_failed_result("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment.")

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "disable_web_page_preview": False
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    message_id = data.get("result", {}).get("message_id")
                    clean_chat = str(self.chat_id).replace("@", "")
                    posted_url = (
                        f"https://t.me/{clean_chat}/{message_id}"
                        if clean_chat and not clean_chat.startswith("-")
                        else f"https://t.me/c/{clean_chat}/{message_id}"
                    )
                    return self.create_success_result(posted_url=posted_url)
                else:
                    return self.create_failed_result(f"Telegram API HTTP {response.status_code}: {response.text}")
        except Exception as exc:
            return self.create_failed_result(f"Telegram connection error: {str(exc)}")
