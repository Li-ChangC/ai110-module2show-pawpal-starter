import streamlit as st
from datetime import date
from pathlib import Path

from pawpal_system import Owner, Pet, Scheduler, Task

DATA_FILE = Path(__file__).resolve().parent / "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json(DATA_FILE)

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.caption(f"Persistence file: {DATA_FILE.name} — changes are saved automatically.")

st.subheader("Adding a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed", value="")

if st.button("Add pet"):
    if any(existing_pet.name == pet_name for existing_pet in owner.get_pets()):
        st.info(f"{pet_name} is already in the session vault.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, breed=breed))
        owner.save_to_json(DATA_FILE)
        st.success(f"Added {pet_name} to the session vault.")

if owner.get_pets():
    st.write("Current pets:")
    st.table([
        {"name": pet.name, "species": pet.species, "breed": pet.breed}
        for pet in owner.get_pets()
    ])
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Scheduling a Task")
st.caption("Add tasks to a pet, then generate today's schedule from the owner vault.")

if owner.get_pets():
    selected_pet_name = st.selectbox("Choose a pet", [pet.name for pet in owner.get_pets()])
    selected_pet = next(pet for pet in owner.get_pets() if pet.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_description = st.text_input("Task description", value="Morning walk")
    with col2:
        task_time = st.text_input("Task time", value="08:00")
    with col3:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly", "monthly"])

    task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)

    if st.button("Add task"):
        selected_pet.add_task(
            Task(
                description=task_description,
                time=task_time,
                frequency=frequency,
                priority=task_priority,
            )
        )
        owner.save_to_json(DATA_FILE)
        st.success(f"Added a task for {selected_pet.name}.")

    if selected_pet.tasks:
        st.success(f"{selected_pet.name} currently has {len(selected_pet.tasks)} task(s).")
        st.table(
            [
                {
                    "icon": task.display_icon(),
                    "description": task.description,
                    "time": task.time,
                    "frequency": task.frequency,
                    "priority": task.priority,
                    "completed": task.completed,
                }
                for task in scheduler.sort_by_time(selected_pet.tasks)
            ]
        )
else:
    st.warning("Add a pet first to schedule tasks.")

st.divider()

st.subheader("Today's Schedule")
schedule_date = st.date_input(
    "View schedule for",
    value=st.session_state.get("schedule_date", date.today()),
)
st.session_state.schedule_date = schedule_date

conflict_warnings = scheduler.get_conflict_warnings()
if conflict_warnings:
    for warning in conflict_warnings:
        st.warning(warning)

scheduled_tasks = scheduler.get_scheduled_tasks_with_pet(schedule_date)

if scheduled_tasks:
    st.success(f"{len(scheduled_tasks)} task(s) are scheduled for {schedule_date}.")
    scheduled_lookup = {task.task_id: pet_name for pet_name, task in scheduled_tasks}
    sorted_scheduled_tasks = scheduler.sort_by_time([task for _, task in scheduled_tasks])
    st.table(
        [
            {
                "pet": scheduled_lookup[task.task_id],
                "icon": task.display_icon(),
                "time": task.time,
                "description": task.description,
                "frequency": task.frequency,
                "priority": task.priority,
            }
            for task in sorted_scheduled_tasks
        ]
    )
    st.markdown("**Readable plan**")
    for line in scheduler.generate_daily_plan(schedule_date):
        st.write(line)

    next_slot = scheduler.find_next_available_slot(schedule_date)
    if next_slot is not None:
        st.info(f"Next available 30-minute slot: {next_slot}")
else:
    st.info("No tasks are scheduled for the selected day yet.")

st.divider()

st.subheader("Filtered Tasks")
pet_filter_options = ["All pets"] + [pet.name for pet in owner.get_pets()]
selected_filter_pet = st.selectbox("Filter by pet", pet_filter_options)
completion_filter = st.selectbox("Filter by completion", ["All tasks", "Pending only", "Completed only"])

completed_filter_value: bool | None
if completion_filter == "Pending only":
    completed_filter_value = False
elif completion_filter == "Completed only":
    completed_filter_value = True
else:
    completed_filter_value = None

filtered_tasks = scheduler.filter_tasks(
    pet_name=None if selected_filter_pet == "All pets" else selected_filter_pet,
    completed=completed_filter_value,
)

if filtered_tasks:
    st.table(
        [
            {
                "icon": task.display_icon(),
                "description": task.description,
                "time": task.time,
                "frequency": task.frequency,
                "priority": task.priority,
                "completed": task.completed,
            }
            for task in scheduler.sort_by_time(filtered_tasks)
        ]
    )
else:
    st.info("No tasks match the selected filters.")
