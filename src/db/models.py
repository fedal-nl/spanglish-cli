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


class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True)
    dictionary_id = Column(Integer, ForeignKey(
        "dictionary.id",
        name="fk_translation_dictionary_id_dictionary"
        ), nullable=False)
    translation = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("dictionary_id", "translation"),
    )

    dictionary = relationship("Dictionary", back_populates="translations")

class Verb(Base):
    __tablename__ = "verbs"

    id = Column(Integer, primary_key=True)
    dictionary_id = Column(Integer, ForeignKey(
        "dictionary.id",
        name="fk_verb_dictionary_id_dictionary"
    ), nullable=False, unique=True)
    yo = Column(String)
    tu = Column(String)
    ella_el = Column(String)
    nosotros = Column(String)
    vosotros = Column(String)
    ellos_ellas = Column(String)

    dictionary = relationship("Dictionary", back_populates="verb")


class Dictionary(Base):
    __tablename__ = "dictionary"

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False, index=True)
    category = Column(Enum(CategoryEnum), nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.now, index=True)
    # Relationship to verbs
    verb = relationship("Verb", back_populates="dictionary", uselist=False)
    # Relationship to translations
    translations = relationship(
        "Translation",
        back_populates="dictionary",
        cascade="all, delete-orphan"
    )

    # create constraints to ensure word uniqueness
    __table_args__ = (
        UniqueConstraint("text", "category"),
    )

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

    # foreign key to dictionary table
    dictionary_id = Column(Integer, ForeignKey(
        "dictionary.id",
        name="fk_quizattempt_dictionary_id_dictionary"
    ), nullable=False)
    answer = Column(String, nullable=False)
    # whether the answer was correct or not, for statistics
    answered_correctly = Column(Boolean, nullable=False, index=True)
    answered_at = Column(DateTime, default=datetime.now, index=True)
    session_id = Column(Integer, ForeignKey(
        "quiz_sessions.id",
        name="fk_quizattempt_session_id_quizsessions"
    ), nullable=False)

    session = relationship("QuizSession", back_populates="attempts")
