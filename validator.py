import re
from datetime import datetime
from typing import List, Union

def validate_email(email: str) -> bool:
    if not isinstance(email, str):
        raise TypeError("Email повинен бути рядком")
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))

def validate_password(password: str) -> bool:
    if not isinstance(password, str):
        raise TypeError("Пароль повинен бути рядком")
    if len(password) < 6:
        return False
    has_digit = any(char.isdigit() for char in password)
    has_letter = any(char.isalpha() for char in password)
    return has_digit and has_letter

def validate_grade(grade: Union[int, float]) -> bool:
    if not isinstance(grade, (int, float)) or isinstance(grade, bool):
        raise TypeError("Оцінка повинна бути числом")
    if grade < 0 or grade > 100:
        raise ValueError("Оцінка має бути в межах від 0 до 100 балів")
    return True

def calculate_average_grade(grades: List[Union[int, float]]) -> float:
    if not isinstance(grades, list):
        raise TypeError("Параметр grades має бути списком")
    if not grades:
        raise ValueError("Список оцінок не може бути порожнім")
    for g in grades:
        validate_grade(g)
    return round(sum(grades) / len(grades), 2)

def calculate_ects_grade(score: Union[int, float]) -> str:
    validate_grade(score)
    if score >= 90:
        return "A"
    elif score >= 82:
        return "B"
    elif score >= 74:
        return "C"
    elif score >= 64:
        return "D"
    elif score >= 60:
        return "E"
    elif score >= 35:
        return "FX"
    else:
        return "F"

def determine_urgency(days_remaining: int) -> str:
    if not isinstance(days_remaining, int):
        raise TypeError("Кількість днів має бути цілим числом")
    if days_remaining < 0:
        return "Прострочено"
    elif days_remaining <= 2:
        return "Критичний"
    elif days_remaining <= 7:
        return "Терміновий"
    else:
        return "Звичайний"
