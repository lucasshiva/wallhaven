import json
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional

import click
from pydantic import BaseModel


class APISettings(BaseModel):
    api_key: Optional[str] = None
    timeout: int = 20
    retries: int = 1


class DownloadSettings(BaseModel):
    path: Optional[str] = None


class Config(BaseModel):
    """The main configuration class for wallhaven."""

    DIRECTORY: ClassVar[Path] = Path(click.get_app_dir("wallhaven"))
    PATH: ClassVar[Path] = DIRECTORY / "config.json"

    api: APISettings = APISettings()
    download: DownloadSettings = DownloadSettings()

    def setup(self) -> None:
        self.DIRECTORY.mkdir(parents=True, exist_ok=True)
        if not self.PATH.exists():
            self.write_default_config()
        else:
            # Not really sure if this is correct, but it seems to work.
            self = self.parse_file(self.PATH)

    def write_default_config(self) -> None:
        """Create the configuration file and write the default settings to it."""
        self.PATH.write_text(json.dumps(self.dict(), indent=2))

    def read_config_file(self) -> Dict[str, Any]:
        """Read the settings from the configuration file."""
        return json.loads(self.PATH.read_text())


wallhaven_config = Config()
wallhaven_config.setup()
