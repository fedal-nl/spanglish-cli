from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.enums import CategoryEnum

from .base import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False, index=True)
    category = Column(Enum(CategoryEnum), nullable=False, index=True)

    # Relationship to verbs
    verb = relationship("Verb", back_populates="word", uselist=False)

    # Relationship to translations
    translations = relationship(
        "Translation",
        back_populates="word",
        cascade="all, delete-orphan"
    )
    quiz_attempts = relationship(
        "QuizAttempt",
        back_populates="word",
        cascade="all, delete-orphan"
    )

    # create a constraint to ensure word uniqueness
    __table_args__ = (
        UniqueConstraint("word", "category"),
    )

class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey(
        "words.id",
        name="fk_translation_word_id_words"
        ), nullable=False)
    translation = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("word_id", "translation"),
    )

    word = relationship("Word", back_populates="translations")

class Verb(Base):
    __tablename__ = "verbs"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey(
        "words.id",
        name="fk_verb_word_id_words"
    ), nullable=False, unique=True)
    yo = Column(String)
    tu = Column(String)
    ella_el = Column(String)
    nosotros = Column(String)
    vosotros = Column(String)
    ellos_ellas = Column(String)

    word = relationship("Word", back_populates="verb")


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now, index=True)

    attempts = relationship(
        "QuizAttempt",
        back_populates="session",
        cascade="all, delete-orphan"
    )

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey(
        "words.id",
        name="fk_quizattempt_word_id_words"
        ), nullable=False)
    answered_correctly = Column(Boolean, nullable=False, index=True)
    answered_at = Column(DateTime, default=datetime.now, index=True)
    session_id = Column(Integer, ForeignKey(
        "quiz_sessions.id",
        name="fk_quizattempt_session_id_quizsessions"
    ), nullable=False)

    word = relationship("Word", back_populates="quiz_attempts")
    session = relationship("QuizSession", back_populates="attempts")
