from typing_extensions import Literal
from dataclasses import dataclass

from wallhaven.models.base import BaseModel


@dataclass
class Tag(BaseModel):
    """Represents a Tag.

    Attributes:
        id (int): The tag ID.
        name (str): The user defined name for the tag.
        alias (str): A comma separated string of aliases for the `name`.
        category (str): The name of the tag's category.
        category_id (int): The ID of the category.
        purity (str): The tag's purity. One of ["sfw", "sketchy", "nsfw"]
        created_at (str): A `%Y-%m-%d %H:%M:%S` string representing the tag's creation
            date. Example: "2014-02-02 23:23:48".
    """

    id: int
    name: str
    alias: str
    category: str
    category_id: int
    purity: Literal["sfw", "sketchy", "nsfw"]
    created_at: str
