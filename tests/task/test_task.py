from tag.repo import TagRepo
from task.model import TaskDraft
from task.repo import TaskRepo
from task.controller import TaskController


def test_create_task_on_one_task_returns_correct_task(task_controller: TaskController):
    draft = TaskDraft(None, "foo")
    task = task_controller.create_task(draft)
    assert task.description == draft.description
    assert task.tag == draft.tag


def test_create_task_on_one_task_matches_database(
    task_controller: TaskController, task_repo: TaskRepo
):
    draft = TaskDraft(None, "foo")
    task = task_controller.create_task(draft)

    processes = task_repo.get_processes()
    assert processes == [task]


def test_create_task_on_multiple_separate_tasks(
    task_controller: TaskController, task_repo: TaskRepo
):
    task1 = task_controller.create_task(TaskDraft(None, "foo"))
    task2 = task_controller.create_task(TaskDraft(None, "bar"))

    # Independent tasks, so shouldn't have parent/sub-tasks.
    assert task1.sub_tasks == []
    assert task1.parent is None
    assert task2.sub_tasks == []
    assert task2.parent is None

    processes = task_repo.get_processes()
    assert processes == [task1, task2]


def test_create_task_on_nested_tasks(
    task_controller: TaskController, task_repo: TaskRepo
):
    t = task_controller.create_task

    process1 = t(TaskDraft(None, "foo"))
    subtask1a = t(TaskDraft(process1, "subtask of foo"))
    subtask1b = t(TaskDraft(process1, "another subtask"))

    process2 = t(TaskDraft(None, "alone"))

    assert process1.sub_tasks == [subtask1a, subtask1b]
    assert process2.sub_tasks == []

    processes = task_repo.get_processes()
    assert processes[0].sub_tasks == process1.sub_tasks


def test_delete_task_on_nested(task_controller: TaskController, task_repo: TaskRepo):
    t = task_controller.create_task

    process1 = t(TaskDraft(None, "foo"))
    subtask1a = t(TaskDraft(process1, "subtask of foo"))
    subtask1b = t(TaskDraft(process1, "another subtask"))

    process2 = t(TaskDraft(None, "alone"))

    task_controller.remove_tasks(None, task_controller.find_task_in_parent(process1), 1)

    processes = task_repo.get_processes()
    assert processes == [process2]


def test_edit_description(task_controller: TaskController, task_repo: TaskRepo):
    OLD = "original description"
    NEW = "new description"

    task = task_controller.create_task(TaskDraft(None, OLD))
    task_controller.update_description(task, NEW)

    [process] = task_repo.get_processes()
    assert process.description == NEW


def test_edit_tag(
    task_controller: TaskController, task_repo: TaskRepo, tag_repo: TagRepo
):
    OLD = tag_repo.add_tag("old")
    NEW = tag_repo.add_tag("new")

    task = task_controller.create_task(TaskDraft(None, tag=OLD))
    task_controller.update_tag(task, NEW)

    [process] = task_repo.get_processes()
    assert process.tag == NEW
