# Data Model: Basic In-Memory Todo Console App

## Task Entity

### Fields
- **id**: `int` - Unique auto-incrementing identifier for the task
- **title**: `str` - Title/description of the task (required)
- **description**: `str` - Detailed description of the task (optional, can be empty string)
- **completed**: `bool` - Status indicator (False = pending, True = complete)

### Validation Rules
- **id**: Must be a positive integer, auto-incremented from the previous highest ID
- **title**: Must not be empty or contain only whitespace
- **description**: Can be any string (including empty)
- **completed**: Must be a boolean value (True/False)

### State Transitions
- **Pending to Complete**: When user marks task as complete using 'complete <id>' command
- **Complete to Pending**: When user marks completed task as pending again using 'complete <id>' command

## Task Collection

### Structure
- **tasks**: `dict[int, Task]` - Dictionary mapping task IDs to Task objects
- **next_id**: `int` - Counter for the next available task ID (auto-incrementing)

### Operations
- **Add Task**: Create new Task object, assign next available ID, add to tasks dictionary
- **Get Task**: Retrieve Task object by ID from tasks dictionary
- **Update Task**: Modify existing Task object in tasks dictionary
- **Delete Task**: Remove Task object from tasks dictionary by ID
- **List Tasks**: Return all Task objects from tasks dictionary