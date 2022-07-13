import json
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional

import click
from pydantic import BaseModel, BaseSettings, Field

from wallhaven.search import SearchParameters


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
    path: Optional[str] = None


class Config(BaseModel):
    """The main configuration class for wallhaven."""

    DIRECTORY: ClassVar[Path] = Path(click.get_app_dir("wallhaven"))
    PATH: ClassVar[Path] = DIRECTORY / "config.json"

    api: APISettings = APISettings()
    download: DownloadSettings = DownloadSettings()
    search: SearchParameters = SearchParameters()

    @classmethod
    def setup(cls) -> "Config":
        """Creates an instance of ``Config``.

        This will read the config file and load its contents. If the former doesn't exist, the
        instance will be created with the default values.
        """
        instance = cls()

        cls.DIRECTORY.mkdir(parents=True, exist_ok=True)
        if not cls.PATH.exists():
            instance.write_default_config()
            return instance

        c = instance.read_config_file()
        instance._load_dict(c)
        return instance

    def _load_dict(self, d: Dict[str, Any]) -> None:
        # The only reason we need to do this manually other than using `self.parse_file()` is
        # because we need to call `SearchParameters.from_dict()` manually.
        for field in self.__fields__:
            if field not in [k.lower() for k in d]:
                continue

            attr = getattr(self, field)
            if field == "search":
                setattr(self, field, attr.from_dict(d[field]))
            else:
                setattr(self, field, attr.parse_obj(d[field]))

    def get_default(self) -> Dict[str, Any]:
        data = {}

        for field, value in self.__fields__.items():
            if field == "search":
                data[field] = value.get_default().as_dict()  # Call `SearchParameters.as_dict()`
            else:
                data[field] = value.get_default().dict()

        return data

    def _write_data(self, data: Dict[str, Any]) -> None:
        """Write data into the configuration file."""
        try:
            self.PATH.write_text(json.dumps(data, indent=2))
        except TypeError as e:
            print(f"Error writing data to config file: {e}")
            exit()

    def write_default_config(self) -> None:
        """Create the configuration file and write the default settings to it."""
        self._write_data(self.get_default())

    def write_current_config(self) -> None:
        """Write the current settings into the configuration file."""
        self._write_data(self.dict())

    def read_config_file(self) -> Dict[str, Any]:
        """Read the settings from the configuration file."""
        return json.loads(self.PATH.read_text())

    def update_config(self) -> None:
        in_file = self.read_config_file()
        default = self.get_default()

        for key, value in default.items():
            if key not in in_file:
                in_file[key] = value
                continue

            for k, v in default[key].items():
                if k not in in_file[key]:
                    in_file[key][k] = v

        self._write_data(in_file)


wallhaven_config = Config.setup()
