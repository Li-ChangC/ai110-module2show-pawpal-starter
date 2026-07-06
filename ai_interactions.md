# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent (Claude Code) to implement the five stretch challenges on top of my working
core project: (1) an advanced algorithmic capability, (2) JSON data persistence, (3) priority-based
scheduling, (4) professional CLI output formatting, and (5) a multi-model prompt comparison. I asked
it to keep the existing class model intact, keep the test suite green, and document each feature in
the README.

**Which files were modified?**

- `pawpal_system.py` — added `priority_rank()` and priority-first sorting in `sort_by_time()`,
  `find_next_available_slot()` (advanced capability), `display_icon()`, and the
  `to_dict()` / `from_dict()` / `save_to_json()` / `load_from_json()` persistence layer.
- `main.py` — rewrote the CLI demo to load/seed `data.json`, render `tabulate` tables with
  color-coded `priority_badge()` / `status_badge()` output, and show a next-slot + recurrence demo.
- `app.py` — wired persistence into `st.session_state`, added a priority selector, and surfaced
  `display_icon()` and `find_next_available_slot()` in the UI.
- `tests/test_pawpal.py` — added tests for priority ordering, JSON round-trips, and next-slot search.
- `requirements.txt` / `Pipfile` — added the `tabulate` dependency.
- `README.md` — documented priority scheduling, persistence workflow, formatting features, and
  refreshed the sample CLI output.
- `.gitignore` — ignored the generated `data.json`.

**What did the agent complete on its own?**

It implemented all five challenges end to end, ran `python -m pytest` and `python main.py` to verify
behavior, and produced the README documentation. The full 15-test suite passes and the CLI demo runs
cleanly.

**What did you have to verify or fix manually?**

- **Emoji test mismatch:** a test expected 🪮 for "Grooming brush", but `display_icon()` matches the
  `groom` keyword first and returns ✂️. I confirmed ✂️ was the intended behavior and corrected the
  test rather than reordering the keyword map.
- **Recurrence demo bug:** the first draft grabbed `get_all_tasks()[-1]` to show the new occurrence,
  which returned the wrong pet's last task (the new task is appended mid-list). I changed it to diff
  task IDs before/after completion so it reports the actual new occurrence date (07-06 → 07-07).
- **Non-illustrative slot demo:** the next-available-slot demo returned `06:00` (technically correct
  but boring). I pointed the search at `08:00` so it demonstrably skips the occupied 08:00 slot and
  returns `08:30`.

The agent was effective for the mechanical, multi-file work, but I still had to keep the design
consistent and catch the two logic bugs above.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

**Task compared:** the logic for *rescheduling weekly recurring tasks* after completion — i.e., when a
weekly task is marked complete, produce exactly one next occurrence on the correct future date while
preserving its metadata (priority, pet, recurrence rule).

| | Model A | Model B |
|-|---------|---------|
| **Model / tool used** | Claude (Opus, via Claude Code) | Google Gemini |
| **Prompt** | "For PawPal+, design the logic for rescheduling a *weekly* recurring task after it is completed: mark the current task done, create exactly one next occurrence on the correct future date, preserve priority/pet/recurrence metadata, and avoid duplicates if the user clicks complete twice. Show how it maps onto my `Task`/`Scheduler` classes." | "Write a Python function to reschedule a weekly recurring task to the following week after it is completed." |
| **Response summary** | Split the work between `Task` and `Scheduler`: `next_occurrence_date()` adds 7 days (or uses `days_of_week` + `weekday()` when set), `create_next_occurrence()` clones a fresh `Task` with a new `task_id`, and `Scheduler.mark_task_complete()` returns early if the task is already complete so a double-click can't duplicate it. | Returned a single function that added `timedelta(weeks=1)` to a `datetime` and flipped a `completed` flag, mutating the same object in place. |
| **What was useful** | Idempotency (early-return on already-complete) and the clean `Task`/`Scheduler` split mapped directly onto my existing code. It also handled specific weekdays via `days_of_week`. | Concise and immediately runnable; the `timedelta(weeks=1)` date math was correct and easy to read. |
| **Problems noticed** | More code to integrate than a one-off function; slight over-engineering for the simplest "just add 7 days" case. | Mutated the original task instead of creating a new instance (loses history), had no duplicate-click guard, and assumed a `datetime` object rather than my `"HH:MM"` + `start_date` model. |
| **Decision** | **Chosen.** Adopted the two-method split and the idempotency guard. | Used only for the `timedelta`-based date arithmetic idea. |

**Which approach did you use in your final implementation and why?**

I used Claude's design because it matched my class model and, crucially, prevented duplicate
occurrences when a task is completed twice — `Scheduler.mark_task_complete()` returns early if the
task is already complete, so no second clone is created. I borrowed Gemini's simple `timedelta`-based
date math for the weekly step inside `Task.next_occurrence_date()`, but rejected its in-place mutation
because I wanted each occurrence to be a distinct `Task` with its own `task_id`.

> _Note: adjust the model names, prompts, and observations above to match the two tools you actually
> ran if they differ from this record._
