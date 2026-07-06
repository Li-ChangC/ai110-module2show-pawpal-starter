from pathlib import Path
import sys
from datetime import date, timedelta


sys.path.append(str(Path(__file__).resolve().parents[1]))

from pawpal_system import Pet, Task
from pawpal_system import Owner, Scheduler


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


def test_scheduler_sorts_tasks_by_parsed_time() -> None:
    owner = Owner("Jordan")
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(description="Late task", time="18:30"))
    pet.add_task(Task(description="Noon task", time="12:00 PM"))
    pet.add_task(Task(description="Early task", time="08:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.sort_by_time()

    assert [task.description for task in sorted_tasks] == [
        "Early task",
        "Noon task",
        "Late task",
    ]


def test_scheduler_filters_tasks_by_pet_and_completion() -> None:
    owner = Owner("Jordan")
    mochi = Pet(name="Mochi", species="cat")
    luna = Pet(name="Luna", species="dog")

    mochi_task = Task(description="Feed breakfast", time="07:30")
    luna_task = Task(description="Evening walk", time="18:30")
    luna_task.mark_complete()

    mochi.add_task(mochi_task)
    luna.add_task(luna_task)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks(pet_name="Mochi") == [mochi_task]
    assert scheduler.filter_tasks(completed=True) == [luna_task]
    assert scheduler.filter_tasks(pet_name="Luna", completed=False) == []


def test_scheduler_detects_conflicting_times() -> None:
    owner = Owner("Jordan")
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(description="Feeding", time="08:00"))
    pet.add_task(Task(description="Medication", time="08:00"))
    pet.add_task(Task(description="Walk", time="09:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert [task.description for task in conflicts[0]] == ["Feeding", "Medication"]


def test_scheduler_returns_conflict_warnings() -> None:
    owner = Owner("Jordan")
    mochi = Pet(name="Mochi", species="cat")
    luna = Pet(name="Luna", species="dog")

    mochi.add_task(Task(description="Feeding", time="08:00"))
    luna.add_task(Task(description="Walk", time="08:00"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)

    warnings = scheduler.get_conflict_warnings()

    assert warnings == [
        "Warning: 08:00 has 2 overlapping tasks for Luna, Mochi: Feeding, Walk"
    ]


def test_task_occurs_on_every_n_days_schedule() -> None:
    task = Task(
        description="Flea treatment",
        time="10:00",
        start_date=date(2026, 7, 1),
        repeat_every_days=3,
    )

    assert task.occurs_on(date(2026, 7, 4)) is True
    assert task.occurs_on(date(2026, 7, 5)) is False


def test_task_occurs_on_monthly_schedule() -> None:
    task = Task(
        description="Nail trim",
        time="11:00",
        frequency="monthly",
        start_date=date(2026, 7, 1),
        days_of_month=(6, 20),
    )

    assert task.occurs_on(date(2026, 7, 6)) is True
    assert task.occurs_on(date(2026, 7, 20)) is True
    assert task.occurs_on(date(2026, 7, 7)) is False


def test_daily_plan_includes_pet_name() -> None:
    owner = Owner("Jordan")
    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(
        Task(
            description="Grooming brush",
            time="07:30",
            frequency="weekly",
            start_date=date(2026, 7, 6),
        )
    )
    owner.add_pet(mochi)

    scheduler = Scheduler(owner)

    assert scheduler.generate_daily_plan(date(2026, 7, 6)) == [
        "07:30 - Mochi: Grooming brush"
    ]


def test_completing_recurring_task_creates_next_occurrence() -> None:
    owner = Owner("Jordan")
    pet = Pet(name="Mochi", species="cat")
    recurring_task = Task(
        description="Morning feeding",
        time="08:00",
        frequency="daily",
        start_date=date(2026, 7, 6),
    )
    one_off_task = Task(
        description="Vet visit",
        time="10:00",
        frequency="once",
        start_date=date(2026, 7, 6),
    )

    pet.add_task(recurring_task)
    pet.add_task(one_off_task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)

    assert scheduler.mark_task_complete(recurring_task.task_id) is True
    assert recurring_task.completed is True
    assert len(pet.tasks) == 3

    next_occurrence = pet.tasks[-1]

    assert next_occurrence.description == recurring_task.description
    assert next_occurrence.time == recurring_task.time
    assert next_occurrence.frequency == recurring_task.frequency
    assert next_occurrence.start_date == recurring_task.start_date + timedelta(days=1)
    assert next_occurrence.completed is False
    assert next_occurrence.task_id != recurring_task.task_id

    assert scheduler.mark_task_complete(one_off_task.task_id) is True
    assert len(pet.tasks) == 3


def test_daily_task_completion_creates_next_day_occurrence() -> None:
    owner = Owner("Jordan")
    pet = Pet(name="Mochi", species="cat")
    recurring_task = Task(
        description="Daily feeding",
        time="08:00",
        frequency="daily",
        start_date=date(2026, 7, 6),
    )

    pet.add_task(recurring_task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)

    assert scheduler.mark_task_complete(recurring_task.task_id) is True

    next_occurrence = pet.tasks[-1]

    assert next_occurrence.start_date == date(2026, 7, 7)
    assert next_occurrence.frequency == "daily"
    assert next_occurrence.completed is False


def test_scheduler_flags_duplicate_times() -> None:
    owner = Owner("Jordan")
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(description="Breakfast", time="08:00"))
    pet.add_task(Task(description="Medication", time="08:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert [task.description for task in conflicts[0]] == ["Breakfast", "Medication"]