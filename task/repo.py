from dataclasses import dataclass

from sqlite_setup import ConnectionFactory
from tag.model import EMPTY_TAG, Tag
from task.model import Task, TaskDraft

# If the parent id is equal to the passed in value,
# Of if both the passed in value and the parent id is null.
_PARENT_EQUAL_SQL = "(parent_id=? OR (? IS NULL AND parent_id is NULL))"


@dataclass
class TaskRepo:
    make_connection: ConnectionFactory

    def __get_rows(self):
        with self.make_connection() as connection:
            rows = connection.execute(
                """SELECT task.task_id, task.parent_id, task.description, task.tag_id, tag.name, task.position
                        FROM task
                        LEFT JOIN tag
                        ON task.tag_id = tag.tag_id"""
            ).fetchall()
        connection.close()
        return rows

    def get_processes(self):
        rows = self.__get_rows()

        tasks_by_id: dict[int, Task] = {}

        for row in rows:
            task_id, parent_id, description, tag_id, tag_name, task_position = row
            if tag_id == EMPTY_TAG.tag_id:
                tag = EMPTY_TAG
            else:
                tag = Tag(tag_id, tag_name)
            tasks_by_id[task_id] = Task(
                task_id, None, description, tag, position=task_position
            )

        # Now that we've made each task object (but without children),
        # go through the rows again and make the tree relationships between the tasks.
        # and find out what the processes are.

        processes = list[Task]()
        for row in rows:
            task_id, parent_id, *_ = row
            task = tasks_by_id[task_id]

            if parent_id is not None:
                parent = tasks_by_id[parent_id]

                # Add task as child of parent. This may be in the wrong position.
                parent.sub_tasks.append(task)

                task.parent = parent
            else:
                processes.append(task)

        # Recursively correct the positions of each task's subtasks.
        self.__correct_positions(processes)

        return processes

    def __correct_positions(self, tasks: list[Task]):

        for i, task in enumerate(tasks):

            # Pigeonhole sort
            # Put this task in the correct position:
            # (put the current task at task.position)
            # (and whatever was originally there now goes here)
            tasks[task.position], tasks[i] = task, tasks[task.position]

        # now correct the positions of all the subtasks:
        for task in tasks:
            self.__correct_positions(task.sub_tasks)

    def create_task(self, draft: TaskDraft) -> Task:
        if draft.parent is not None:
            parent_id = draft.parent.task_id
        else:
            parent_id = None

        with self.make_connection() as connection:
            # Make space for the task, by shifting the position fields of the tasks that will come after
            connection.execute(
                f"""UPDATE task SET position=position + 1 
                WHERE {_PARENT_EQUAL_SQL} AND position >= ?""",
                (parent_id, parent_id, draft.position),
            )

            cursor = connection.execute(
                "INSERT INTO task (description, parent_id, tag_id, position) VALUES (?, ?, ?, ?)",
                (draft.description, parent_id, draft.tag.tag_id, draft.position),
            )

            assert cursor.lastrowid is not None
            task = Task(
                cursor.lastrowid,
                draft.parent,
                draft.description,
                draft.tag,
                position=draft.position,
            )

        connection.close()

        return task

    def update(self, task: Task):
        """Only for updating the description, tag or parent!"""

        with self.make_connection() as connection:
            connection.execute(
                "UPDATE task SET description=?,tag_id=? WHERE task_id=?",
                (
                    task.description,
                    task.tag.tag_id,
                    task.task_id,
                ),
            )
        connection.close()
        return task

    def delete_task(self, task_id: int, parent_id: int | None, position: int):
        """Deletes the whole tree of tasks, rooted at the task with id `task_id`."""

        # This works because in the sqlite setup, we use cascade
        with self.make_connection() as connection:
            connection.execute("DELETE FROM task WHERE task_id=?", (task_id,))

            # We then need to find all the siblings which have a position greater than the position of this task
            connection.execute(
                f"""
                UPDATE task SET position=position-1
                WHERE {_PARENT_EQUAL_SQL} AND position > ?""",
                (parent_id, parent_id, position),
            )
        connection.close()

    def move_task(
        self,
        task_id: int,
        old_parent_id: int | None,
        new_parent_id: int | None,
        old_position: int,
        new_position: int,
    ):
        """
        `target_position` must be the index after the move. This means that if the parent has remainded the same,
        the position must be subtracted by 1 before passing into this function.
        """

        with self.make_connection() as connection:
            # update old siblings
            connection.execute(
                f"UPDATE task SET position=position-1 WHERE {_PARENT_EQUAL_SQL} AND position > ?",
                (old_parent_id, old_parent_id, old_position),
            )

            # update new siblings
            # since the task might still be at the same parent as it originally was,
            # we need to make sure we don't accidentally shift it here
            connection.execute(
                f"UPDATE task SET position=position+1 WHERE {_PARENT_EQUAL_SQL} AND position >= ? AND task_id != ?",
                (new_parent_id, new_parent_id, new_position, task_id),
            )

            # - add the task to the parent
            # - adjust its position to the target
            connection.execute(
                f"UPDATE task SET parent_id=?, position=? WHERE task_id=?",
                (new_parent_id, new_position, task_id),
            )

            # - if there is now a parent, then remove its tag.
            connection.execute(
                f"UPDATE task SET tag_id=-1 WHERE task_id=? AND parent_id IS NOT NULL",
                (task_id,),
            )
        connection.close()
