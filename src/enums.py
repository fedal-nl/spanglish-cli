from enum import Enum


class CategoryEnum(str, Enum):
    NOUN = "Noun"
    VERB = "Verb"
    ADJECTIVE = "Adjective"
    DAY = "Days"
    MONTH = "Months"
    FOOD = "Food"
    COLOR = "Colors"
    BODY_PART = "Body Parts"
    ANIMAL = "Animals"
    FAMILY = "Family"
    NUMBERS = "Numbers"
    TIME = "Time"
    DIRECTIONS = "Directions"

class TopicEnum(str, Enum):
    GREETINGS = "Greetings"
    WEATHER = "Weather"
    DIRECTIONS = "Directions"
    SONGS = "Songs"
    TIME = "Time"
    FOOD = "Food"

class QuizContentTypeEnum(str, Enum):
    WORD = "word"
    SENTENCE = "sentence"


class LanguageEnum(str, Enum):
    SPANISH = "Spanish"
    ENGLISH = "English"
