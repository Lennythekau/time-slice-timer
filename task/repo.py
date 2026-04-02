from typing import cast
from dataclasses import dataclass

from sqlite_setup import ConnectionFactory
from tag.model import Tag

from .model import Task


@dataclass
class TaskRepo:
    make_connection: ConnectionFactory

    def add_task(self, description: str, tag: Tag | None, parent: Task | None):
        parent_id = None if parent is None else parent.task_id
        tag_id = None if tag is None else tag.tag_id

        with self.make_connection() as connection:
            cursor = connection.execute(
                """INSERT INTO task (parent_id, description_tag_id, tag_id)
                    VALUES (?, ?, ?)""",
                (parent_id, description, tag_id),
            )
        connection.close()

        task_id = cast(int, cursor.lastrowid)
        return Task(task_id, parent, description, tag)

    def delete_task(self, task_id: int):
        """These ids should form a subtree for correctness."""

        with self.make_connection() as connection:
            connection.execute("DELETE FROM task WHERE task_id=?", (task_id,))
        connection.close()

    def __get_rows(self):
        with self.make_connection() as connection:
            rows = connection.execute(
                """SELECT task.task_id, task.parent_id, task.description, task.tag_id, tag.name
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
            task_id, parent_id, description, tag_id, tag_name = row

            if tag_id is not None:
                assert tag_name is not None
                tag = Tag(tag_id, tag_name)
            else:
                tag = None

            tasks_by_id[task_id] = Task(task_id, None, description, tag)

        # Now that we've made each task object (but without children),
        # go through the rows again and make the tree relationships between the tasks.
        # and find out what the processes are.

        processes = list[Task]()
        for row in rows:
            task_id, parent_id, *_ = row
            task = tasks_by_id[task_id]

            if parent_id is not None:
                parent = tasks_by_id[parent_id]

                # Add task as child of parent
                parent.sub_tasks.append(task)

                # Add parent to task
                task.parent = parent
            else:
                processes.append(task)

        return processes

    def write(self, task: Task):
        parent_id = None if task.parent is None else task.parent.task_id
        with self.make_connection() as connection:
            # Write
            if task.task_id == task.UNSET_ID:
                cursor = connection.execute(
                    "INSERT INTO task (description, parent_id) VALUES (?, ?)",
                    (task.description, parent_id),
                )
                assert cursor.lastrowid is not None
                task.task_id = cursor.lastrowid
            # Update
            else:
                connection.execute(
                    "UPDATE task SET description=?, parent_id=?",
                    (task.description, parent_id),
                )

        connection.close()
        return task
