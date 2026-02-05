# Quickstart: AI Todo Chatbot (Phase III)

**Feature**: AI Todo Chatbot
**Date**: 2026-02-04
**Status**: Implementation Complete

This guide walks through setting up and running the AI chatbot feature locally.

---

## Prerequisites

- Python 3.13+ installed
- Node.js 18+ installed
- Existing Phase II setup running (FastAPI + Next.js)
- Cohere API account and API key (already configured in this project)

---

## Step 1: Get Cohere API Key

1. Sign up at [https://dashboard.cohere.com/](https://dashboard.cohere.com/)
2. Navigate to API Keys section
3. Create a new API key (or use existing)
4. Copy the key for next step

---

## Step 2: Configure Environment

Add to `backend/.env`:
```bash
# Existing variables (keep these)
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret

# NEW for Phase III
COHERE_API_KEY=your-cohere-api-key-here
```

---

## Step 3: Install Backend Dependencies

```bash
cd backend
pip install cohere
# or add to requirements.txt and run:
pip install -r requirements.txt
```

---

## Step 4: Start Backend

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

On startup, new tables (conversation, message) will be created automatically.

---

## Step 5: Start Frontend

```bash
cd frontend
npm run dev
```

---

## Step 6: Test the Chat

### Via cURL

```bash
# First, get a JWT token by logging in
# Then test the chat endpoint:

curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what can you do?"}'
```

Expected response:
```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "Hello! I can help you manage your tasks. You can ask me to add, list, complete, update, or delete tasks."
  },
  "tool_executed": false
}
```

### Via Frontend

1. Navigate to `http://localhost:3000/chat`
2. Log in if not already authenticated
3. Type a message like "Add a task to buy groceries"
4. See the chatbot response

---

## Quick Test Commands

Try these messages with the chatbot:

| Command | Expected Behavior |
|---------|-------------------|
| "Add task buy milk" | Creates task, confirms |
| "Show my tasks" | Lists all tasks |
| "Show high priority tasks" | Filters by priority |
| "Complete the milk task" | Marks task done |
| "Delete task 1" | Asks for confirmation |

---

## Troubleshooting

### "COHERE_API_KEY not set"
- Ensure `.env` file exists in `backend/` directory
- Restart the backend after adding the key

### "Could not validate credentials"
- JWT token expired - log in again
- Check BETTER_AUTH_SECRET matches between frontend and backend

### "AI service unavailable"
- Check Cohere API status at [https://status.cohere.com/](https://status.cohere.com/)
- Verify API key is valid and not rate-limited

### Tables not created
- Check database connection in `DATABASE_URL`
- Look for errors in backend startup logs

---

## Verification Checklist

- [ ] Backend starts without errors
- [ ] `curl /health` returns `{"status": "healthy"}`
- [ ] Chat endpoint returns response (not 401 or 500)
- [ ] Frontend loads chat page
- [ ] Can send message and receive response
- [ ] Task created via chat appears in task list
