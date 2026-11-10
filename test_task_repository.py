import sqlite3
import pytest
from task_repository import TaskRepository

@pytest.fixture
def repo():
    connection = sqlite3.connect(":memory:")
    repository = TaskRepository(connection)
    yield repository
    connection.close()

def test_add_task_integration(repo):
    """IT-001: Додавання навчального завдання до бази даних"""
    task_id = repo.add_task(
        user_id="user_123",
        title="Лабораторна робота 11",
        subject="ПППІ",
        priority="Високий",
        status="В процесі",
        grade=None
    )
    assert task_id is not None
    assert task_id > 0

    task = repo.get_task(task_id)
    assert task is not None
    assert task["title"] == "Лабораторна робота 11"
    assert task["subject"] == "ПППІ"
    assert task["user_id"] == "user_123"
    assert task["status"] == "В процесі"

def test_get_user_tasks_integration(repo):
    """IT-002: Вибірка завдань для конкретного користувача"""
    repo.add_task("user_1", "Завдання 1", "Математика")
    repo.add_task("user_1", "Завдання 2", "Фізика")
    repo.add_task("user_2", "Завдання 3", "Історія")

    user_1_tasks = repo.get_user_tasks("user_1")
    assert len(user_1_tasks) == 2

    user_2_tasks = repo.get_user_tasks("user_2")
    assert len(user_2_tasks) == 1
    assert user_2_tasks[0]["title"] == "Завдання 3"

def test_update_task_integration(repo):
    """IT-003: Оновлення статусу та виставлення оцінки за завдання"""
    task_id = repo.add_task("user_123", "Курсова робота", "Програмування", status="В процесі")
    
    updated = repo.update_task_status_and_grade(task_id, status="Виконано", grade=95.0)
    assert updated is True

    task = repo.get_task(task_id)
    assert task["status"] == "Виконано"
    assert task["grade"] == 95.0

def test_delete_task_integration(repo):
    """IT-004: Видалення завдання з бази даних"""
    task_id = repo.add_task("user_123", "Тестовий таск", "Тест")
    assert repo.get_task(task_id) is not None

    deleted = repo.delete_task(task_id)
    assert deleted is True

    assert repo.get_task(task_id) is None
