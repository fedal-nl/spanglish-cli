from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    UniqueConstraint,
    DateTime,
    Boolean
)
from sqlalchemy.orm import relationship
from .base import Base
from src.enums import CategoryEnum
from datetime import datetime

class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False, unique=True)
    category = Column(Enum(CategoryEnum), nullable=False)

    # Relationship to verbs
    verb = relationship("Verb", back_populates="word", uselist=False)
    
    # Relationship to translations
    translations = relationship("Translation", back_populates="word", cascade="all, delete-orphan")
    quiz = relationship("Quiz", back_populates="word", cascade="all, delete-orphan")

class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    translation = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("word_id", "translation"),
    )

    word = relationship("Word", back_populates="translations")

class Verb(Base):
    __tablename__ = "verbs"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False, unique=True)

    yo = Column(String)
    tu = Column(String)
    ella_el = Column(String)
    nosotros = Column(String)
    vosotros = Column(String)
    ellos_ellas = Column(String)

    word = relationship("Word", back_populates="verb")


class Quiz(Base):
    __tablename__ = "quizes"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    is_correct = Column(Boolean, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now, index=True)

    word = relationship("Word", back_populates="quiz")
