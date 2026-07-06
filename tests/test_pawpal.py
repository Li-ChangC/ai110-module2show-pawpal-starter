from pathlib import Path
import sys


sys.path.append(str(Path(__file__).resolve().parents[1]))

from pawpal_system import Pet, Task


def test_task_completion_changes_status() -> None:
    task = Task(description="Morning walk", time="08:00")

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="cat")
    task = Task(description="Feed breakfast", time="07:30")

    assert len(pet.tasks) == 0

    pet.add_task(task)

    assert len(pet.tasks) == 1