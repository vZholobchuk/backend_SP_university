from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

class Report(ABC):
    """Абстрактний базовий клас продукту (Product) звіту."""
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class TasksSummaryReport(Report):
    """Конкретний звіт: Зведена аналітика навчальних завдань студента."""
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tasks: List[Dict[str, Any]] = data.get("tasks", [])
        total = len(tasks)
        done = sum(1 for t in tasks if t.get("status") == "Виконано")
        in_progress = sum(1 for t in tasks if t.get("status") == "В процесі")
        todo = sum(1 for t in tasks if t.get("status") == "До виконання")
        
        grades = [t["grade"] for t in tasks if t.get("grade") is not None]
        avg_grade = round(sum(grades) / len(grades), 2) if grades else 0.0

        return {
            "report_title": "ЗВЕДЕНИЙ ЗВІТ ПО НАВЧАЛЬНИХ ЗАВДАННЯХ",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "student_name": data.get("student_name", "Студент"),
            "statistics": {
                "total_tasks": total,
                "done_count": done,
                "in_progress_count": in_progress,
                "todo_count": todo,
                "completion_rate_percent": round((done / total * 100), 1) if total > 0 else 0.0,
                "average_grade": avg_grade
            }
        }

class AcademicPerformanceReport(Report):
    """Конкретний звіт: Офіційна відомість академічної успішності за семестр."""
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        disciplines: List[Dict[str, Any]] = data.get("disciplines", [])
        total_score = 0.0
        details = []

        for item in disciplines:
            score = item.get("score", 0.0)
            ects = "A" if score >= 90 else ("B" if score >= 82 else ("C" if score >= 74 else ("D" if score >= 64 else ("E" if score >= 60 else "F"))))
            passed = score >= 60.0
            details.append({
                "subject": item.get("subject"),
                "credits": item.get("credits", 3),
                "score": score,
                "ects": ects,
                "status": "Зараховано" if passed else "Не зараховано"
            })
            total_score += score

        overall_avg = round(total_score / len(disciplines), 2) if disciplines else 0.0

        return {
            "report_title": "ВІДОМІСТЬ АКАДЕМІЧНОЇ УСПІШНОСТІ СТУДЕНТА",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "student_name": data.get("student_name", "Студент"),
            "group": data.get("group", "ІПЗ-41"),
            "overall_average": overall_avg,
            "disciplines_details": details
        }

class ReportCreator(ABC):
    """Базовий клас творця (Creator) із фабричним методом create_report()."""
    @abstractmethod
    def create_report(self) -> Report:
        """Фабричний метод, що перевизначається в підкласах."""
        pass

    def render(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Клієнтський метод, який використовує продукт, створений фабричним методом."""
        report = self.create_report()
        return report.generate(data)

class TasksReportCreator(ReportCreator):
    """Конкретний творець звіту за завданнями."""
    def create_report(self) -> Report:
        return TasksSummaryReport()

class AcademicReportCreator(ReportCreator):
    """Конкретний творець звіту про академічну успішність."""
    def create_report(self) -> Report:
        return AcademicPerformanceReport()
