from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class ITaskRepository(ABC):
    """Абстрактний інтерфейс репозиторію для доступу до навчальних завдань."""
    @abstractmethod
    def add(self, user_id: str, title: str, subject: str, priority: str, status: str, grade: Optional[float] = None) -> int:
        pass

    @abstractmethod
    def get(self, task_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update(self, task_id: int, status: str, grade: Optional[float] = None) -> bool:
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        pass

class InMemoryTaskRepository(ITaskRepository):
    """Конкретна реалізація репозиторію в пам'яті (in-memory) для швидкого тестування."""
    def __init__(self):
        self._storage: Dict[int, Dict[str, Any]] = {}
        self._counter = 1

    def add(self, user_id: str, title: str, subject: str, priority: str = "Середній", 
            status: str = "До виконання", grade: Optional[float] = None) -> int:
        task_id = self._counter
        self._storage[task_id] = {
            "id": task_id,
            "user_id": user_id,
            "title": title,
            "subject": subject,
            "priority": priority,
            "status": status,
            "grade": grade
        }
        self._counter += 1
        return task_id

    def get(self, task_id: int) -> Optional[Dict[str, Any]]:
        return self._storage.get(task_id)

    def list_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        return [task for task in self._storage.values() if task["user_id"] == user_id]

    def update(self, task_id: int, status: str, grade: Optional[float] = None) -> bool:
        if task_id not in self._storage:
            return False
        self._storage[task_id]["status"] = status
        if grade is not None:
            self._storage[task_id]["grade"] = grade
        return True

    def delete(self, task_id: int) -> bool:
        if task_id in self._storage:
            del self._storage[task_id]
            return True
        return False
