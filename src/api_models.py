"""Typed Pydantic models for the versioned Spanglish HTTP API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Reference(BaseModel):
    """Represent a selectable API reference value."""

    id: int
    name: str


class Language(Reference):
    """Represent an API language and its stable code."""

    code: str


class Category(Reference):
    """Represent a quiz category with an optional availability count."""

    available_questions: int = 0


class QuizOptions(BaseModel):
    """Contain all values needed to render the quiz setup prompts."""

    languages: list[Language]
    categories: list[Category]
    chapters: list[Reference]
    selection_modes: list[str]
    question_types: list[str]
    default_question_count: int
    maximum_question_count: int


class Translation(BaseModel):
    """Represent one accepted translation returned by the API."""

    id: int
    language_id: int
    translation: str


class Conjugation(BaseModel):
    """Represent one structured verb form returned by the API."""

    id: int
    tense: str
    mood: str
    pronoun: str
    form: str


class Vocabulary(BaseModel):
    """Represent a complete vocabulary card."""

    id: int
    text: str
    language: Language
    chapter: Reference | None
    song: "Song | None" = None
    categories: list[Reference]
    translations: list[Translation]
    verb_conjugations: list[Conjugation]
    created_at: datetime


class Song(BaseModel):
    """A selectable song with its artist."""

    id: int
    title: str
    artist: Reference


class VocabularyPage(BaseModel):
    """Represent a paginated vocabulary response."""

    items: list[Vocabulary]
    total: int
    page: int
    page_size: int


class QuizQuestion(BaseModel):
    """Represent a locally executable translation or conjugation question."""

    id: str
    vocabulary_id: int
    type: str
    prompt: str
    accepted_answers: list[str] | dict[str, list[str]]
    category_ids: list[int]


class Quiz(BaseModel):
    """Represent a complete quiz fetched in one API call."""

    quiz_id: int
    generated_at: datetime
    requested_question_count: int
    actual_question_count: int
    configuration: dict[str, Any]
    warnings: list[str]
    questions: list[QuizQuestion]


class Attempt(BaseModel):
    """Represent one answer collected locally by the CLI."""

    question_id: str
    answer: str | dict[str, str]
    response_time_ms: int | None = Field(default=None, ge=0)


class Score(BaseModel):
    """Represent the authoritative score calculated by the API."""

    correct: int
    incorrect: int
    total: int
    percentage: float


class AttemptEvaluation(BaseModel):
    """Represent the API's authoritative evaluation of one quiz answer."""

    question_id: str
    correct: bool
    score: float
    accepted_answers: list[str] | dict[str, list[str]]
    feedback: str


class QuizResult(BaseModel):
    """Represent a completed quiz result and server advice."""

    result_id: int
    quiz_id: int
    score: Score
    attempts: list[AttemptEvaluation]
    advice: dict[str, Any]


class QuizHistoryItem(BaseModel):
    """Represent one completed quiz in the learner's score history."""

    quiz_id: int
    completed_at: datetime
    correct: int
    total: int
    percentage: float
