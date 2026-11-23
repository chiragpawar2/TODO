"""The household's memory: people, tasks, chores, shopping list, remembered facts.

Everything lives in one SQLite file, so the whole household state is a single
file you can copy to the Raspberry Pi later or back up to a USB stick.
"""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, date
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS people (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    role        TEXT DEFAULT 'member',
    notes       TEXT DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    person_id   INTEGER REFERENCES people(id),
    due         TEXT,
    priority    TEXT DEFAULT 'normal',
    status      TEXT DEFAULT 'open',
    notes       TEXT DEFAULT '',
    created_by  TEXT,
    created_at  TEXT NOT NULL,
    done_at     TEXT
);

CREATE TABLE IF NOT EXISTS chores (
    id            INTEGER PRIMARY KEY,
    title         TEXT NOT NULL,
    person_id     INTEGER REFERENCES people(id),
    recurrence    TEXT DEFAULT 'daily',
    last_done_at  TEXT,
    last_done_by  TEXT,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shopping (
    id          INTEGER PRIMARY KEY,
    item        TEXT NOT NULL,
    qty         TEXT DEFAULT '',
    added_by    TEXT,
    status      TEXT DEFAULT 'needed',
    created_at  TEXT NOT NULL,
    bought_at   TEXT
);

CREATE TABLE IF NOT EXISTS facts (
    id          INTEGER PRIMARY KEY,
    person_id   INTEGER REFERENCES people(id),
    text        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY,
    speaker     TEXT,
    role        TEXT NOT NULL,
    text        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Store:
    def __init__(self, path: str | Path):
        self.path = str(path)
        # check_same_thread=False so the web server (which serves requests on
        # worker threads) can share one connection. A lock keeps writes safe.
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(SCHEMA)
            self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # --- low-level helpers -------------------------------------------------

    def _write(self, sql: str, params: tuple = ()) -> int:
        with self._lock:
            cur = self._conn.execute(sql, params)
            self._conn.commit()
            return cur.lastrowid

    def _rows(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(r) for r in self._conn.execute(sql, params).fetchall()]

    def _row(self, sql: str, params: tuple = ()) -> dict[str, Any] | None:
        rows = self._rows(sql, params)
        return rows[0] if rows else None

    # --- people ------------------------------------------------------------

    def upsert_person(self, name: str, role: str = "member", notes: str = "") -> int:
        """Add a person, or update their details if the name already exists."""
        existing = self._row("SELECT id FROM people WHERE name = ? COLLATE NOCASE", (name,))
        if existing:
            self._write(
                "UPDATE people SET role = ?, notes = ? WHERE id = ?",
                (role, notes, existing["id"]),
            )
            return existing["id"]
        return self._write(
            "INSERT INTO people (name, role, notes, created_at) VALUES (?, ?, ?, ?)",
            (name, role, notes, _now()),
        )

    def list_people(self) -> list[dict]:
        return self._rows("SELECT * FROM people ORDER BY name")

    def find_person(self, name: str | None) -> dict | None:
        if not name:
            return None
        return self._row("SELECT * FROM people WHERE name = ? COLLATE NOCASE", (name,))

    def _person_id(self, name: str | None) -> int | None:
        """Resolve a name to an id, creating the person if they're new."""
        if not name:
            return None
        person = self.find_person(name)
        return person["id"] if person else self.upsert_person(name)

    # --- tasks -------------------------------------------------------------

    def add_task(
        self,
        title: str,
        assignee: str | None = None,
        due: str | None = None,
        priority: str = "normal",
        notes: str = "",
        created_by: str | None = None,
    ) -> dict:
        task_id = self._write(
            """INSERT INTO tasks (title, person_id, due, priority, notes, created_by, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, self._person_id(assignee), due, priority, notes, created_by, _now()),
        )
        return self.get_task(task_id)

    def get_task(self, task_id: int) -> dict | None:
        return self._row(
            """SELECT t.*, p.name AS assignee FROM tasks t
               LEFT JOIN people p ON p.id = t.person_id WHERE t.id = ?""",
            (task_id,),
        )

    def list_tasks(
        self,
        assignee: str | None = None,
        status: str = "open",
        due_on_or_before: str | None = None,
    ) -> list[dict]:
        sql = """SELECT t.*, p.name AS assignee FROM tasks t
                 LEFT JOIN people p ON p.id = t.person_id WHERE 1=1"""
        params: list[Any] = []
        if status and status != "all":
            sql += " AND t.status = ?"
            params.append(status)
        if assignee:
            sql += " AND p.name = ? COLLATE NOCASE"
            params.append(assignee)
        if due_on_or_before:
            sql += " AND t.due IS NOT NULL AND t.due <= ?"
            params.append(due_on_or_before)
        sql += " ORDER BY t.due IS NULL, t.due, t.id"
        return self._rows(sql, tuple(params))

    def complete_task(self, task_id: int) -> dict | None:
        if not self.get_task(task_id):
            return None
        self._write(
            "UPDATE tasks SET status = 'done', done_at = ? WHERE id = ?", (_now(), task_id)
        )
        return self.get_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        if not self.get_task(task_id):
            return False
        self._write("DELETE FROM tasks WHERE id = ?", (task_id,))
        return True

    # --- chores ------------------------------------------------------------

    def add_chore(self, title: str, assignee: str | None = None, recurrence: str = "daily") -> dict:
        chore_id = self._write(
            """INSERT INTO chores (title, person_id, recurrence, created_at)
               VALUES (?, ?, ?, ?)""",
            (title, self._person_id(assignee), recurrence, _now()),
        )
        return self.get_chore(chore_id)

    def get_chore(self, chore_id: int) -> dict | None:
        return self._row(
            """SELECT c.*, p.name AS assignee FROM chores c
               LEFT JOIN people p ON p.id = c.person_id WHERE c.id = ?""",
            (chore_id,),
        )

    def list_chores(self) -> list[dict]:
        return self._rows(
            """SELECT c.*, p.name AS assignee FROM chores c
               LEFT JOIN people p ON p.id = c.person_id ORDER BY c.id"""
        )

    def chore_done(self, chore_id: int, by: str | None = None) -> dict | None:
        if not self.get_chore(chore_id):
            return None
        self._write(
            "UPDATE chores SET last_done_at = ?, last_done_by = ? WHERE id = ?",
            (_now(), by, chore_id),
        )
        return self.get_chore(chore_id)

    # --- shopping ----------------------------------------------------------

    def add_shopping(self, item: str, qty: str = "", added_by: str | None = None) -> dict:
        item_id = self._write(
            "INSERT INTO shopping (item, qty, added_by, created_at) VALUES (?, ?, ?, ?)",
            (item, qty, added_by, _now()),
        )
        return self._row("SELECT * FROM shopping WHERE id = ?", (item_id,))

    def list_shopping(self, status: str = "needed") -> list[dict]:
        if status == "all":
            return self._rows("SELECT * FROM shopping ORDER BY id")
        return self._rows("SELECT * FROM shopping WHERE status = ? ORDER BY id", (status,))

    def mark_bought(self, item: str) -> dict | None:
        row = self._row(
            "SELECT * FROM shopping WHERE item = ? COLLATE NOCASE AND status = 'needed'",
            (item,),
        )
        if not row:
            return None
        self._write(
            "UPDATE shopping SET status = 'bought', bought_at = ? WHERE id = ?",
            (_now(), row["id"]),
        )
        return self._row("SELECT * FROM shopping WHERE id = ?", (row["id"],))

    # --- facts the bot should remember -------------------------------------

    def remember(self, text: str, about: str | None = None) -> dict:
        fact_id = self._write(
            "INSERT INTO facts (person_id, text, created_at) VALUES (?, ?, ?)",
            (self._person_id(about), text, _now()),
        )
        return self._row("SELECT * FROM facts WHERE id = ?", (fact_id,))

    def recall(self, about: str | None = None) -> list[dict]:
        sql = """SELECT f.*, p.name AS about FROM facts f
                 LEFT JOIN people p ON p.id = f.person_id"""
        if about:
            return self._rows(sql + " WHERE p.name = ? COLLATE NOCASE ORDER BY f.id", (about,))
        return self._rows(sql + " ORDER BY f.id")

    # --- conversation log --------------------------------------------------

    def log_message(self, role: str, text: str, speaker: str | None = None) -> None:
        self._write(
            "INSERT INTO messages (speaker, role, text, created_at) VALUES (?, ?, ?, ?)",
            (speaker, role, text, _now()),
        )

    def recent_messages(self, limit: int = 20) -> list[dict]:
        rows = self._rows("SELECT * FROM messages ORDER BY id DESC LIMIT ?", (limit,))
        return list(reversed(rows))

    # --- a compact snapshot for the bot's system prompt --------------------

    def briefing(self) -> str:
        """A short text summary of household state, for the model to read."""
        today = date.today().isoformat()
        lines: list[str] = []

        open_tasks = self.list_tasks(status="open")
        if open_tasks:
            lines.append("Open tasks:")
            for t in open_tasks[:25]:
                who = t["assignee"] or "unassigned"
                due = f", due {t['due']}" if t["due"] else ""
                overdue = " (OVERDUE)" if t["due"] and t["due"] < today else ""
                lines.append(f"  #{t['id']} {t['title']} [{who}{due}]{overdue}")
        else:
            lines.append("Open tasks: none")

        chores = self.list_chores()
        if chores:
            lines.append("Chores:")
            for c in chores:
                who = c["assignee"] or "unassigned"
                last = c["last_done_at"][:10] if c["last_done_at"] else "never"
                lines.append(f"  #{c['id']} {c['title']} [{who}, {c['recurrence']}, last done {last}]")

        shopping = self.list_shopping()
        if shopping:
            items = ", ".join(f"{s['item']}{' ' + s['qty'] if s['qty'] else ''}" for s in shopping)
            lines.append(f"Shopping list: {items}")

        facts = self.recall()
        if facts:
            lines.append("Remembered:")
            for f in facts[-15:]:
                about = f"{f['about']}: " if f["about"] else ""
                lines.append(f"  {about}{f['text']}")

        return "\n".join(lines)
