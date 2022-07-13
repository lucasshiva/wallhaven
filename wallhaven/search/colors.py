from typing import Set, Union, Sequence

from pydantic import Field

from wallhaven.search.enums import Color
from wallhaven.search.base import BaseParameter

ColorTypes = Union[str, Sequence[str]]


class ColorManager(BaseParameter):
    colors: Set[Color] = Field(default_factory=set)

    def _parse_color(self, color: Union[Color, str]) -> Color:
        """Instantiates a `Color` object from a string, if needed."""
        if isinstance(color, str):
            color = Color.create(color)

        return color

    def add(self, *colors: Union[Color, str]) -> None:
        """Add one or more colors.

        If the color is already present, this method will do nothing.
        """
        for color in colors:
            color = self._parse_color(color)
            self.colors.add(color)

    def remove(self, *colors: Union[Color, str]) -> None:
        """Remove one or more colors.

        If the color is not present, this method will do nothing.
        """
        for color in colors:
            color = self._parse_color(color)

            try:
                self.colors.remove(color)
            except KeyError:
                pass

    def has_color(self, color: Union[Color, str]) -> bool:
        """Whether the color is present."""
        color = self._parse_color(color)
        if color not in self.colors:
            return False
        return True

    def as_query_param(self) -> str:
        return ",".join(color.as_query_param() for color in self.colors)

    @classmethod
    def create(cls, data: ColorTypes) -> "ColorManager":

        colors: Set[Color] = set()
        if isinstance(data, str):
            colors = {Color.create(c.strip()) for c in data.split(",")}
        elif isinstance(data, Sequence):
            for color in data:
                colors.add(Color.create(color))
        else:
            raise TypeError(
                f"Got type {type(data)} for data, expected one of: {ColorTypes.__args__}"
            )

        return cls(colors=colors)
