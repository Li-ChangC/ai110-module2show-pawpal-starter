from __future__ import annotations

import calendar
import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable
from uuid import uuid4


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
TASK_EMOJIS = {
    "feeding": "🍽️",
    "feed": "🍽️",
    "walk": "🐕",
    "medication": "💊",
    "med": "💊",
    "groom": "✂️",
    "brush": "🪮",
    "litter": "🧹",
    "flea": "🪲",
    "play": "🎾",
}


@dataclass
class Task:
    description: str
    time: str
    frequency: str = "once"
    priority: str = "normal"
    start_date: date = field(default_factory=date.today)
    repeat_every_days: int | None = None
    days_of_week: tuple[int, ...] | None = None
    days_of_month: tuple[int, ...] | None = None
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self.frequency = self.frequency.strip().lower()
        self.priority = self.priority.strip().lower()

        if self.priority == "normal":
            self.priority = "medium"

        if self.priority not in PRIORITY_ORDER:
            self.priority = "medium"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return a numeric ranking for priority-based sorting."""
        return PRIORITY_ORDER.get(self.priority, PRIORITY_ORDER["medium"])

    def display_icon(self) -> str:
        """Return a small emoji that matches the task description."""
        description = self.description.lower()

        for keyword, emoji in TASK_EMOJIS.items():
            if keyword in description:
                return emoji

        return "🐾"

    def is_recurring(self) -> bool:
        """Return whether this task should repeat."""
        return (
            self.frequency.lower() in {"daily", "weekly", "monthly"}
            or self.repeat_every_days is not None
            or self.days_of_week is not None
            or self.days_of_month is not None
        )

    def _add_months(self, source_date: date, months: int) -> date:
        """Shift a date forward by whole months while preserving the day when possible."""
        month_index = source_date.month - 1 + months
        year = source_date.year + month_index // 12
        month = month_index % 12 + 1
        last_day = calendar.monthrange(year, month)[1]
        day = min(source_date.day, last_day)
        return date(year, month, day)

    def next_occurrence_date(self) -> date:
        """Calculate the next calendar date on which this recurring task should appear."""
        if self.repeat_every_days is not None:
            return self.start_date + timedelta(days=self.repeat_every_days)

        frequency = self.frequency.lower()

        if frequency == "daily":
            return self.start_date + timedelta(days=1)

        if frequency == "weekly":
            return self.start_date + timedelta(days=7)

        if frequency == "monthly":
            return self._add_months(self.start_date, 1)

        return self.start_date + timedelta(days=1)

    def occurs_on(self, target_date: date) -> bool:
        """Check whether this task belongs on a specific date based on its recurrence rule."""
        if target_date < self.start_date:
            return False

        if self.repeat_every_days is not None:
            return (target_date - self.start_date).days % self.repeat_every_days == 0

        frequency = self.frequency.lower()

        if frequency == "once":
            return target_date == self.start_date

        if frequency == "daily":
            return True

        if frequency == "weekly":
            if self.days_of_week is None:
                return (target_date - self.start_date).days % 7 == 0

            return target_date.weekday() in self.days_of_week

        if frequency == "monthly":
            if self.days_of_month is None:
                return target_date.day == self.start_date.day

            return target_date.day in self.days_of_month

        return target_date == self.start_date

    def create_next_occurrence(self) -> Task:
        """Clone this task into the next scheduled instance using the computed next date."""
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            priority=self.priority,
            start_date=self.next_occurrence_date(),
            repeat_every_days=self.repeat_every_days,
            days_of_week=self.days_of_week,
            days_of_month=self.days_of_month,
        )

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def update_time(self, new_time: str) -> None:
        """Update the task's scheduled time."""
        self.time = new_time

    def to_dict(self) -> dict:
        """Convert this task into a JSON-safe dictionary."""
        return {
            "description": self.description,
            "time": self.time,
            "frequency": self.frequency,
            "priority": self.priority,
            "start_date": self.start_date.isoformat(),
            "repeat_every_days": self.repeat_every_days,
            "days_of_week": list(self.days_of_week) if self.days_of_week is not None else None,
            "days_of_month": list(self.days_of_month) if self.days_of_month is not None else None,
            "completed": self.completed,
            "task_id": self.task_id,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> Task:
        """Build a task from a persisted dictionary payload."""
        start_date_value = payload.get("start_date")
        if start_date_value:
            start_date = date.fromisoformat(start_date_value)
        else:
            start_date = date.today()

        days_of_week = payload.get("days_of_week")
        if days_of_week is not None:
            days_of_week = tuple(days_of_week)

        days_of_month = payload.get("days_of_month")
        if days_of_month is not None:
            days_of_month = tuple(days_of_month)

        return cls(
            description=payload.get("description", ""),
            time=payload.get("time", "00:00"),
            frequency=payload.get("frequency", "once"),
            priority=payload.get("priority", "medium"),
            start_date=start_date,
            repeat_every_days=payload.get("repeat_every_days"),
            days_of_week=days_of_week,
            days_of_month=days_of_month,
            completed=payload.get("completed", False),
            task_id=payload.get("task_id", str(uuid4())),
        )


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    birth_date: date | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID and return whether anything changed."""
        before_count = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        return len(self.tasks) != before_count

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return list(self.tasks)

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]

    def get_completed_tasks(self) -> list[Task]:
        """Return only tasks that are completed."""
        return [task for task in self.tasks if task.completed]

    def to_dict(self) -> dict:
        """Convert this pet into a JSON-safe dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "birth_date": self.birth_date.isoformat() if self.birth_date is not None else None,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, payload: dict) -> Pet:
        """Build a pet from a persisted dictionary payload."""
        birth_date_value = payload.get("birth_date")
        birth_date = date.fromisoformat(birth_date_value) if birth_date_value else None

        pet = cls(
            name=payload.get("name", "Unnamed Pet"),
            species=payload.get("species", "other"),
            breed=payload.get("breed", ""),
            birth_date=birth_date,
        )
        pet.tasks = [Task.from_dict(task_payload) for task_payload in payload.get("tasks", [])]
        return pet


