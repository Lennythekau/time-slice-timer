from dataclasses import dataclass, field
from pprint import pformat

from lib.event import Event0
from tag.model import EMPTY_TAG, Tag
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

    def get_parent_id(self, task: Task) -> int | None:
        return None if task.parent is None else task.parent.task_id

    def find_task_in_parent(self, child_task: Task):
        source = self.get_children(child_task.parent)
        return source.index(child_task)

    def __adjust_position_values(self, tasks: list[Task], start_index: int):
        """Adjust the position fields for `tasks` starting from `start_index.`"""
        for i in range(start_index, len(tasks)):
            task = tasks[i]
            task.position = i

    def create_task(self, draft: TaskDraft):
        sink = self.get_children(draft.parent)
        if draft.position == -1:
            draft = draft._replace(position=len(sink))

        task = self.task_repo.create_task(draft)
        sink.insert(draft.position, task)
        self.__adjust_position_values(sink, draft.position + 1)

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
            self.task_repo.delete_task(
                task.task_id, self.get_parent_id(task), task.position
            )

        self.__adjust_position_values(source, start_index)
        self.tasks_changed()

    def can_move(self, task: Task, new_parent: Task | None, position: int):
        # No-op case
        if (
            position
            in (task.position, task.position + 1)  # the gap just before/after task
            # still keeping the same parent, so just rearranging siblings
            and new_parent == task.parent
        ):
            return False

        # decide if new_parent is a descendent of task
        current = new_parent
        while current is not None:
            if current == task:
                return False
            current = current.parent
        return True

    def move_task(self, task: Task, new_parent: Task | None, position: int):
        print(
            f"START move_task(\n- task={pformat(task)},\n- destination={pformat(new_parent)},\n- position={pformat(position)})"
        )

        old_position = task.position
        old_parent_id = self.get_parent_id(task)

        # remove the task from its original parent
        source = self.get_children(task.parent)
        source.pop(old_position)
        self.__adjust_position_values(source, old_position)

        sink = self.get_children(new_parent)

        # Issue if the source position < destination position.
        if task.parent == new_parent and task.position < position:
            new_position = position - 1
            print(f"Same parent => {new_position=}")
        else:
            new_position = position

        # add the task to the new parent
        sink.insert(new_position, task)
        self.__adjust_position_values(sink, new_position + 1)

        task.parent = new_parent
        task.position = new_position

        # Only processes are allowed to have tags
        if task.parent is not None:
            task.tag = EMPTY_TAG

        new_parent_id = None if new_parent is None else new_parent.task_id

        self.task_repo.move_task(
            task.task_id, old_parent_id, new_parent_id, old_position, new_position
        )

        self.tasks_changed()
        print("END move_task")

    def update_description(self, task: Task, value: str):
        task.description = value
        self.task_repo.update(task)
        self.tasks_changed()

    def update_tag(self, task: Task, value: Tag):
        task.tag = value
        self.task_repo.update(task)
        self.tasks_changed()
