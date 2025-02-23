from datetime import datetime
from typing import TypedDict


class Result(TypedDict):
    title: str
    media: str
    date: str
    datetime: datetime
    desc: str
    link: str
    img: str
