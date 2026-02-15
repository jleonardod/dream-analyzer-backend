from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class DreamCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., min_length=1, description="Contenido del sueño")
    tags: Optional[List[str]] = Field(None, description="Tags del sueño")

class DreamUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None

class DreamResponse(BaseModel):
    id: int
    title: Optional[str]
    content: str
    tags: Optional[List[str]]
    emotion: Optional[str]
    emotion_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class WordFrequency(BaseModel):
    word: str
    count: int
    percentage: float

class DreamStats(BaseModel):
    total_dreams: int
    total_words: int
    avg_words_per_dream: float
    most_common_words: List[WordFrequency]
    emmotions_distribution: dict
    tags_distribution: dict
    dreams_by_month: dict

class DreamAnalysis(BaseModel):
    keywords: List[str]
    word_count: int
    emotion: Optional[str]
    emotion_score: Optional[float]
    suggested_tags: List[str]
