You are now using the Filter Application Skill.

When the user wants to list tasks:
- Check if they mentioned any filter word:
  - pending / not done / incomplete → status = "pending"
  - completed / done / finished → status = "completed"
  - nothing or all / everything → status = "all" (default)
- If no filter is detected → use "all"
- Pass the correct status parameter to list_tasks MCP tool
- Do not invent other filters unless explicitly supported later

Only apply status filter — ignore other filters for now.