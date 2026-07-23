from pydantic import BaseModel, Field
from typing import Literal


class ReviewAnalysis(BaseModel):
    rating: int = Field(ge=1, le=5)
    sentiment: Literal["positive", "neutral", "negative"]
    confidence: float = Field(ge=0, le=1)
    summary: str
