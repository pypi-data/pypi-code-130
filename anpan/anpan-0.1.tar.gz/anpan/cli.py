#!/usr/bin/env python
import datetime
import glob
import logging
import os
import re

import click
import inquirer


logging.basicConfig(level=logging.INFO)


TASKS_DIR = filename = os.path.join(os.path.dirname(__file__), "tasks/")
ALL_STATUS = [
    "backlog",
    "todo",
    "ongoing",
    "blocked",
    "done",
    "abandoned",
]


def task_name_to_filepath(task_name):
    """
    Generate filepath from task name
    """
    return os.path.join(TASKS_DIR, f"{task_name}.md")


class Task:
    def __init__(self, filepath: str):
        self.name = ".".join(filepath.split("/")[-1].split(".")[:-1])
        self.status = "unknown"
        self.due_date = None
        self.estimated_completion_time = None
        self.estimated_completion_date = None

        with open(filepath, "r") as f:
            lines = f.read()
            # Find status
            for status in ALL_STATUS:
                if f"#status__{status}" in lines:
                    self.status = status
                    break
            # Find due date
            match = re.search(r"#due__\d{8,8}", lines)
            if match:
                self.due_date = match.group(0)[6:]
            # Find estimated completion_time
            match = re.search(r"#ect__\d+", lines)
            if match:
                self.estimated_completion_time = match.group(0)[6:]
            # Find estimated completion date
            match = re.search(r"#ecd__\d{8,8}", lines)
            if match:
                self.estimated_completion_date = match.group(0)[6:]


def get_tasks() -> list:
    """
    Load all tasks from tasks directory.
    """
    filepaths = glob.glob(f"{TASKS_DIR}*", recursive=True)
    tasks = [Task(filepath) for filepath in filepaths]

    return tasks


@click.group()
def main():
    pass


@main.group()
def kanban():
    pass


@kanban.command("update")
def kanban_update_command():
    """
    Click command that runs kanban_update().

    This method exists since kanban_update() is called in other methods,
    and the click decorator prevents it from easily calling it.
    """
    kanban_update()


def kanban_update():
    """
    Update kanban using tags in tasks in `tasks/` folder.
    """
    logging.info("Updating kanban...")

    # Gather tasks
    tasks_per_status = { status: [] for status in ALL_STATUS + ["unknown"] }
    filepaths = glob.glob(f"{TASKS_DIR}*", recursive=True)
    for filepath in filepaths:
        task = Task(filepath)
        tasks_per_status[task.status].append(task)

    # Write to KANBAN.md
    with open("KANBAN.md", "w") as f:
        f.write("# KANBAN\n\n")
        for status, tasks in tasks_per_status.items():
            f.write(f"## {status.capitalize()}\n\n")
            for task in tasks:
                f.write(f"- [[{task.name}]]")
                if task.due_date:
                    f.write(f" (DUE {task.due_date})")
                if task.estimated_completion_time:
                    f.write(f" (ECT {task.estimated_completion_time})")
                if task.estimated_completion_date:
                    f.write(f" (ECD {task.estimated_completion_date})")
                f.write("\n")
            f.write("\n\n")

    logging.info("Kanban updated successfully.")


@kanban.command("status")
def kanban_status():
    """
    Show summary of the tasks
    """
    tasks = get_tasks()

    ## Find overdue / overecd tasks
    overdue_tasks = []
    overecd_tasks = []
    for task in tasks:
        if (task.status not in ["done", "abandoned"]
        and task.due_date
        and task.due_date < datetime.datetime.now().strftime("%Y%m%d")):
            overdue_tasks.append(task)
        if (task.status not in ["done", "abandoned"]
        and task.estimated_completion_date
        and task.estimated_completion_date < datetime.datetime.now().strftime("%Y%m%d")):
            overecd_tasks.append(task)
    overdue_tasks.sort(key=lambda task: task.due_date)
    overecd_tasks.sort(key=lambda task: task.estimated_completion_date)

    # Print overdue / overecd tasks
    if overdue_tasks or overecd_tasks:
        print(" Overdue Tasks")
        print("===============")
        for task in overdue_tasks:
            print(f"DUE {task.due_date} {task.name}")
        for task in overecd_tasks:
            print(f"ECD {task.estimated_completion_date} {task.name}")


@main.group()
def task():
    pass


@task.command("add")
@click.option("--name", prompt="Name of the task")
@click.option("--status", prompt=f"Status ({'/'.join(ALL_STATUS)})", default="todo")
@click.option("--due", prompt="Due date (YYYYMMDD)", default="")
@click.option("--ect", prompt="Estimated completion time (in minutes)", default="")
@click.option("--ecd", prompt="Estimated completion date (YYYYMMDD)", default="")
@click.option("--tags", prompt="Tags (separated by comma)", default="")
def task_add(name, status, due, ect, ecd, tags):
    """
    Add a new task Markdown file.
    """
    filepath = task_name_to_filepath(name)
    if os.path.exists(filepath):
        raise ValueError(f"{filepath} already exists.")
    with open(filepath, "w") as f:
        f.write(f"# {name}\n")
        f.write(f"#status__{status}\n")
        if due:
            f.write(f"#ect__{due}\n")
        if ect:
            f.write(f"#ect__{ect}\n")
        if ecd:
            f.write(f"#ecd__{ecd}\n")
        if tags:
            for tag in tags.split(","):
                f.write(f"#{tag.strip()}\n")

    logging.info(f"Added task {name}")
    kanban_update()


@task.command("start")
def task_start():
    """
    Change task status from todo to ongoing.
    """
    # Gather todo tasks
    todo_tasks = []
    filepaths = glob.glob(f"{TASKS_DIR}*", recursive=True)
    for filepath in filepaths:
        task = Task(filepath)
        if task.status == "todo":
            todo_tasks.append(task)

    # Ask user to choose the task
    questions = [
    inquirer.List(
        "name",
            message="Which task are you starting?",
            choices=[task.name for task in todo_tasks],
        ),
    ]
    answers = inquirer.prompt(questions)
    selected_task = todo_tasks[[task.name for task in todo_tasks].index(answers["name"])]

    # Update selected task file
    selected_filepath = task_name_to_filepath(selected_task.name)
    with open(selected_filepath, "r") as f:
        modified_text = f.read().replace("#status__todo", "#status__ongoing")

    with open(selected_filepath, "w") as f:
        f.write(modified_text)

    logging.info(f"Started task {selected_task.name}")
    kanban_update()


@task.command("done")
def task_done():
    """
    Change task status from todo/ongoing/blocked to done.
    """
    # Gather tasks
    tasks = []
    filepaths = glob.glob(f"{TASKS_DIR}*", recursive=True)
    for filepath in filepaths:
        task = Task(filepath)
        if task.status in ["todo", "ongoing", "blocked"]:
            tasks.append(task)

    # Ask user to choose the task
    questions = [
    inquirer.List(
        "name",
            message="Which task are you starting?",
            choices=[task.name for task in tasks],
        ),
    ]
    answers = inquirer.prompt(questions)
    selected_task = tasks[[task.name for task in tasks].index(answers["name"])]

    # Update selected task file
    selected_filepath = task_name_to_filepath(selected_task.name)
    with open(selected_filepath, "r") as f:
        modified_text = f.read().replace(f"#status__{selected_task.status}", "#status__done")

    with open(selected_filepath, "w") as f:
        f.write(modified_text)

    logging.info(f"Finished task {selected_task.name}")
    kanban_update()


if __name__ == '__main__':
    main()
