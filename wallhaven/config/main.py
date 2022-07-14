import json
from pathlib import Path
from typing import Any, ClassVar, Dict

import click

from wallhaven.search import SearchParameters
from wallhaven.config import APISettings, DownloadSettings
from wallhaven.models import BaseModel


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
            obj = value.get_default()
            if hasattr(obj, "as_dict"):
                data[field] = obj.as_dict()
            else:
                data[field] = obj.dict()

        return data

    def _write_data(self, data: Dict[str, Any]) -> None:
        """Write data into the configuration file."""
        self.PATH.write_text(json.dumps(data, indent=2))

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
