from dataclasses import dataclass

from src.enums import CategoryEnum


@dataclass
class QuizItem:
    text_id: int
    question: str
    answer: str
    conjugation: dict[str, str] = None  # Only for verbs
    category: CategoryEnum | None = None
