"""
format of our request
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal

cards = Literal["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


class front_json(BaseModel):
    delt: list[cards] = Field(min_length=2)
    dealer: cards


class response(BaseModel):
    action: Literal["hit", "stand", "double"]
    win: float
    lose: float
    tie: float
    bust: float
    hand_value: int
    is_soft: bool
