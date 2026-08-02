import sqlite3
from typing import Dict, List, Optional, Any

DB_FILE = "tasks.db"


def get_db_path(custom_path: Optional[str] = None) -> str:
    return custom_path if custom_path is not None else DB_FILE


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the SQLite database, create tables, and seed initial data if empty."""
    target = get_db_path(db_path)
    with get_db_connection(target) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        
        cursor.execute("SELECT COUNT(*) AS count FROM tasks")
        count = cursor.fetchone()["count"]
        
        if count == 0:
            example_tasks = [
                ("Complete Assignment", True),
                ("Go to the gym", True),
                ("Write about today in journal", False),
            ]
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                example_tasks
            )
        conn.commit()


def reset_db(db_path: Optional[str] = None) -> None:
    """Drop tasks table and re-initialize with default seed tasks."""
    target = get_db_path(db_path)
    with get_db_connection(target) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tasks")
        conn.commit()
    init_db(target)


def get_all_tasks(
    search: Optional[str] = None,
    done: Optional[bool] = None,
    sort: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    query = "SELECT id, title, done FROM tasks"
    conditions = []
    params: List[Any] = []

    if search:
        conditions.append("title LIKE ?")
        params.append(f"%{search}%")
    if done is not None:
        conditions.append("done = ?")
        params.append(1 if done else 0)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort:
        if sort.lower() == "desc":
            query += " ORDER BY title DESC"
        elif sort.lower() == "asc":
            query += " ORDER BY title ASC"
    else:
        query += " ORDER BY id ASC"

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]


def get_task_by_id(task_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row:
            return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        return None


def create_task(title: str, done: bool = False, db_path: Optional[str] = None) -> Dict[str, Any]:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 1 if done else 0))
        conn.commit()
        new_id = cursor.lastrowid
        return {"id": new_id, "title": title, "done": done}


def update_task(
    task_id: int,
    title: Optional[str] = None,
    done: Optional[bool] = None,
    db_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    existing = get_task_by_id(task_id, db_path=db_path)
    if not existing:
        return None

    new_title = title if title is not None else existing["title"]
    new_done = done if done is not None else existing["done"]

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, 1 if new_done else 0, task_id)
        )
        conn.commit()
        return {"id": task_id, "title": new_title, "done": new_done}


def delete_task(task_id: int, db_path: Optional[str] = None) -> bool:
    existing = get_task_by_id(task_id, db_path=db_path)
    if not existing:
        return False

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return True


def get_task_stats(db_path: Optional[str] = None) -> Dict[str, int]:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM tasks")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS completed FROM tasks WHERE done = 1")
        completed = cursor.fetchone()["completed"]

        pending = total - completed
        return {"total_tasks": total, "completed_tasks": completed, "pending_tasks": pending}
