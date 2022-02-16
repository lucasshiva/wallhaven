from typing import List
from typing_extensions import Literal
from dataclasses import dataclass

from wallhaven.models.base import BaseModel


@dataclass
class UserSettings(BaseModel):
    """Represents an user's browsing settings.

    These settings are read-only, which means that we can't modify them through the API.
    Also, they can be used automatically when performing a search. To achieve that, we
    simply need to perform a search with the only parameter being the user's API key.
    Wallhaven will automatically make use of these settings to return results that
    match them.

    Attributes:
        thumb_size (str): The thumbnail size when browsing for images.
        per_page (str): The amount of images per page when browsing for images.
        purity (list): A list of the enabled purities to match.
        categories (list): A list of the enabled categories to match.
        resolutions (list): A list of the resolutions to match.
        aspect_ratios (list): A list of the aspect ratios to match.
        toplist_range (str): The default toplist range.
        tag_blacklist (list): A list of tags to exclude.
        user_blacklist (list): A list of users to exclude.
    """

    thumb_size: Literal["original", "small", "large"]
    per_page: Literal["24", "32", "64"]
    purity: List[str]
    categories: List[str]
    resolutions: List[str]
    aspect_ratios: List[str]
    toplist_range: Literal["1d", "3d", "1w", "1M", "3M", "6M", "1y"]
    tag_blacklist: List[str]
    user_blacklist: List[str]
