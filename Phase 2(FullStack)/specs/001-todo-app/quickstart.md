# Quickstart Guide: Basic In-Memory Todo Console App

## Project Setup

1. **Prerequisites**: Python 3.13+ installed on your system
2. **Virtual Environment**: Use UV for dependency management (though no external dependencies required for this phase)

## Running the Application

1. Navigate to the project directory
2. Run the application: `python -m src.todo_app.main`
3. The interactive CLI will start, showing a prompt

## Available Commands

- `add "title" "description"` - Add a new task with title and description
- `list` - Display all tasks with their IDs and status indicators
- `update <id> "new_title" "new_description"` - Update task details by ID
- `delete <id>` - Remove a task by ID
- `complete <id>` - Toggle completion status of a task by ID
- `quit` - Exit the application

## Example Usage

```
Welcome to the Todo App!
Available commands: add, list, update <id>, delete <id>, complete <id>, quit
For add: use add "title" "description"
Type 'quit' to exit the application.

> add "Buy groceries" "Milk, bread, eggs"
Added task #1: Buy groceries

> add "Finish report" "Complete the quarterly report"
Added task #2: Finish report

> list
[ ] 1: Buy groceries
      Description: Milk, bread, eggs
[ ] 2: Finish report
      Description: Complete the quarterly report

> complete 1
Task #1 marked as complete.

> list
[x] 1: Buy groceries
      Description: Milk, bread, eggs
[ ] 2: Finish report
      Description: Complete the quarterly report

> quit
Goodbye!
```

## Development

1. The main entry point is in `src/todo_app/main.py`
2. Task model is defined in `src/todo_app/task.py`
3. Task management logic is in `src/todo_app/task_manager.py`
4. CLI interface is handled in `src/todo_app/cli.py`