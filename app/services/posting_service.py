import asyncio
import logging
from typing import List
from app.schemas import PostingResponse, PlatformPostingResult
from app.platforms import (
    BasePlatform,
    TelegramPlatform,
    DiscordPlatform,
    SlackPlatform,
    MastodonPlatform,
    DevtoPlatform,
)

logger = logging.getLogger(__name__)


class PostingService:
    """
    Coordinates simultaneous publishing across multiple platforms.
    Ensures failure isolation: if one platform encounters an error,
    remaining platforms continue uninterrupted.
    """

    def __init__(self, platforms: List[BasePlatform] = None):
        self.platforms = platforms or [
            TelegramPlatform(),
            DiscordPlatform(),
            SlackPlatform(),
            MastodonPlatform(),
            DevtoPlatform(),
        ]

    async def publish_message(self, message: str) -> PostingResponse:
        """
        Publishes the validated message across all configured platforms concurrently.
        """
        logger.info("Initiating multi-platform publication across %d platforms", len(self.platforms))

        async def _safe_post(platform: BasePlatform) -> PlatformPostingResult:
            try:
                return await platform.post_message(message)
            except Exception as e:
                logger.error("Unexpected error in platform %s: %s", platform.name, str(e), exc_info=True)
                return platform.create_failed_result(f"Unexpected execution error: {str(e)}")

        # Execute all platform postings concurrently using asyncio.gather
        tasks = [_safe_post(p) for p in self.platforms]
        results: List[PlatformPostingResult] = await asyncio.gather(*tasks)

        # Determine overall success: true if at least one platform succeeded
        overall_success = any(r.status == "success" for r in results)

        return PostingResponse(
            success=overall_success,
            results=results
        )


posting_service = PostingService()
