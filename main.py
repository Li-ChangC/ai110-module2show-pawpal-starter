from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan")

    mochi = Pet(name="Mochi", species="cat", breed="Siamese")
    luna = Pet(name="Luna", species="dog", breed="Corgi")

    mochi.add_task(Task(description="Morning feeding", time="08:00", frequency="daily"))
    mochi.add_task(Task(description="Litter box cleanup", time="09:00", frequency="daily"))
    luna.add_task(Task(description="Evening walk", time="18:30", frequency="daily"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)

    print("Today's Schedule")
    print("----------------")
    for line in scheduler.generate_daily_plan():
        print(line)


if __name__ == "__main__":
    main()