You are now using the Database Persistence Skill.

For every tool call or agent action that changes data:
- Perform the database operation inside the tool
- Commit changes immediately
- Return success response only after commit
- If any DB error → rollback and return error to agent
- Log error internally but never expose DB details to user

Ensure complete atomicity for each tool invocation.