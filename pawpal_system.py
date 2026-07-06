from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Iterable
from uuid import uuid4


@dataclass
class Task:
    description: str
    time: str
    frequency: str = "once"
    start_date: date = field(default_factory=date.today)
    repeat_every_days: int | None = None
    days_of_week: tuple[int, ...] | None = None
    days_of_month: tuple[int, ...] | None = None
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid4()))

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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
        """Sort tasks by time, then by frequency and description for stability."""

        tasks_to_sort = list(tasks if tasks is not None else self.get_pending_tasks())

        def sort_key(task: Task) -> tuple[datetime, str, str]:
            return (
                self._parse_time(task.time),
                task.frequency.lower(),
                task.description.lower(),
            )

        return sorted(tasks_to_sort, key=sort_key)

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
            f"{task.time} - {pet_lookup[task.task_id]}: {task.description}"
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