class Owner:
    def __init__(self, name: str = "Local User") -> None:
        """Create an owner who can manage one or more pets."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name and return whether anything changed."""
        before_count = len(self.pets)
        self.pets = [pet for pet in self.pets if pet.name != pet_name]
        return len(self.pets) != before_count

    def get_pets(self) -> list[Pet]:
        """Return all pets owned by this owner."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def get_all_pending_tasks(self) -> list[Task]:
        """Return every incomplete task from every pet."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_pending_tasks())
        return tasks

    def to_dict(self) -> dict:
        """Convert the owner, pets, and tasks into JSON-safe data."""
        return {"name": self.name, "pets": [pet.to_dict() for pet in self.pets]}

    @classmethod
    def from_dict(cls, payload: dict) -> Owner:
        """Build an owner from a persisted dictionary payload."""
        owner = cls(name=payload.get("name", "Local User"))
        owner.pets = [Pet.from_dict(pet_payload) for pet_payload in payload.get("pets", [])]
        return owner

    def save_to_json(self, file_path: str | Path = "data.json") -> None:
        """Persist this owner and all nested pets/tasks to disk."""
        path = Path(file_path)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(cls, file_path: str | Path = "data.json") -> Owner:
        """Load an owner from disk, returning an empty owner if the file does not exist."""
        path = Path(file_path)

        if not path.exists():
            return cls()

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return cls()

        return cls.from_dict(payload)


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that works from one owner's pets."""
        self.owner = owner

    def _parse_time(self, task_time: str) -> datetime:
        """Convert a task time string into a sortable datetime value."""
        for format_string in ("%H:%M", "%I:%M %p"):
            try:
                return datetime.strptime(task_time.strip(), format_string)
            except ValueError:
                continue

        return datetime.max

    def _iter_tasks_with_pet(self) -> Iterable[tuple[str, Task]]:
        """Yield each task alongside the pet it belongs to."""
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                yield pet.name, task

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks available to the scheduler."""
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> list[Task]:
        """Return only pending tasks available to the scheduler."""
        return self.owner.get_all_pending_tasks()

    def get_scheduled_tasks(self, plan_date: date | None = None) -> list[Task]:
        """Return pending tasks that should appear on a given date."""
        current_date = plan_date or date.today()
        return [task for task in self.get_pending_tasks() if task.occurs_on(current_date)]

    def get_scheduled_tasks_with_pet(
        self, plan_date: date | None = None
    ) -> list[tuple[str, Task]]:
        """Return all scheduled tasks for a date together with the pet name they belong to."""
        current_date = plan_date or date.today()
        scheduled_tasks: list[tuple[str, Task]] = []

        for pet_name, task in self._iter_tasks_with_pet():
            if task.completed:
                continue

            if task.occurs_on(current_date):
                scheduled_tasks.append((pet_name, task))

        return scheduled_tasks

    def sort_by_time(self, tasks: Iterable[Task] | None = None) -> list[Task]:
        """Sort tasks by priority first, then by time, then by frequency and description."""

        tasks_to_sort = list(tasks if tasks is not None else self.get_pending_tasks())

        def sort_key(task: Task) -> tuple[int, datetime, str, str]:
            return (
                task.priority_rank(),
                self._parse_time(task.time),
                task.frequency.lower(),
                task.description.lower(),
            )

        return sorted(tasks_to_sort, key=sort_key)

    def find_next_available_slot(
        self,
        plan_date: date | None = None,
        start_time: str = "06:00",
        end_time: str = "22:00",
        step_minutes: int = 30,
    ) -> str | None:
        """Return the first open time slot for a date using fixed time increments."""
        current_date = plan_date or date.today()
        occupied_times = {
            task.time.strip() for _, task in self.get_scheduled_tasks_with_pet(current_date)
        }

        try:
            current_slot = datetime.strptime(start_time, "%H:%M")
            last_slot = datetime.strptime(end_time, "%H:%M")
        except ValueError:
            return None

        while current_slot <= last_slot:
            slot_text = current_slot.strftime("%H:%M")
            if slot_text not in occupied_times:
                return slot_text
            current_slot += timedelta(minutes=step_minutes)

        return None

    def format_task_line(self, pet_name: str, task: Task) -> str:
        """Return a readable CLI line with an emoji and priority marker."""
        return f"{task.display_icon()} {task.time} - {pet_name}: {task.description} [priority: {task.priority}]"

    def organize_tasks(self) -> list[Task]:
        """Sort pending tasks into a stable daily order."""
        return self.sort_by_time()

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Filter tasks by pet name and/or completion status."""
        filtered_tasks: list[Task] = []

        for current_pet_name, task in self._iter_tasks_with_pet():
            if pet_name is not None and current_pet_name != pet_name:
                continue

            if completed is not None and task.completed != completed:
                continue

            filtered_tasks.append(task)

        return filtered_tasks

    def get_recurring_tasks(self) -> list[Task]:
        """Return tasks that repeat on a daily or weekly cadence."""
        return [task for task in self.get_all_tasks() if task.is_recurring() and not task.completed]

    def detect_conflicts(self) -> list[list[Task]]:
        """Group tasks that share the same time."""
        grouped_tasks: dict[str, list[Task]] = {}

        for task in self.get_pending_tasks():
            normalized_time = task.time.strip()
            grouped_tasks.setdefault(normalized_time, []).append(task)

        return [tasks for tasks in grouped_tasks.values() if len(tasks) > 1]

    def get_conflict_warnings(self) -> list[str]:
        """Build readable warnings for any same-time scheduled tasks that overlap."""
        grouped_tasks: dict[str, list[tuple[str, Task]]] = {}

        for pet_name, task in self._iter_tasks_with_pet():
            if task.completed:
                continue

            if not task.occurs_on(date.today()):
                continue

            normalized_time = task.time.strip()
            grouped_tasks.setdefault(normalized_time, []).append((pet_name, task))

        warnings: list[str] = []

        for task_time in sorted(grouped_tasks, key=self._parse_time):
            overlapping_tasks = grouped_tasks[task_time]
            if len(overlapping_tasks) < 2:
                continue

            pet_names = sorted({pet_name for pet_name, _ in overlapping_tasks})
            descriptions = ", ".join(task.description for _, task in overlapping_tasks)
            pet_label = ", ".join(pet_names)
            warnings.append(
                f"Warning: {task_time} has {len(overlapping_tasks)} overlapping tasks "
                f"for {pet_label}: {descriptions}"
            )

        return warnings

    def generate_daily_plan(self, plan_date: date | None = None) -> list[str]:
        """Build a readable, pet-labeled schedule for the selected date."""
        scheduled_tasks_with_pet = self.get_scheduled_tasks_with_pet(plan_date)
        sorted_tasks = self.sort_by_time([task for _, task in scheduled_tasks_with_pet])

        pet_lookup = {task.task_id: pet_name for pet_name, task in scheduled_tasks_with_pet}

        return [
            self.format_task_line(pet_lookup[task.task_id], task)
            for task in sorted_tasks
        ]

    def mark_task_complete(self, task_id: str) -> bool:
        """Mark a task complete by ID and return whether it was found."""
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                if task.task_id == task_id:
                    if task.completed:
                        return True

                    task.mark_complete()

                    if task.is_recurring():
                        pet.add_task(task.create_next_occurrence())

                    return True
        return False

    def find_task(self, task_id: str) -> Task | None:
        """Find a task by ID and return it if it exists."""
        for task in self.owner.get_all_tasks():
            if task.task_id == task_id:
                return task
        return None


# Backward-compatible aliases for the earlier UML names.
TaskInfo = Task
PetInfo = Pet
PetCareTasks = Pet
Schedule = Scheduler