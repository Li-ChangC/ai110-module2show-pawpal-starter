from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable
from uuid import uuid4


@dataclass
class Task:
    description: str
    time: str
    frequency: str = "once"
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid4()))

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks available to the scheduler."""
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> list[Task]:
        """Return only pending tasks available to the scheduler."""
        return self.owner.get_all_pending_tasks()

    def organize_tasks(self) -> list[Task]:
        """Sort pending tasks into a stable daily order."""
        def sort_key(task: Task) -> tuple[str, str, str]:
            return (task.time, task.frequency.lower(), task.description.lower())

        return sorted(self.get_pending_tasks(), key=sort_key)

    def generate_daily_plan(self) -> list[str]:
        """Build a readable schedule for today's tasks."""
        plan: list[str] = []
        for task in self.organize_tasks():
            plan.append(f"{task.time} - {task.description} ({task.frequency})")
        return plan

    def mark_task_complete(self, task_id: str) -> bool:
        """Mark a task complete by ID and return whether it was found."""
        for task in self.owner.get_all_tasks():
            if task.task_id == task_id:
                task.mark_complete()
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