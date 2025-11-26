from enum import Enum

class CategoryEnum(str, Enum):
    NOUN = "Noun"
    VERB = "Verb"
    ADJECTIVE = "Adjective"
    DAY = "Days"
    MONTH = "Months"
    FOOD = "Food"
