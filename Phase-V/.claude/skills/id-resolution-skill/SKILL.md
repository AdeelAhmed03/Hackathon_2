You are now using the ID Resolution Skill.

When user refers to a task without giving a number (e.g. "delete the groceries task"):
1. First call list_tasks to get current tasks
2. Search the titles/descriptions for a close match to what user said
3. If exactly one strong match → use that task_id
4. If multiple matches → ask user which one (show short list)
5. If no match → tell user politely and suggest listing tasks first

Never guess or delete wrong task — always verify.