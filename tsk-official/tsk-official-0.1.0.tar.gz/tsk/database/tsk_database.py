from datetime import datetime
import os
import sqlite3
from typing import List

from tsk.settings import Settings
from tsk import utils

from tsk.models.task import Task
from tsk.models.tasklist import Tasklist


class TskDatabase:
    """SQLite Database wrapper for tsk."""

    def __init__(self):
        self.conf = Settings()
        db_path = os.path.join(os.path.dirname(__file__), self.conf["Database"]["filename"])
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()

        # initial table creation sequence
        with self.conn:
            self._create_tasklists_table()
            self._add_default_tasklist_ifndef()
            self._create_tasks_table()
    
    def _create_tasklists_table(self):
        """Add a Tasklists table to the Database if it doesn't exist.
        - Tasklists:
            * id         (str) : tasklist id
            * title      (str) : name of the tasklist
        """

        self.c.execute("""CREATE TABLE IF NOT EXISTS Tasklists
            (
                id TEXT,
                title TEXT
            )
        """)
    
    def _add_default_tasklist_ifndef(self):
        """Add the default tasklist to the Tasklists table
        if there are no tasklists to ensure tasklist availability.
        """

        num_rows = self.c.execute("""
            SELECT COUNT(*) FROM Tasklists
        """).fetchone()[0]
        if not num_rows:
            default_tasklist = Tasklist(
                title='Tasks',
                id=self.conf['Database']['default_tasklist_id']
            )
            self.add_tasklist(default_tasklist)
            self.conf['TaskDefaults']['tasklist_id'] = default_tasklist.id
            self.conf.commit()
    
    def _create_tasks_table(self):
        """Add a Tasks table to the Database if it doesn't exist.
        - Tasks:
            * id           (str): task id
            * tasklist_id  (str): parent tasklist id
            * title        (str): task name
            * is_completed (bool): indicates if the task is finished
            * priority     (int): 1-3 importance rank (1 lowest / 3 highest)
            * date_created (str): task creation date timestamp
            * date_due     (str): date the task should be completed by
            * notes        (str): additional task information
        """
        
        self.c.execute("""CREATE TABLE IF NOT EXISTS Tasks
            (
                id TEXT,
                tasklist_id TEXT,
                title TEXT,
                is_completed INTEGER,
                priority INTEGER,
                date_created TEXT,
                date_due TEXT,
                notes TEXT
            )
        """)
    
    def _transform_tasklist(self, tasklist_data) -> Tasklist:
        tasklist = Tasklist(
            title=tasklist_data[1],
            id=tasklist_data[0]
        )
        return tasklist

    def _transform_task(self, task_data) -> Task:
        task = Task(
            tasklist_id=task_data[1],
            title=task_data[2],
            is_completed=task_data[3],
            priority=task_data[4],
            date_created=utils.tstr_to_tstamp(task_data[5]),
            date_due=utils.tstr_to_tstamp(task_data[6]),
            notes=task_data[7],
            id=task_data[0],
        )
        return task
    
    def is_tasklist(self, id: str) -> bool:
        """Returns True if id matches a row in Tasklists
        and False otherwise.
        """
        self.c.execute("SELECT COUNT(*) FROM Tasklists WHERE id=?", (id,))
        return self.c.fetchone()[0]
 
    def add_tasklist(self, tasklist: Tasklist):
        """Adds a tasklist to Tasklists."""
        with self.conn:
            self.c.execute("""INSERT INTO Tasklists
                (
                    id, title
                )
                VALUES (?,?)""",
                (
                    tasklist.id, tasklist.title
                )
            )
    
    def add_task(self, task: Task):
        """Adds a task to Tasks."""
        with self.conn:
            self.c.execute("""INSERT INTO Tasks
                (
                    id, tasklist_id,
                    title, is_completed,
                    priority, date_created,
                    date_due, notes
                )
                VALUES (?,?,?,?,?,?,?,?)""",
                (
                    task.id, task.tasklist_id,
                    task.title, task.is_completed,
                    task.priority,
                    utils.tstamp_to_tstr(task.date_created),
                    utils.tstamp_to_tstr(task.date_due),
                    task.notes
                )
            )

    def get_tasklists(self, query_ids: List[str]=[]) -> List[Tasklist]:
        """Returns a list of all tasklists. Override query_ids
        to specify specific tasklists needed."""

        tasklists = []
        if query_ids:
            for query_id in query_ids:
                self.c.execute("""
                    SELECT * FROM Tasklists WHERE id=?
                """, (query_id,))
                qres = self.c.fetchone()
                tasklists.append(self._transform_tasklist(qres))
        else:
            self.c.execute("""
                SELECT * FROM Tasklists
            """)
            res = self.c.fetchall()
            if res:
                [tasklists.append(self._transform_tasklist(tasklist_data)) for tasklist_data in res]
        
        return tasklists

    def get_tasks(self, tasklist_id: str) -> List[Task]:
        """Returns a list of Tasks that are in the Tasklist.
        If no Tasks match the Tasklist or if the id doesn't exist,
        an empty list is returned.
        """

        self.c.execute("""
            SELECT * FROM Tasks WHERE tasklist_id=?
        """, (tasklist_id,))
        res = self.c.fetchall()
        if res:
            tasks = [self._transform_task(task_data) for task_data in res]
            return tasks
        return []
    
    def get_tasks_by_ids(self, task_ids: List[str]) -> List[Task]:
        """Returns a list of Tasks given the ids. If the ids are not found,
        then an empty list is returned.
        """

        tasks = []
        for task_id in task_ids:
            self.c.execute("""
                SELECT * FROM Tasks WHERE id=?
            """, (task_id,))
            res = self.c.fetchone()
            if res is None:
                print(f'Task id {task_id} not found')
            else:
                tasks.append(self._transform_task(res))

        return tasks

    def set_tasks_completion(self, ids: List[str], is_set_complete: bool):
        """Sets is_completed to is_set_complete for all tasks in ids."""
        
        params = [(is_set_complete, id) for id in ids]
        with self.conn:
            self.c.executemany("""
                UPDATE Tasks SET is_completed=? WHERE id=?
            """, params)

    def remove_tasklists(self, tasklist_ids: List[str]):
        """Removes all tasklists with matching ids. Also deletes all
        tasks within the matching tasklists.
        """
        tasklist_ids = [(id,) for id in tasklist_ids]
        with self.conn:
            # delete tasklists
            self.c.executemany("""
                DELETE FROM Tasklists WHERE id=?
            """, tasklist_ids)
            # delete tasks associated with tasklists
            self.c.executemany("""
                DELETE FROM Tasks WHERE tasklist_id=?
            """, tasklist_ids)

    def remove_tasks(self, ids: List[str]):
        """Removes all tasks with matching ids."""
        ids = [(id,) for id in ids]
        with self.conn:
            self.c.executemany("""
                DELETE FROM Tasks WHERE id=?
            """, ids)

    def update_tasklist(self, id: str, title: str=None):
        """Updates a tasklist."""

        with self.conn:
            self.c.execute("""
                UPDATE Tasklists
                SET title=CASE WHEN :title IS NOT NULL
                    THEN :title ELSE title END
                WHERE id=:id""",
                {
                    'title': title,
                    'id': id
                }
            )

    def update_task(self, id: str, title: str=None,
                    priority: int=None, date_due: datetime=None,
                    notes: str=None):
        """Updates a task."""
        
        date_due_val = utils.tstamp_to_tstr(date_due) if date_due \
            is not None else date_due
        with self.conn:
            self.c.execute("""
                UPDATE Tasks
                SET title=CASE WHEN :title IS NOT NULL
                        THEN :title ELSE title END,
                    priority=CASE WHEN :priority IS NOT NULL
                        THEN :priority ELSE priority END,
                    date_due=CASE WHEN :date_due IS NOT NULL
                        THEN :date_due ELSE date_due END,
                    notes=CASE WHEN :notes IS NOT NULL
                        THEN :notes ELSE notes END
                WHERE id=:id""",
                {
                    'title': title, 'priority': priority,
                    'date_due': date_due_val, 'notes': notes,
                    'id': id
                }
            )

    def wipe(self):
        """Removes all tasklists and tasks."""
        with self.conn:
            self.c.executescript("""
                DROP TABLE Tasklists;
                DROP TABLE Tasks
            """)
