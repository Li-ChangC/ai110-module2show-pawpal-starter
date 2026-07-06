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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
