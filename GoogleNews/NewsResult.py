from datetime import datetime
from typing import TypedDict


class NewsResult(TypedDict):
    title: str
    media: str
    date: str
    datetime: datetime | None
    desc: str
    link: str
    img: str
    site: str | None
    reporter: str | None
