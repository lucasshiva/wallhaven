from typing import Optional, Dict, Any
from pathlib import Path

from pydantic import BaseSettings, Field

from wallhaven.models import BaseModel


class APISettings(BaseSettings):
    """Settings for the API.

    Attributes:
        api_key: The API key is used for operations that require the user to be authenticated
            (such as viewing your browsing settings), and for NSFW wallpapers. If none is given,
            `Wallhaven` will try to read one from the 'WALLHAVEN_API_KEY' environment variable.
        timeout: The amount of seconds to wait for the server's response before giving up.
        retries: The amount of retries to perform when requesting the API.
    """

    api_key: Optional[str] = Field(default=None, env="WALLHAVEN_API_KEY")
    timeout: int = 20
    retries: int = 1


class DownloadSettings(BaseModel):
    path: Path = Path()  # The current directory by default.
    override: bool = True

    def as_dict(self) -> Dict[str, Any]:
        """Returns the instance as a dictionary."""
        # The only reason we need this if to call `self.path.name`.
        return {"path": self.path.name, "override": self.override}
