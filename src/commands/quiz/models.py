from dataclasses import dataclass

from src.enums import CategoryEnum, QuizContentTypeEnum, TopicEnum


@dataclass
class QuizItem:
    content_type_id: int
    content_type: QuizContentTypeEnum
    question: str
    answer: str
    conjugation: dict[str, str] = None  # Only for verbs
    category: CategoryEnum | TopicEnum = None
