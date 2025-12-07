import json
from pathlib import Path

TASKS_FILE = Path(__file__).resolve().parent / "tasks.json"

def load_tasks():
    """Load tasks from the JSON file."""

    #If tasks.json already exists -> load it.
    if TASKS_FILE.exists():
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
        
    #Otherwise -> return empty list
    return []

def save_tasks(tasks):
    """Write the updated list of tasks back to tasks.json."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def add_task(description):
    """Create and save a new task with the given text."""
    tasks = load_tasks()

    #Auto-assign a unique ID using length + 1
    new_task = {
        "id": len(tasks) + 1,
        "description": description,
        #New tasks are incomplete by default. 
        "completed": False
    }

    #Append new task to list
    tasks.append(new_task)

    #Save updated list.
    save_tasks(tasks)

def complete_task(task_id):
    """Mark a specific task as completed by modifying its 'completed' field."""
    tasks = load_tasks()
    
    # Find the matching task
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            #Stop early when we find the matching task
            break

    # Save updated task list
    save_tasks(tasks)
