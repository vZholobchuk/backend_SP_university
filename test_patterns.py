import pytest
from patterns.strategies import (
    SimpleAverageStrategy,
    WeightedGradeStrategy,
    ECTSRatingStrategy,
    GradeCalculator
)
from patterns.observers import (
    GradeEventPublisher,
    AuditLogObserver,
    NotificationObserver,
    DashboardStatsObserver
)
from patterns.reports import (
    TasksReportCreator,
    AcademicReportCreator
)
from patterns.repositories import InMemoryTaskRepository

# -------------------------------------------------------------------
# 1. ТЕСТИ ДЛЯ ПАТЕРНА STRATEGY
# -------------------------------------------------------------------

def test_simple_average_strategy():
    strategy = SimpleAverageStrategy()
    result = strategy.calculate([90.0, 80.0, 70.0])
    assert result["average"] == 80.0
    assert result["count"] == 3
    assert result["type"] == "simple_average"

def test_simple_average_strategy_empty():
    strategy = SimpleAverageStrategy()
    result = strategy.calculate([])
    assert result["average"] == 0.0
    assert result["count"] == 0

def test_weighted_grade_strategy():
    strategy = WeightedGradeStrategy()
    grades = [90.0, 80.0, 70.0]
    weights = [4.0, 3.0, 3.0] # 360 + 240 + 210 = 810 / 10 = 81.0
    result = strategy.calculate(grades, weights=weights)
    assert result["average"] == 81.0
    assert result["total_weight"] == 10.0

def test_weighted_grade_strategy_errors():
    strategy = WeightedGradeStrategy()
    with pytest.raises(ValueError, match="необхідно вказати вагові коефіцієнти"):
        strategy.calculate([90.0, 80.0])

    with pytest.raises(ValueError, match="не відповідає кількості ваг"):
        strategy.calculate([90.0, 80.0], weights=[1.0])

    with pytest.raises(ValueError, match="не можуть бути від'ємними"):
        strategy.calculate([90.0, 80.0], weights=[2.0, -1.0])

def test_ects_rating_strategy():
    strategy = ECTSRatingStrategy()
    assert strategy.calculate([95.0])["ects"] == "A"
    assert strategy.calculate([85.0])["ects"] == "B"
    assert strategy.calculate([75.0])["ects"] == "C"
    assert strategy.calculate([65.0])["ects"] == "D"
    assert strategy.calculate([60.0])["ects"] == "E"
    assert strategy.calculate([45.0])["ects"] == "FX"
    assert strategy.calculate([20.0])["ects"] == "F"

def test_grade_calculator_runtime_switching():
    calculator = GradeCalculator(SimpleAverageStrategy())
    grades = [100.0, 80.0]
    res1 = calculator.compute(grades)
    assert res1["average"] == 90.0

    # Зміна стратегії на льоту на ECTS
    calculator.set_strategy(ECTSRatingStrategy())
    res2 = calculator.compute(grades)
    assert res2["ects"] == "A"

# -------------------------------------------------------------------
# 2. ТЕСТИ ДЛЯ ПАТЕРНА OBSERVER
# -------------------------------------------------------------------

def test_observer_notifications_and_audit():
    publisher = GradeEventPublisher()
    audit = AuditLogObserver()
    notifications = NotificationObserver()
    dashboard = DashboardStatsObserver()

    publisher.subscribe(audit)
    publisher.subscribe(notifications)
    publisher.subscribe(dashboard)

    # Викладач виставив першу оцінку
    publisher.notify("student_123", "Лабораторна робота 12", "ПППІ", 95.0)

    # Перевірка аудиту
    assert len(audit.logs) == 1
    assert audit.logs[0]["student_id"] == "student_123"
    assert audit.logs[0]["new_grade"] == 95.0

    # Перевірка сповіщень
    assert len(notifications.notifications) == 1
    assert "Лабораторна робота 12" in notifications.notifications[0]
    assert "95.0" in notifications.notifications[0]

    # Перевірка дашборду
    assert dashboard.current_average == 95.0

    # Друга оцінка
    publisher.notify("student_123", "Тест 1", "ПППІ", 85.0)
    assert dashboard.current_average == 90.0
    assert len(audit.logs) == 2

def test_observer_unsubscribe():
    publisher = GradeEventPublisher()
    audit = AuditLogObserver()
    publisher.subscribe(audit)
    publisher.notify("student_1", "Завдання 1", "Мат", 80.0)
    assert len(audit.logs) == 1

    publisher.unsubscribe(audit)
    publisher.notify("student_1", "Завдання 2", "Мат", 90.0)
    # Кількість логів не повинна збільшитись
    assert len(audit.logs) == 1

# -------------------------------------------------------------------
# 3. ТЕСТИ ДЛЯ ПАТЕРНА FACTORY METHOD
# -------------------------------------------------------------------

def test_tasks_report_creator():
    creator = TasksReportCreator()
    mock_data = {
        "student_name": "Іван Петренко",
        "tasks": [
            {"title": "Лаб 1", "status": "Виконано", "grade": 90.0},
            {"title": "Лаб 2", "status": "Виконано", "grade": 100.0},
            {"title": "Лаб 3", "status": "В процесі", "grade": None}
        ]
    }
    report = creator.render(mock_data)
    assert report["report_title"] == "ЗВЕДЕНИЙ ЗВІТ ПО НАВЧАЛЬНИХ ЗАВДАННЯХ"
    stats = report["statistics"]
    assert stats["total_tasks"] == 3
    assert stats["done_count"] == 2
    assert stats["in_progress_count"] == 1
    assert stats["average_grade"] == 95.0
    assert stats["completion_rate_percent"] == 66.7

def test_academic_report_creator():
    creator = AcademicReportCreator()
    mock_data = {
        "student_name": "Іван Петренко",
        "group": "ІПЗ-41",
        "disciplines": [
            {"subject": "ПППІ", "credits": 4, "score": 92.0},
            {"subject": "Бази даних", "credits": 5, "score": 75.0}
        ]
    }
    report = creator.render(mock_data)
    assert report["report_title"] == "ВІДОМІСТЬ АКАДЕМІЧНОЇ УСПІШНОСТІ СТУДЕНТА"
    assert report["overall_average"] == 83.5
    assert len(report["disciplines_details"]) == 2
    assert report["disciplines_details"][0]["ects"] == "A"
    assert report["disciplines_details"][1]["ects"] == "C"

# -------------------------------------------------------------------
# 4. ТЕСТИ ДЛЯ ПАТЕРНА REPOSITORY
# -------------------------------------------------------------------

def test_in_memory_task_repository():
    repo = InMemoryTaskRepository()
    t_id = repo.add("user_1", "Завдання 1", "Основи ПЗ", priority="Високий")
    assert t_id == 1

    task = repo.get(1)
    assert task is not None
    assert task["title"] == "Завдання 1"

    repo.add("user_1", "Завдання 2", "Математика")
    repo.add("user_2", "Завдання 3", "Фізика")

    user_1_tasks = repo.list_by_user("user_1")
    assert len(user_1_tasks) == 2

    # Оновлення
    updated = repo.update(1, status="Виконано", grade=98.0)
    assert updated is True
    assert repo.get(1)["status"] == "Виконано"
    assert repo.get(1)["grade"] == 98.0

    # Видалення
    deleted = repo.delete(1)
    assert deleted is True
    assert repo.get(1) is None
