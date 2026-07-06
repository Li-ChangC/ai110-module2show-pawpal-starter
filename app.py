import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

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
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Adding a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed", value="")

if st.button("Add pet"):
    if any(existing_pet.name == pet_name for existing_pet in owner.get_pets()):
        st.info(f"{pet_name} is already in the session vault.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, breed=breed))
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
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        selected_pet.add_task(
            Task(
                description=task_description,
                time=task_time,
                frequency=frequency,
            )
        )
        st.success(f"Added a task for {selected_pet.name}.")

    if selected_pet.tasks:
        st.write(f"Tasks for {selected_pet.name}:")
        st.table(
            [
                {
                    "description": task.description,
                    "time": task.time,
                    "frequency": task.frequency,
                    "completed": task.completed,
                }
                for task in selected_pet.tasks
            ]
        )
else:
    st.warning("Add a pet first to schedule tasks.")

st.divider()

st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    today_schedule = scheduler.generate_daily_plan()

    if today_schedule:
        for line in today_schedule:
            st.write(line)
    else:
        st.info("No tasks are scheduled yet.")
