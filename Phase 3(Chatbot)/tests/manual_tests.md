# Manual Testing Instructions for Todo App

## Setup
1. Ensure Python 3.13+ is installed
2. Install dependencies: `pip install -e .` or run directly with Python
3. Run the application: `python -m src.todo_app.main`

## Test Cases

### 1. Add Task Functionality
**Objective**: Verify that users can add tasks with title and description
**Steps**:
1. Start the application
2. Enter: `add "Buy groceries" "Milk, bread, eggs"`
3. Verify task is added with auto-incremented ID
4. Enter: `add "Finish report" "Complete the quarterly report"`
5. Verify second task is added with next ID

**Expected Result**: Two tasks added successfully with IDs 1 and 2

### 2. List Tasks Functionality
**Objective**: Verify that users can view all tasks
**Steps**:
1. Add at least one task
2. Enter: `list`
3. Verify all tasks are displayed with status indicators and descriptions

**Expected Result**: All tasks shown with [ ] for pending, IDs, titles, and descriptions

### 3. Update Task Functionality
**Objective**: Verify that users can update task details by ID
**Steps**:
1. Add a task: `add "Old title" "Old description"`
2. Enter: `update 1 "New title" "New description"`
3. Enter: `list` to verify changes

**Expected Result**: Task details updated successfully

### 4. Delete Task Functionality
**Objective**: Verify that users can delete tasks by ID
**Steps**:
1. Add a task: `add "Task to delete" "Description"`
2. Enter: `delete 1`
3. Enter: `list` to verify task is removed

**Expected Result**: Task removed from list

### 5. Complete Task Functionality
**Objective**: Verify that users can toggle task completion status
**Steps**:
1. Add a task: `add "Task to complete" "Description"`
2. Enter: `complete 1`
3. Enter: `list` to verify status change
4. Enter: `complete 1` again
5. Enter: `list` to verify status toggles back

**Expected Result**: Task status toggles between [ ] and [x]

### 6. Empty List Handling
**Objective**: Verify behavior when list is empty
**Steps**:
1. Start fresh application with no tasks
2. Enter: `list`

**Expected Result**: Shows "No tasks found. Add a task to get started!"

### 7. Invalid ID Handling
**Objective**: Verify behavior when using non-existent task IDs
**Steps**:
1. Enter: `update 999 "New title" "New description"`
2. Enter: `delete 999`
3. Enter: `complete 999`

**Expected Result**: Shows message asking to try again with different ID

### 8. Invalid Command Handling
**Objective**: Verify behavior when using invalid commands
**Steps**:
1. Enter: `invalidcommand`

**Expected Result**: Shows message about available commands

### 9. Required Title Validation
**Objective**: Verify that titles are required
**Steps**:
1. Enter: `add "" "Description"`

**Expected Result**: Shows error message that title is required

## Edge Cases to Verify

1. **Empty Description**: `add "Title" ""` should work (description is optional)
2. **Special Characters**: Add tasks with special characters, quotes, etc.
3. **Long Text**: Add tasks with very long titles and descriptions
4. **Sequential IDs**: Verify IDs continue incrementing after deletion (don't reuse IDs)
5. **Quit Command**: Verify `quit` command exits cleanly