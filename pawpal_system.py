from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class TaskInfo:
    taskType: str
    description: str = ""
    priority: str = "medium"
    preferredTime: str = ""
    durationMinutes: int = 0
    preferences: list[str] = field(default_factory=list)

    def setPriority(self, priority: str) -> None:
        pass

    def addPreference(self, preference: str) -> None:
        pass

    def isCompatibleWith(self, otherTask: TaskInfo) -> bool:
        pass


@dataclass
class PetInfo:
    species: str
    name: str
    gender: str = ""
    dob: date | None = None
    breed: str = ""
    healthIssues: list[str] = field(default_factory=list)

    def calculateAge(self) -> int:
        pass

    def updateHealthIssue(self, issue: str) -> None:
        pass

    def getCareSummary(self) -> str:
        pass


class PetCareTasks:
    def __init__(self) -> None:
        self.tasks: list[TaskInfo] = []

    def addTask(self, task: TaskInfo) -> None:
        pass

    def removeTask(self, taskId: str) -> None:
        pass

    def getTasks(self) -> list[TaskInfo]:
        pass


class Schedule:
    def __init__(self) -> None:
        self.scheduleDate: date | None = None
        self.scheduledTasks: list[TaskInfo] = []
        self.availableTimeSlots: list[str] = []
        self.constraints: list[str] = []

    def setAvailability(self, timeSlots: list[str]) -> None:
        pass

    def addTask(self, task: TaskInfo) -> bool:
        pass

    def removeTask(self, taskId: str) -> None:
        pass

    def canSchedule(self, task: TaskInfo, timeSlot: str) -> bool:
        pass

    def getSchedule(self) -> list[TaskInfo]:
        pass