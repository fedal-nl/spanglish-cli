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
