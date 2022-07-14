from typing import Dict

from wallhaven.models import BaseModel


class Uploader(BaseModel):
    """Represents an Uploader.
    Uploaders are not included in all wallpapers objects.
    Attributes:
        username (str): The username of the uploader.
        group (str): A string determining the type of account. Usually this defined as
            the literal "user".
        avatar (dict): A mapping of the user's avatar in different sizes.
    """

    username: str
    group: str
    avatar: Dict[str, str]
