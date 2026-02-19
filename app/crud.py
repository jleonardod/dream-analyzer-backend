from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime
from collections import Counter

from app import models, schemas
from app.analyzer import analyze_dream_text, get_word_frequency

def get_dream(db: Session, dream_id: int) -> Optional[models.Dream]:
    return db.query(models.Dream).filter(models.Dream.id == dream_id).first()

def get_dreams(db: Session, skip: int = 0, limit: int = 100) -> List[models.Dream]:
    return db.query(models.Dream).order_by(models.Dream.created_at.desc()).offset(skip).limit(limit).all()

def create_dream(db: Session, dream: schemas.DreamCreate) -> models.Dream:
    analysis = analyze_dream_text(dream.content)

    user_tags = dream.tags if dream.tags else []
    suggested_tags = analysis['suggested_tags']
    all_tags = list(set(user_tags + suggested_tags))

    db_dream = models.Dream(
        title=dream.title,
        content=dream.content,
        tags=",".join(all_tags) if all_tags else None,
        emotion=analysis['emotion'],
        emotion_score=analysis['emotion_score']
    )

    db.add(db_dream)
    db.commit()
    db.refresh(db_dream)

    return db_dream

def update_dream(db: Session, dream_id: int, dream: schemas.DreamUpdate) -> Optional[models.Dream]:
    db_dream = get_dream(db, dream_id)

    if not db_dream:
        return None
    
    if dream.title is not None:
        db_dream.title = dream.title

    if dream.content is not None:
        db_dream.content = dream.content

        analysis = analyze_dream_text(dream.content)
        db_dream.emotion = analysis['emotion']
        db_dream.emotion_score = analysis['emotion_score']

    if dream.tags is not None:
        db_dream.tags = ','.join(dream.tags) if dream.tags else None

    db.commit()
    db.refresh(db_dream)

    return db_dream

def delete_dream(db: Session, dream_id: int) -> bool:
    db_dream = get_dream(db, dream_id)

    if not db_dream:
        return False
    
    db.delete(db_dream)
    db.commit()

    return True

def get_dream_statistics(db: Session) -> schemas.DreamStats:
    dreams = db.query(models.Dream).all()

    if not dreams:
        return schemas.DreamStats(
            total_dreams=0,
            total_words=0,
            avg_words_per_dream=0,
            most_common_words=[],
            emmotions_distribution={},
            tags_distribution={},
            dreams_by_month={}
        )
    
    contents = [d.content for d in dreams]

    word_freq = get_word_frequency(contents, top_n=30)
    
    total_words = sum(len(content.split()) for content in contents)
    avg_words = total_words / len(dreams) if dreams else 0

    emotions = [d.emotion for d in dreams if d.emotion]
    emotion_counts = Counter(emotions)
    emotions_distribution = dict(emotion_counts)

    all_tags = []
    for dream in dreams:
        if dream.tags:
            all_tags.extend(dream.tags.split(','))
    tag_counts = Counter(all_tags)
    tags_distribution = dict(tag_counts.most_common(20))

    dreams_by_month = {}

    for dream in dreams:
        month_key = dream.created_at.strftime('%Y-%m')
        dreams_by_month[month_key] = dreams_by_month.get(month_key, 0) + 1

    return schemas.DreamStats(
        total_dreams=len(dreams),
        total_words=total_words,
        avg_words_per_dream=round(avg_words, 2),
        most_common_words=word_freq,
        emotions_distribution=emotions_distribution,
        tags_distribution=tags_distribution,
        dreams_by_month=dreams_by_month
    )

def search_dreams(db: Session, query: str) -> List[models.Dream]:
    search_pattern = f"%{query}%"
    return db.query(models.Dream).filter(
        (models.Dream.content.ilike(search_pattern)) | (models.Dream.title.ilike(search_pattern))
    ).order_by(models.Dream.created_at.desc()).all()

def get_dreams_by_tag(db: Session, tag: str) -> List[models.Dream]:
    search_pattern = f"%{tag}%"
    return db.query(models.Dream).filter(
        models.Dream.tags.ilike(search_pattern)
    ).order_by(models.Dream.created_at.desc()).all()

def get_dreams_by_emotion(db: Session, emotion: str) -> List[models.Dream]:
    return db.query(models.Dream).filter(
        models.Dream.emotion == emotion
    ).order_by(models.Dream.created_at.desc()).all()
