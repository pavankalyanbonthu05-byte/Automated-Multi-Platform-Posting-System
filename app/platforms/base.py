from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional
from app.schemas import PlatformPostingResult


class BasePlatform(ABC):
    """
    Abstract Base Class for all social/content posting platforms.
    Every platform integration must inherit from this class and implement
    the post_message method.
    """

    def __init__(self, name: str, is_public: bool = True):
        self.name = name
        self.is_public = is_public

    @abstractmethod
    async def post_message(self, message: str) -> PlatformPostingResult:
        """
        Asynchronously publishes the given message to the target platform.
        Must handle errors gracefully and never throw unhandled exceptions.
        """
        pass

    def create_success_result(
        self,
        posted_url: Optional[str] = None,
        public_access: Optional[bool] = None,
        dt: Optional[datetime] = None
    ) -> PlatformPostingResult:
        """Helper to create a standard successful response."""
        now = dt or datetime.now()
        return PlatformPostingResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=self.is_public if public_access is None else public_access,
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            error=None
        )

    def create_failed_result(
        self,
        error_msg: str,
        public_access: Optional[bool] = None
    ) -> PlatformPostingResult:
        """Helper to create a standard failed response."""
        return PlatformPostingResult(
            platform=self.name,
            status="failed",
            posted_url=None,
            public_access=False if public_access is None else public_access,
            date=None,
            time=None,
            error=error_msg
        )
