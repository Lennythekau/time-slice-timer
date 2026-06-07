from dataclasses import dataclass, field

from tag.model import Tag
from task.model import Task, TaskDraft
from task.repo import TaskRepo


@dataclass
class TaskController:
    task_repo: TaskRepo
    processes: list[Task] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.processes = self.task_repo.get_processes()

    def get_children(self, parent: Task | None):
        if parent is None:
            return self.processes
        else:
            return parent.sub_tasks

    def create_task(self, draft: TaskDraft):
        task = self.task_repo.create_task(draft)
        sink = self.get_children(task.parent)
        if draft.index == -1:
            sink.append(task)
        else:
            sink.insert(draft.index, task)
        return task

    def remove_tasks(self, parent_task: Task | None, start_index: int, count: int):
        source = self.get_children(parent_task)

        tasks_to_delete = source[start_index : start_index + count]
        source[start_index : start_index + count] = []

        for task in tasks_to_delete:
            self.task_repo.delete_task(task.task_id)

    def find_task_in_parent(self, child_task: Task):
        source = self.get_children(child_task.parent)
        return source.index(child_task)

    def update_description(self, task: Task, value: str):
        task.description = value
        self.task_repo.update(task)

    def update_tag(self, task: Task, value: Tag):
        task.tag = value
        self.task_repo.update(task)
