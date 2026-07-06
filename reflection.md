# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
My initial design used four main classes: `PetInfo`, `TaskInfo`, `PetCareTasks`, and `Schedule`.

`PetInfo` stores the pet's basic profile, including species, name, gender, date of birth, breed, and any health issues. Its job is to represent the pet the app is planning for and to provide helper methods like calculating age or summarizing care needs.

`TaskInfo` represents one care task, such as feeding, a walk, grooming, or medication. It stores the task type, description, duration, priority, preferred time, and user preferences so the scheduler can decide when and whether to place it in the plan.

`PetCareTasks` manages the collection of tasks for a pet. It gives the app a place to add, remove, and retrieve tasks before scheduling begins.

`Schedule` represents the daily plan. It keeps the scheduled tasks, available time slots, and constraints, and it is responsible for checking whether a task can fit into the schedule.

This design keeps the model simple for a single-user offline app while separating pet data, task data, task storage, and schedule generation into clear responsibilities.


**b. Design changes**

Yes, the design changed slightly during implementation.

I removed owner-specific data from the model because this app is meant for one local user, so a separate owner class was not necessary. That kept the design simpler and focused the app on pet care planning only.

I also changed the task preference wording from owner-specific preferences to generic preferences. That makes the model easier to reuse for scheduling without assuming multiple users or accounts.

Finally, I used Python dataclasses for the main data objects in the backend skeleton because they keep the model code clean and make the attributes easy to define and read.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler currently considers task time, recurrence rules, completion status, and the pet the task belongs to. I also added task priority so the output can communicate importance clearly, even though the core sort order is still driven by time.

I treated time as the most important constraint because the app is first and foremost a daily scheduler. After that, I prioritized recurrence rules and completion status so the schedule only shows tasks that actually belong on a given day. Priority is useful for display and future planning, but it does not override time ordering in the current implementation.

**b. Tradeoffs**

- The scheduler checks for exact time matches when finding conflicts instead of comparing overlapping durations.
- That tradeoff is reasonable for this project because it keeps the logic simple and easy to explain, while still catching the most common pet-care collisions like two tasks both set for 08:00.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI as a design and implementation assistant in three main ways: to compare my UML draft against the final backend code, to suggest test cases for tricky scheduling behavior, and to help rewrite the README and reflection text so they matched the finished project.

The most helpful prompts were specific and anchored to real files, such as asking what should change in `pawpal_system.py`, which edge cases matter for recurring tasks, and how the Streamlit UI should show sorted and filtered schedules. That kept the assistant focused on the actual system rather than generic scheduling advice.

**b. Judgment and verification**

One suggestion I rejected was keeping the original UML classes (`PetInfo`, `TaskInfo`, `PetCareTasks`, and `Schedule`) as the primary design. I modified that idea because the final code centered on `Task`, `Pet`, `Owner`, and `Scheduler`, and I wanted the diagram to match the real implementation instead of the first draft.

I verified the AI's suggestions by checking the source files directly, running the tests, and comparing the behavior of the app output against the README examples. If a suggestion did not match the code path I actually implemented, I simplified it or rewrote it.

**c. Separate chat sessions**

Using a separate chat session for each phase kept the assistant's context focused and prevented earlier decisions from bleeding into unrelated work. For example, I kept algorithmic planning (sorting, recurrence, conflict detection) in its own session from core implementation, and testing in yet another. That meant each conversation stayed anchored to the files and goals that mattered for that phase, so the AI's suggestions were more relevant, easier to review, and less likely to reintroduce ideas I had already rejected. It also made it easier to trace which prompts produced which changes when I went back to verify them.

---

## 4. Testing and Verification

**a. What you tested**

I tested task completion, task sorting, filtering by pet and completion status, conflict detection, recurring task scheduling, and daily plan generation. I also checked that recurring tasks create a new next occurrence and that priority is preserved in the output.

These tests were important because they cover the core behaviors the scheduler is supposed to guarantee. Without them, it would be easy for the app to look correct in the UI while still producing the wrong schedule logic underneath.

**b. Confidence**

I am fairly confident that the scheduler works correctly for the behaviors this project currently supports, especially because the full test suite passes and the main workflow is covered end to end.

If I had more time, I would test invalid time formats, leap-year monthly recurrence, month-end rollover, overlapping duration-based conflicts, and larger multi-pet schedules with many recurring tasks.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the way the scheduler now produces readable daily plans while still handling recurring tasks, conflict warnings, and task filtering. The app feels much closer to a real planning tool instead of just a list of tasks.

**b. What you would improve**

In a later iteration, I would add richer priority-based scheduling rules, duration-aware conflict detection, and a more polished UI for editing or removing tasks. I would also separate the model even more cleanly from the display layer so the scheduling logic could be reused outside Streamlit.

**c. Key takeaway**

My biggest takeaway is that working with powerful AI is most effective when I stay in the role of lead architect. I got the best results when I set the structure, checked the implementation against the code, and used AI to accelerate specific decisions instead of letting it define the system for me.
