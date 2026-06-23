from tag.model import EMPTY_TAG
from tag.repo import TagRepo
from task.model import TaskDraft
from task.repo import TaskRepo
from task.service import TaskService


def test_create_task_on_one_task_returns_correct_task(task_service: TaskService):
    draft = TaskDraft(None, "foo")
    task = task_service.create_task(draft)
    assert task.description == draft.description
    assert task.tag == draft.tag


def test_create_task_on_one_task_matches_database(
    task_service: TaskService, task_repo: TaskRepo
):
    draft = TaskDraft(None, "foo")
    task = task_service.create_task(draft)

    processes = task_repo.get_processes()
    assert processes == [task]


def test_create_task_on_multiple_separate_tasks(
    task_service: TaskService, task_repo: TaskRepo
):
    task1 = task_service.create_task(TaskDraft(None, "foo"))
    task2 = task_service.create_task(TaskDraft(None, "bar"))

    # Independent tasks, so shouldn't have parent/sub-tasks.
    assert task1.sub_tasks == []
    assert task1.parent is None
    assert task2.sub_tasks == []
    assert task2.parent is None

    processes = task_repo.get_processes()
    assert processes == [task1, task2]


def test_create_task_on_nested_tasks(task_service: TaskService, task_repo: TaskRepo):
    t = task_service.create_task

    process1 = t(TaskDraft(None, "foo"))
    subtask1a = t(TaskDraft(process1, "subtask of foo"))
    subtask1b = t(TaskDraft(process1, "another subtask"))

    process2 = t(TaskDraft(None, "alone"))

    assert process1.sub_tasks == [subtask1a, subtask1b]
    assert process1.parent is None

    assert process2.sub_tasks == []
    assert process2.parent is None

    assert subtask1a.parent == process1
    assert subtask1b.parent == process1

    processes = task_repo.get_processes()
    assert processes == [process1, process2]


def test_delete_task_on_nested(task_service: TaskService, task_repo: TaskRepo):
    t = task_service.create_task

    process1 = t(TaskDraft(description="foo"))
    subtask1a = t(TaskDraft(process1, "subtask of foo"))
    subtask1b = t(TaskDraft(process1, "another subtask"))

    process2 = t(TaskDraft(description="alone"))

    task_service.remove_tasks(None, process1.position, 1)

    processes = task_repo.get_processes()
    assert processes == [process2]


def test_edit_description(task_service: TaskService, task_repo: TaskRepo):
    OLD = "original description"
    NEW = "new description"

    task = task_service.create_task(TaskDraft(description=OLD))
    task_service.update_description(task, NEW)

    [process] = task_repo.get_processes()
    assert process.description == NEW


def test_edit_tag(task_service: TaskService, task_repo: TaskRepo, tag_repo: TagRepo):
    OLD = tag_repo.add_tag("old")
    NEW = tag_repo.add_tag("new")

    task = task_service.create_task(TaskDraft(tag=OLD))
    task_service.update_tag(task, NEW)

    [process] = task_repo.get_processes()
    assert process.tag == NEW


# TODO: test moving tag
def test_move_tag_into_new_parent(task_service: TaskService):
    t = task_service.create_task

    parent = t(TaskDraft())
    child = t(TaskDraft(parent))

    task = t(TaskDraft())
    new_position = 0
    task_service.move_task(task, parent, new_position)

    assert task.parent == parent
    assert task.position == new_position
    # Since the task is at position 0, this child task should be shifted to position 1
    assert child.position == new_position + 1

    assert parent.sub_tasks == [task, child]


def test_move_process_under_task_removes_tag(
    task_service: TaskService, tag_repo: TagRepo
):
    # Only processes should have tags.

    OLD = tag_repo.add_tag("foob")
    t = task_service.create_task

    parent = t(TaskDraft())
    task = t(TaskDraft(tag=OLD))

    task_service.move_task(task, parent, 0)
    print(task.parent)

    assert task.tag == EMPTY_TAG


def test_move_task_also_moves_children(task_service: TaskService):
    t = task_service.create_task

    parent = t(TaskDraft())
    child1 = t(TaskDraft(parent))
    child2 = t(TaskDraft(parent))

    grand_parent = t(TaskDraft(None))
    task_service.move_task(parent, grand_parent, 0)

    assert parent.sub_tasks == [child1, child2]
    assert parent.parent == grand_parent
    assert grand_parent.position == 0


def test_move_tag_into_same_parent(task_service: TaskService):
    t = task_service.create_task

    parent = t(TaskDraft())
    child1 = t(TaskDraft(parent))
    child2 = t(TaskDraft(parent))

    task_service.move_task(child1, parent, 2)
    assert parent.sub_tasks == [child2, child1]
    assert child1.position == 1
    assert child2.position == 0


def test_move_tag_into_new_parent_updates_source_positions(task_service: TaskService):
    t = task_service.create_task
    process1 = t(TaskDraft())
    process2 = t(TaskDraft())

    task_service.move_task(process1, process2, 0)
    assert process2.position == 0


def test_can_move_returns_false_for_same_parent_same_position(
    task_service: TaskService,
):
    t = task_service.create_task
    process1 = t(TaskDraft())
    process2 = t(TaskDraft(process1))

    assert not task_service.can_move(process2, process1, 0)


def test_can_move_returns_false_for_same_parent_position_plus_1(
    task_service: TaskService,
):
    t = task_service.create_task
    process1 = t(TaskDraft())
    process2 = t(TaskDraft(process1))

    assert not task_service.can_move(process2, process1, 1)


def test_can_move_returns_true_for_same_parent_but_not_a_noop(
    task_service: TaskService,
):
    t = task_service.create_task
    process1 = t(TaskDraft())
    process2 = t(TaskDraft(process1))
    process3 = t(TaskDraft(process1))

    assert task_service.can_move(process2, process1, 2)


def test_can_move_returns_true_for_different_parent(
    task_service: TaskService,
):
    t = task_service.create_task
    process1 = t(TaskDraft())
    process2 = t(TaskDraft())
    process3 = t(TaskDraft(process1))

    assert task_service.can_move(process3, process2, 0)
