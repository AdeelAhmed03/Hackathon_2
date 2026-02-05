You are now using the Tool Definition Skill.

When defining or reviewing MCP tools:
- Follow exact parameter names and types from the Phase III spec
- Every tool must require user_id (string) for ownership check
- Return consistent JSON shape: {task_id, status, title} or array for list
- Include clear description and example input/output in tool metadata
- Validate all inputs before DB operation
- Raise proper error if validation fails

Do not deviate from documented tool signatures.