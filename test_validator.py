import pytest
from validator import (
    validate_email,
    validate_password,
    validate_grade,
    calculate_average_grade,
    calculate_ects_grade,
    determine_urgency
)

def test_validate_email_valid():
    assert validate_email("student@pnu.edu.ua") is True
    assert validate_email("user.name+test@domain.com") is True

def test_validate_email_invalid():
    assert validate_email("plainaddress") is False
    assert validate_email("@missingusername.com") is False
    assert validate_email("user@.com") is False

def test_validate_email_type_error():
    with pytest.raises(TypeError):
        validate_email(12345)

def test_validate_password_valid():
    assert validate_password("Pass123") is True
    assert validate_password("student2026") is True

def test_validate_password_invalid_short_or_simple():
    assert validate_password("12345") is False
    assert validate_password("passw") is False
    assert validate_password("onlyletters") is False
    assert validate_password("12345678") is False

def test_validate_grade_boundaries():
    assert validate_grade(0) is True
    assert validate_grade(100) is True
    assert validate_grade(85.5) is True

def test_validate_grade_out_of_range():
    with pytest.raises(ValueError):
        validate_grade(-1)
    with pytest.raises(ValueError):
        validate_grade(101)

def test_validate_grade_type_error():
    with pytest.raises(TypeError):
        validate_grade("відмінно")
    with pytest.raises(TypeError):
        validate_grade(True)

def test_calculate_average_grade_normal():
    grades = [90, 80, 70]
    assert calculate_average_grade(grades) == 80.0
    assert calculate_average_grade([95, 88, 92]) == 91.67

def test_calculate_average_grade_empty_list():
    with pytest.raises(ValueError):
        calculate_average_grade([])

def test_calculate_ects_grade():
    assert calculate_ects_grade(95) == "A"
    assert calculate_ects_grade(85) == "B"
    assert calculate_ects_grade(75) == "C"
    assert calculate_ects_grade(65) == "D"
    assert calculate_ects_grade(60) == "E"
    assert calculate_ects_grade(45) == "FX"
    assert calculate_ects_grade(20) == "F"

def test_determine_urgency():
    assert determine_urgency(-1) == "Прострочено"
    assert determine_urgency(1) == "Критичний"
    assert determine_urgency(5) == "Терміновий"
    assert determine_urgency(14) == "Звичайний"
