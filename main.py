"""CLI demo for PawPal+.

Verifies the backend logic in `pawpal_system.py` from the terminal: it loads (or
seeds) an owner from `data.json`, then prints priority-ordered schedules, conflict
warnings, the next available slot, and a recurrence demo using tabulate tables with
colored-emoji priority/status badges.
"""

from datetime import date
from pathlib import Path

from pawpal_system import Owner, Pet, Scheduler, Task

try:
    from tabulate import tabulate

    HAS_TABULATE = True
except ImportError:  # pragma: no cover - tabulate is a declared dependency
    HAS_TABULATE = False


DATA_FILE = Path(__file__).resolve().parent / "data.json"

PRIORITY_BADGES = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def priority_badge(priority: str) -> str:
    """Return a color-coded emoji badge for a task priority."""
    return PRIORITY_BADGES.get(priority.lower(), f"⚪ {priority.title()}")


def status_badge(completed: bool) -> str:
    """Return a color-coded emoji badge for completion status."""
    return "✅ Done" if completed else "⏳ Pending"


def render_table(rows: list[list[str]], headers: list[str]) -> str:
    """Render rows as a boxed table, falling back to plain text without tabulate."""
    if HAS_TABULATE:
        return tabulate(rows, headers=headers, tablefmt="rounded_grid")

    widths = [max(len(str(cell)) for cell in column) for column in zip(headers, *rows)]
    lines = ["  ".join(str(value).ljust(width) for value, width in zip(headers, widths))]
    lines.append("  ".join("-" * width for width in widths))
    for row in rows:
        lines.append("  ".join(str(value).ljust(width) for value, width in zip(row, widths)))
    return "\n".join(lines)


def section(title: str) -> None:
    """Print a labeled section header."""
    print(f"\n{title}")
    print("=" * len(title))


def seed_owner() -> Owner:
    """Build a demo owner with two pets and a spread of prioritized tasks."""
    owner = Owner("Jordan")

    mochi = Pet(name="Mochi", species="cat", breed="Siamese")
    luna = Pet(name="Luna", species="dog", breed="Corgi")

    mochi.add_task(Task(description="Litter box cleanup", time="09:00", frequency="daily", priority="low"))
    mochi.add_task(Task(description="Morning feeding", time="08:00", frequency="daily", priority="high"))
    mochi.add_task(Task(description="Medication", time="08:00", frequency="daily", priority="high"))
    mochi.add_task(Task(description="Flea treatment", time="10:00", repeat_every_days=3, priority="medium"))
    mochi.add_task(
        Task(description="Nail trim", time="11:00", frequency="monthly", days_of_month=(6, 20), priority="low")
    )
    luna.add_task(Task(description="Evening walk", time="18:30", frequency="daily", priority="medium"))
    luna.add_task(Task(description="Grooming brush", time="07:30", frequency="weekly", priority="high"))

    owner.add_pet(mochi)
    owner.add_pet(luna)
    return owner


def main() -> None:
    # Challenge 2: load persisted data; seed and save on first run.
    owner = Owner.load_from_json(DATA_FILE)
    if not owner.get_pets():
        owner = seed_owner()
        owner.save_to_json(DATA_FILE)
        print(f"Seeded a new owner and saved it to {DATA_FILE.name}.")
    else:
        print(f"Loaded existing owner from {DATA_FILE.name}.")

    scheduler = Scheduler(owner)
    today = date.today()

    # Challenge 3 + 4: priority-first schedule rendered as a colored table.
    section("🐾 Today's Schedule (priority, then time)")
    scheduled = scheduler.get_scheduled_tasks_with_pet(today)
    pet_lookup = {task.task_id: pet_name for pet_name, task in scheduled}
    ordered = scheduler.sort_by_time([task for _, task in scheduled])
    rows = [
        [
            task.display_icon(),
            task.time,
            pet_lookup[task.task_id],
            task.description,
            priority_badge(task.priority),
            task.frequency,
            status_badge(task.completed),
        ]
        for task in ordered
    ]
    print(render_table(rows, ["", "Time", "Pet", "Task", "Priority", "Freq", "Status"]))
    print(
        "Note: high-priority tasks lead the list even when a lower-priority task is "
        "earlier in the day."
    )

    # Challenge 4: readable one-line plan with emojis + priority markers.
    section("📋 Readable plan")
    for line in scheduler.generate_daily_plan(today):
        print(line)

    # Challenge 4: same-time conflict warnings.
    section("⚠️  Time conflicts")
    warnings = scheduler.get_conflict_warnings()
    print("\n".join(warnings) if warnings else "No conflicts found.")

    # Challenge 1: advanced capability — next open slot on the schedule.
    section("🕒 Next available slot")
    next_slot = scheduler.find_next_available_slot(today, start_time="08:00")
    print(
        f"Searching from 08:00 (which is taken), the next open slot is: {next_slot}"
        if next_slot is not None
        else "No open slot found in the working window."
    )

    # Challenge 3 + recurrence: demonstrate on an in-memory copy so data.json stays stable.
    section("🔁 Recurrence demo (in-memory, not persisted)")
    demo_owner = Owner.from_dict(owner.to_dict())
    demo_scheduler = Scheduler(demo_owner)
    daily_task = next(
        (task for task in demo_owner.get_all_tasks() if task.frequency == "daily"), None
    )
    if daily_task is not None:
        ids_before = {task.task_id for task in demo_owner.get_all_tasks()}
        demo_scheduler.mark_task_complete(daily_task.task_id)
        new_tasks = [task for task in demo_owner.get_all_tasks() if task.task_id not in ids_before]
        follow_up = new_tasks[0]
        print(
            f"Completed '{daily_task.description}' ({daily_task.start_date}); "
            f"task count {len(ids_before)} -> {len(demo_owner.get_all_tasks())}. "
            f"Next occurrence auto-created for {follow_up.start_date}."
        )


if __name__ == "__main__":
    main()
