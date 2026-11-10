import sqlite3
from typing import Optional, List, Dict, Any

class TaskRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.db = connection
        self.create_tables()

    def create_tables(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                grade REAL
            )
        """)
        self.db.commit()

    def add_task(self, user_id: str, title: str, subject: str, priority: str = "Середній", 
                 status: str = "До виконання", grade: Optional[float] = None) -> int:
        cursor = self.db.execute(
            """INSERT INTO tasks (user_id, title, subject, priority, status, grade) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, title, subject, priority, status, grade)
        )
        self.db.commit()
        return cursor.lastrowid

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.execute(
            "SELECT id, user_id, title, subject, priority, status, grade FROM tasks WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "user_id": row[1],
            "title": row[2],
            "subject": row[3],
            "priority": row[4],
            "status": row[5],
            "grade": row[6]
        }

    def get_user_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.db.execute(
            "SELECT id, user_id, title, subject, priority, status, grade FROM tasks WHERE user_id = ?",
            (user_id,)
        )
        rows = cursor.fetchall()
        return [
            {
                "id": r[0],
                "user_id": r[1],
                "title": r[2],
                "subject": r[3],
                "priority": r[4],
                "status": r[5],
                "grade": r[6]
            }
            for r in rows
        ]

    def update_task_status_and_grade(self, task_id: int, status: str, grade: Optional[float] = None) -> bool:
        cursor = self.db.execute(
            "UPDATE tasks SET status = ?, grade = ? WHERE id = ?",
            (status, grade, task_id)
        )
        self.db.commit()
        return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        cursor = self.db.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )
        self.db.commit()
        return cursor.rowcount > 0
