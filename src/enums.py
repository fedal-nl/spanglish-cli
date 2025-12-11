from enum import Enum


class CategoryEnum(str, Enum):
    NOUN = "Noun"
    VERB = "Verb"
    ADJECTIVE = "Adjective"
    DAY = "Days"
    MONTH = "Months"
    COLOR = "Colors"
    BODY_PART = "Body Parts"
    ANIMAL = "Animals"
    FAMILY = "Family"
    NUMBERS = "Numbers"
    TIME = "Time"
    DIRECTIONS = "Directions"
    GREETINGS = "Greetings"
    WEATHER = "Weather"
    SONGS = "Songs"
    FOOD = "Food"

class LanguageEnum(str, Enum):
    SPANISH = "Spanish"
    ENGLISH = "English"
