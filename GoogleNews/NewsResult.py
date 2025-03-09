from datetime import datetime
from typing import TypedDict


class NewsResult(TypedDict):
    title: str
    media: str
    date: str
    datetime: datetime
    desc: str
    link: str
    img: str
