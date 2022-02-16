# mypy: allow-untyped-defs
import json
from typing import Dict, Any

import httpx


class BaseModel:
    """Base model class with methods that other models will inherit."""

    def __init__(self, **kwargs: Any) -> None:
        self._data: Dict[str, Any] = {}

    def as_dict(self) -> Dict[str, Any]:
        """Return the instance as a dictionary."""
        return self._data

    def as_json(self, **kwargs: Any) -> str:
        """Return the instance as a JSON string.

        Args:
            **kwargs: Optional keyword arguments that `json.dumps` takes.
        """
        return json.dumps(self.as_dict(), **kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Return an instance of `cls` from `data`.

        Args:
            data (dict): The data returned from the API.
        """
        # Save the original data.
        cls._data = data.copy()
        return cls(**data)

    @classmethod
    def from_response(cls, response: httpx.Response):
        """Return an instance of ``cls`` from a response object."""
        data: dict = response.json()["data"]

        return cls.from_dict(data)
