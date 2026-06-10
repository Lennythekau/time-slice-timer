from dataclasses import dataclass, field

from lib.event import Event0
from tag.model import Tag
from task.model import Task, TaskDraft
from task.repo import TaskRepo
from user_session import UserSession


@dataclass
class TaskService:
    __session: UserSession
    task_repo: TaskRepo
    tasks_changed: Event0 = field(init=False, default_factory=Event0)

    def __post_init__(self):
        self.__session.processes = self.task_repo.get_processes()

    def get_children(self, parent: Task | None):
        if parent is None:
            return self.__session.processes
        else:
            return parent.sub_tasks

    def find_task_in_parent(self, child_task: Task):
        source = self.get_children(child_task.parent)
        return source.index(child_task)

    def create_task(self, draft: TaskDraft):
        task = self.task_repo.create_task(draft)
        sink = self.get_children(task.parent)
        if draft.index == -1:
            sink.append(task)
        else:
            sink.insert(draft.index, task)
        self.tasks_changed()
        return task

    def get_tag(self, task: Task):
        while task.parent is not None:
            task = task.parent

        return task.tag

    def remove_tasks(self, parent_task: Task | None, start_index: int, count: int):
        source = self.get_children(parent_task)

        tasks_to_delete = source[start_index : start_index + count]
        source[start_index : start_index + count] = []

        for task in tasks_to_delete:
            self.task_repo.delete_task(task.task_id)
        self.tasks_changed()

    def update_description(self, task: Task, value: str):
        task.description = value
        self.task_repo.update(task)
        self.tasks_changed()

    def update_tag(self, task: Task, value: Tag):
        task.tag = value
        self.task_repo.update(task)
        self.tasks_changed()
