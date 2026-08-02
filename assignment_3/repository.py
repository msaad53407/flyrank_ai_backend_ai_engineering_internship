from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import os
import psycopg2
from psycopg2.extras import RealDictCursor


class TaskRepository(ABC):
    @abstractmethod
    def get_all(
        self, search: Optional[str] = None, done: Optional[bool] = None, sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create(self, title: str, done: bool = False) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update(
        self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        pass


class PostgresTaskRepository(TaskRepository):
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@db:5432/tasks_db"
        )

    def _get_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)

    def init_db(self):
        """Creates table and seeds default tasks if empty."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        done BOOLEAN NOT NULL DEFAULT FALSE
                    );
                """)
                cur.execute("SELECT COUNT(*) AS count FROM tasks;")
                count = cur.fetchone()["count"]
                if count == 0:
                    cur.execute("""
                        INSERT INTO tasks (title, done) VALUES
                        ('Complete Assignment', TRUE),
                        ('Go to the gym', TRUE),
                        ('Write about today in journal', FALSE);
                    """)
                conn.commit()

    def get_all(
        self, search: Optional[str] = None, done: Optional[bool] = None, sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT id, title, done FROM tasks"
        conditions = []
        params = []

        if search:
            conditions.append("title ILIKE %s")
            params.append(f"%{search}%")
        if done is not None:
            conditions.append("done = %s")
            params.append(done)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        if sort:
            if sort.lower() == "desc":
                query += " ORDER BY title DESC"
            elif sort.lower() == "asc":
                query += " ORDER BY title ASC"
        else:
            query += " ORDER BY id ASC"

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]

    def get_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (task_id,))
                row = cur.fetchone()
                if row:
                    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
                return None

    def create(self, title: str, done: bool = False) -> Dict[str, Any]:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
                    (title, done),
                )
                row = cur.fetchone()
                conn.commit()
                return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

    def update(
        self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        existing = self.get_by_id(task_id)
        if not existing:
            return None

        new_title = title if title is not None else existing["title"]
        new_done = done if done is not None else existing["done"]

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
                    (new_title, new_done, task_id),
                )
                row = cur.fetchone()
                conn.commit()
                return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

    def delete(self, task_id: int) -> bool:
        existing = self.get_by_id(task_id)
        if not existing:
            return False

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
                conn.commit()
                return True

    def get_stats(self) -> Dict[str, int]:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS total FROM tasks;")
                total = cur.fetchone()["total"]

                cur.execute("SELECT COUNT(*) AS completed FROM tasks WHERE done = TRUE;")
                completed = cur.fetchone()["completed"]

                pending = total - completed
                return {"total_tasks": total, "completed_tasks": completed, "pending_tasks": pending}


class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self.tasks = [
            {"id": 1, "title": "Complete Assignment", "done": True},
            {"id": 2, "title": "Go to the gym", "done": True},
            {"id": 3, "title": "Write about today in journal", "done": False},
        ]

    def get_all(
        self, search: Optional[str] = None, done: Optional[bool] = None, sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        result = self.tasks
        if search:
            result = [t for t in result if search.lower() in t["title"].lower()]
        if done is not None:
            result = [t for t in result if t["done"] == done]
        if sort == "asc":
            result = sorted(result, key=lambda t: t["title"])
        elif sort == "desc":
            result = sorted(result, key=lambda t: t["title"], reverse=True)
        return result

    def get_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def create(self, title: str, done: bool = False) -> Dict[str, Any]:
        new_id = (max([t["id"] for t in self.tasks]) if self.tasks else 0) + 1
        new_task = {"id": new_id, "title": title, "done": done}
        self.tasks.append(new_task)
        return new_task

    def update(
        self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        task = self.get_by_id(task_id)
        if not task:
            return None
        if title is not None:
            task["title"] = title
        if done is not None:
            task["done"] = done
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)
        if not task:
            return False
        self.tasks.remove(task)
        return True

    def get_stats(self) -> Dict[str, int]:
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["done"])
        return {"total_tasks": total, "completed_tasks": completed, "pending_tasks": total - completed}
