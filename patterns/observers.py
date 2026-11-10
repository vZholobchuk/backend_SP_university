from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

class GradeObserver(ABC):
    """Абстрактний спостерігач (Observer) за змінами та виставленням оцінок."""
    @abstractmethod
    def update(self, student_id: str, task_title: str, subject: str, grade: float):
        pass

class GradeEventPublisher:
    """Видавець подій (Subject / Observable), який керує підписниками та сповіщає їх."""
    def __init__(self):
        self._observers: List[GradeObserver] = []

    def subscribe(self, observer: GradeObserver):
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: GradeObserver):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, student_id: str, task_title: str, subject: str, grade: float):
        for observer in self._observers:
            observer.update(student_id, task_title, subject, grade)

class AuditLogObserver(GradeObserver):
    """Спостерігач для фіксації змін оцінок у журналі аудиту безпеки."""
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def update(self, student_id: str, task_title: str, subject: str, grade: float):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "student_id": student_id,
            "subject": subject,
            "task_title": task_title,
            "new_grade": grade,
            "action": "GRADE_REGISTERED"
        }
        self.logs.append(log_entry)

class NotificationObserver(GradeObserver):
    """Спостерігач для формування сповіщень (Push / In-App) для студента."""
    def __init__(self):
        self.notifications: List[str] = []

    def update(self, student_id: str, task_title: str, subject: str, grade: float):
        message = (
            f"🔔 Студент {student_id}: Оновлено оцінку з дисципліни «{subject}»! "
            f"Завдання: «{task_title}» — {grade} балів."
        )
        self.notifications.append(message)

class DashboardStatsObserver(GradeObserver):
    """Спостерігач для автоматичного оновлення показників успішності на Дашборді."""
    def __init__(self):
        self.total_evaluations: int = 0
        self.total_points: float = 0.0

    def update(self, student_id: str, task_title: str, subject: str, grade: float):
        self.total_evaluations += 1
        self.total_points += grade

    @property
    def current_average(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        return round(self.total_points / self.total_evaluations, 2)
