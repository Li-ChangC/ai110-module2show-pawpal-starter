from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan")

    mochi = Pet(name="Mochi", species="cat", breed="Siamese")
    luna = Pet(name="Luna", species="dog", breed="Corgi")

    mochi.add_task(Task(description="Litter box cleanup", time="09:00", frequency="daily"))
    mochi.add_task(Task(description="Morning feeding", time="08:00", frequency="daily"))
    mochi.add_task(Task(description="Medication", time="08:00", frequency="daily"))
    mochi.add_task(
        Task(description="Flea treatment", time="10:00", repeat_every_days=3)
    )
    mochi.add_task(
        Task(description="Nail trim", time="11:00", frequency="monthly", days_of_month=(6, 20))
    )
    luna.add_task(Task(description="Evening walk", time="18:30", frequency="daily"))
    luna.add_task(Task(description="Grooming brush", time="07:30", frequency="weekly"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)

    luna.tasks[0].mark_complete()

    print("Today's Schedule")
    print("----------------")
    for line in scheduler.generate_daily_plan():
        print(line)

    print("\nSorted by time")
    print("--------------")
    for task in scheduler.sort_by_time():
        print(f"{task.time} - {task.description} ({task.frequency})")

    print("\nPending tasks for Mochi")
    print("----------------------")
    mochi_tasks = scheduler.sort_by_time(
        scheduler.filter_tasks(pet_name="Mochi", completed=False)
    )
    for task in mochi_tasks:
        print(f"{task.time} - {task.description} ({task.frequency})")

    print("\nRecurring tasks")
    print("---------------")
    for task in scheduler.sort_by_time(scheduler.get_recurring_tasks()):
        print(f"{task.time} - {task.description} ({task.frequency})")

    print("\nTime conflicts")
    print("--------------")
    conflict_warnings = scheduler.get_conflict_warnings()
    if conflict_warnings:
        for warning in conflict_warnings:
            print(warning)
    else:
        print("No conflicts found.")


if __name__ == "__main__":
    main()