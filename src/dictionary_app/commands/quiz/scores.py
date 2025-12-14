'''
This module contains functions to calculate quiz scores.
'''

def get_score(question: str, answer: str) -> bool:
    """Calculate score for a given question and answer.
    This function will return True if the answer matches the
    question (case insensitive), otherwise it returns False.
    Args:
        question (str): The quiz question.
        answer (str): The user's answer.
    Returns:
        bool: True if the answer is correct, False otherwise.
    """
    return question.strip().lower() == answer.strip().lower()
