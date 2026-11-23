"""The bot's hands.

Each entry in TOOLS tells Claude about one action it can take. `dispatch` runs
the action against the Store. Keep the tool list stable and in a fixed order -
it is part of the cached prompt prefix, so reordering it costs money.
"""

from __future__ import annotations

import json
from typing import Any

from .store import Store

TOOLS: list[dict[str, Any]] = [
    {
        "name": "add_task",
        "description": (
            "Add a task for someone in the household. Use this whenever a person "
            "says they need to do something, or asks you to remind them of work. "
            "Dates must be YYYY-MM-DD."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short description of the task."},
                "assignee": {"type": "string", "description": "Name of the person responsible."},
                "due": {"type": "string", "description": "Due date as YYYY-MM-DD."},
                "priority": {"type": "string", "enum": ["low", "normal", "high"]},
                "notes": {"type": "string"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "list_tasks",
        "description": (
            "Look up tasks. Filter by person, by status, or by a due date cutoff. "
            "Use this before answering questions about what anyone has to do."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "assignee": {"type": "string"},
                "status": {"type": "string", "enum": ["open", "done", "all"]},
                "due_on_or_before": {"type": "string", "description": "YYYY-MM-DD."},
            },
        },
    },
    {
        "name": "complete_task",
        "description": "Mark a task finished. Needs the task's id number.",
        "input_schema": {
            "type": "object",
            "properties": {"task_id": {"type": "integer"}},
            "required": ["task_id"],
        },
    },
    {
        "name": "delete_task",
        "description": "Remove a task entirely, for when it was added by mistake.",
        "input_schema": {
            "type": "object",
            "properties": {"task_id": {"type": "integer"}},
            "required": ["task_id"],
        },
    },
    {
        "name": "add_chore",
        "description": (
            "Add a recurring household chore, such as washing dishes or watering plants. "
            "Use this instead of add_task when the job repeats."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "assignee": {"type": "string"},
                "recurrence": {
                    "type": "string",
                    "description": "How often, e.g. daily, weekly, every Sunday.",
                },
            },
            "required": ["title"],
        },
    },
    {
        "name": "list_chores",
        "description": "List all recurring chores, who owns each, and when it was last done.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "chore_done",
        "description": "Record that a chore was just done. Needs the chore's id number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chore_id": {"type": "integer"},
                "by": {"type": "string", "description": "Who did it."},
            },
            "required": ["chore_id"],
        },
    },
    {
        "name": "add_shopping",
        "description": "Add an item to the household shopping list.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item": {"type": "string"},
                "qty": {"type": "string", "description": "Amount, e.g. '2 kg', '1 packet'."},
            },
            "required": ["item"],
        },
    },
    {
        "name": "list_shopping",
        "description": "Read the shopping list.",
        "input_schema": {
            "type": "object",
            "properties": {"status": {"type": "string", "enum": ["needed", "bought", "all"]}},
        },
    },
    {
        "name": "mark_bought",
        "description": "Tick an item off the shopping list once it has been purchased.",
        "input_schema": {
            "type": "object",
            "properties": {"item": {"type": "string"}},
            "required": ["item"],
        },
    },
    {
        "name": "remember",
        "description": (
            "Save a lasting fact about the household or a person - preferences, "
            "allergies, schedules, sizes, birthdays. Use this when someone tells you "
            "something worth knowing next week, not just right now."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The fact, in one sentence."},
                "about": {"type": "string", "description": "Person it concerns, if any."},
            },
            "required": ["text"],
        },
    },
    {
        "name": "recall",
        "description": "Look up facts you saved earlier, optionally about one person.",
        "input_schema": {
            "type": "object",
            "properties": {"about": {"type": "string"}},
        },
    },
    {
        "name": "list_people",
        "description": "List everyone the household database knows about.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "add_person",
        "description": (
            "Register a new member of the household. Use when you meet someone "
            "whose name is not in the database yet."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "role": {"type": "string", "description": "e.g. adult, child, guest."},
                "notes": {"type": "string"},
            },
            "required": ["name"],
        },
    },
]


def dispatch(store: Store, name: str, args: dict[str, Any], speaker: str | None = None) -> str:
    """Run one tool call and return a JSON string for the model to read."""

    def ok(payload: Any) -> str:
        return json.dumps({"ok": True, "result": payload}, default=str)

    def err(message: str) -> str:
        return json.dumps({"ok": False, "error": message})

    try:
        if name == "add_task":
            task = store.add_task(
                title=args["title"],
                assignee=args.get("assignee") or speaker,
                due=args.get("due"),
                priority=args.get("priority", "normal"),
                notes=args.get("notes", ""),
                created_by=speaker,
            )
            return ok(task)

        if name == "list_tasks":
            return ok(
                store.list_tasks(
                    assignee=args.get("assignee"),
                    status=args.get("status", "open"),
                    due_on_or_before=args.get("due_on_or_before"),
                )
            )

        if name == "complete_task":
            task = store.complete_task(args["task_id"])
            return ok(task) if task else err(f"No task with id {args['task_id']}.")

        if name == "delete_task":
            deleted = store.delete_task(args["task_id"])
            return ok("deleted") if deleted else err(f"No task with id {args['task_id']}.")

        if name == "add_chore":
            return ok(
                store.add_chore(
                    title=args["title"],
                    assignee=args.get("assignee"),
                    recurrence=args.get("recurrence", "daily"),
                )
            )

        if name == "list_chores":
            return ok(store.list_chores())

        if name == "chore_done":
            chore = store.chore_done(args["chore_id"], by=args.get("by") or speaker)
            return ok(chore) if chore else err(f"No chore with id {args['chore_id']}.")

        if name == "add_shopping":
            return ok(
                store.add_shopping(
                    item=args["item"], qty=args.get("qty", ""), added_by=speaker
                )
            )

        if name == "list_shopping":
            return ok(store.list_shopping(status=args.get("status", "needed")))

        if name == "mark_bought":
            row = store.mark_bought(args["item"])
            return ok(row) if row else err(f"'{args['item']}' is not on the list.")

        if name == "remember":
            return ok(store.remember(text=args["text"], about=args.get("about")))

        if name == "recall":
            return ok(store.recall(about=args.get("about")))

        if name == "list_people":
            return ok(store.list_people())

        if name == "add_person":
            person_id = store.upsert_person(
                name=args["name"],
                role=args.get("role", "member"),
                notes=args.get("notes", ""),
            )
            return ok({"id": person_id, "name": args["name"]})

        return err(f"Unknown tool: {name}")

    except KeyError as e:
        return err(f"Missing required argument: {e}")
    except Exception as e:  # a tool crash should become a result, never kill the loop
        return err(f"{type(e).__name__}: {e}")
