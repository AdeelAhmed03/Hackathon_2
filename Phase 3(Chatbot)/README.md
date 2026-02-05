# Full-Stack Todo Application with AI Chatbot

A modern, full-stack todo application built with FastAPI backend and Next.js 16 frontend, featuring JWT authentication, SQLModel ORM, Better Auth integration, and **AI-powered natural language task management**.

## 🌟 Features

### Core Features
- **User Authentication**: Secure JWT-based authentication with Better Auth
- **Task Management**: Complete CRUD operations for todo tasks
- **Multi-User Support**: Each user has isolated data with proper security
- **Modern Tech Stack**: FastAPI, Next.js 16, SQLModel, Neon PostgreSQL

### 🤖 AI Chatbot Features (Phase III)
- **Natural Language Processing**: Manage tasks using conversational language
- **Floating Chat Widget**: Always-accessible chat interface on every page
- **Intent Recognition**: Automatically understands user commands
- **Multi-Tool Execution**: Performs complex operations in a single request
- **Conversation History**: Maintains context across chat sessions
- **Real-time Responses**: Instant feedback with loading indicators
- **Tool Result Badges**: Visual confirmation of completed actions

### Advanced Todo Features
- **Priorities**: Low, Medium, High priority levels
- **Tags**: Multi-select tagging system for organization
- **Search**: Case-insensitive keyword search
- **Filtering**: Filter by tags, priorities, and status
- **Due Dates**: Timezone-aware datetime with relative display
- **Recurring Tasks**: Daily, weekly, monthly, yearly recurrence patterns
- **Visual Indicators**: Status badges and due date warnings

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLModel**: SQLAlchemy-based ORM with Pydantic integration
- **Cohere AI**: Large Language Model for natural language processing
- **Better Auth**: Authentication and authorization
- **Neon PostgreSQL**: Serverless PostgreSQL database
- **Pydantic v2**: Data validation and settings management

### Frontend
- **Next.js 16**: React framework with App Router
- **TailwindCSS**: Utility-first CSS framework
- **Framer Motion**: Animation library for smooth UI transitions
- **Better Auth**: Client-side authentication
- **React Hook Form**: Form management
- **Zod**: Schema validation
- **Lucide React**: Icon library

### AI Integration
- **Cohere Command R**: LLM for intent extraction and response generation
- **Custom Tool System**: Extensible tool framework for task operations
- **Stateless Chat**: No server-side session storage, database-backed history

## 📁 Project Structure

```
Phase 3(Chatbot)/
├── backend/                          # FastAPI backend
│   ├── src/
│   │   ├── models/                  # SQLModel database models
│   │   │   ├── user.py             # User model
│   │   │   ├── task.py             # Task model with advanced features
│   │   │   ├── tag.py              # Tag model
│   │   │   ├── conversation.py     # Chat conversation model
│   │   │   └── message.py          # Chat message model
│   │   ├── services/               # Business logic
│   │   │   ├── chat_service.py    # Cohere AI integration
│   │   │   └── tool_service.py    # Tool execution orchestration
│   │   ├── tools/                  # AI Tool definitions
│   │   │   ├── definitions.py     # Tool schemas for Cohere
│   │   │   ├── add_task.py        # Create task tool
│   │   │   ├── list_tasks.py      # List tasks tool
│   │   │   ├── complete_task.py   # Complete task tool
│   │   │   ├── update_task.py     # Update task tool
│   │   │   └── delete_task.py     # Delete task tool
│   │   ├── api/                   # API endpoints
│   │   │   ├── auth.py           # Authentication routes
│   │   │   ├── tasks.py          # Task CRUD routes
│   │   │   └── chat.py           # AI chatbot routes
│   │   ├── middleware/            # Authentication middleware
│   │   └── database/             # Database configuration
│   └── requirements.txt
├── frontend/                        # Next.js frontend
│   ├── src/
│   │   ├── app/                   # App Router pages
│   │   │   ├── chat/             # Dedicated chat page
│   │   │   ├── dashboard/        # Main dashboard
│   │   │   ├── sign-in/          # Sign in page
│   │   │   └── sign-up/          # Sign up page
│   │   ├── components/           # React components
│   │   │   ├── chat/            # Chat UI components
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   └── MessageInput.tsx
│   │   │   └── common/          # Shared components
│   │   │       ├── FloatingChatButton.tsx  # AI chat widget
│   │   │       ├── Navbar.tsx
│   │   │       └── Footer.tsx
│   │   ├── hooks/               # Custom React hooks
│   │   │   └── useChat.ts      # Chat state management
│   │   ├── types/              # TypeScript definitions
│   │   │   └── chat.ts        # Chat-related types
│   │   └── lib/               # Shared utilities
│   ├── package.json
│   └── next.config.js
├── specs/                        # Feature specifications
│   └── 1-ai-chatbot/           # AI chatbot specs
└── .env                        # Environment variables
```

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Node.js 18+
- Cohere API Key ([Get one free](https://dashboard.cohere.com/))
- PostgreSQL database (or use Neon serverless)

### Environment Setup

#### Backend (.env)
```env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require

# Authentication (must match frontend)
BETTER_AUTH_SECRET=your-secret-key-here

# Cohere AI API (Phase III - Required)
COHERE_API_KEY=your-cohere-api-key-here

# CORS
FRONTEND_URL=http://localhost:3000

# Server
PORT=8000
```

#### Frontend (.env)
```env
# Backend API URL
NEXT_PUBLIC_API_BASE_URL=https://adeelahmed01-todo-chatbot.hf.space
BACKEND_API_URL=https://adeelahmed01-todo-chatbot.hf.space

# Frontend URL (for Better Auth)
NEXT_PUBLIC_BASE_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here

# Cohere AI API (Phase III)
COHERE_API_KEY=your-cohere-api-key-here
```

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Phase 3(Chatbot)"
   ```

2. **Generate Better Auth Secret**
   ```bash
   openssl rand -base64 32
   ```
   Use this in both frontend and backend `.env` files.

3. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn src.main:app --reload --port 8000
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🤖 AI Chatbot Usage

### Natural Language Commands

The AI chatbot understands natural language and can perform various task operations:

#### Creating Tasks
- "Add a task to buy groceries"
- "Create a new task: Call dentist tomorrow"
- "Remind me to submit the report by Friday"
- "Add buy milk with high priority"

#### Listing Tasks
- "Show my tasks"
- "What's on my list?"
- "List all my high priority tasks"
- "Show me tasks due today"

#### Completing Tasks
- "Mark buy milk as done"
- "Complete the groceries task"
- "I finished the report task"

#### Updating Tasks
- "Change the title of task 5 to 'Buy vegetables'"
- "Update task priority to high"
- "Set due date for task 3 to tomorrow"

#### Deleting Tasks
- "Delete the buy milk task"
- "Remove task 7"
- "Delete all completed tasks"

### Floating Chat Widget

The floating chat button appears on all pages (except `/chat`) and provides:
- **Instant Access**: Click the blue/purple button in bottom-right
- **Minimize/Expand**: Collapse to header only when needed
- **Quick Suggestions**: Pre-filled prompts for common actions
- **Real-time Feedback**: Loading indicators and tool result badges
- **Conversation Persistence**: History maintained across sessions

### Chat Features

- **Contextual Understanding**: Maintains conversation context
- **Multi-turn Conversations**: Ask follow-up questions
- **Error Handling**: Clear error messages with retry options
- **Tool Execution Feedback**: Visual badges showing completed actions
- **Auto-scroll**: Always shows the latest message
- **Responsive Design**: Works on desktop and mobile

## 🏗️ Architecture

### AI Chatbot Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FloatingChatButton / ChatContainer                  │  │
│  │  - User input                                        │  │
│  │  - Message display                                   │  │
│  │  - Tool result badges                                │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │ POST /api/v1/chat                    │
└─────────────────────┼───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     Backend                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Chat API (chat.py)                                  │  │
│  │  - Receive user message                              │  │
│  │  - Load conversation history                         │  │
│  │  - Format for Cohere                                 │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Chat Service (chat_service.py)                      │  │
│  │  - Call Cohere Command R                            │  │
│  │  - Extract tool calls                                │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Tool Service (tool_service.py)                      │  │
│  │  - Execute tools (add/list/complete/update/delete)  │  │
│  │  - Database operations                               │  │
│  │  - Return results                                    │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Database (Neon PostgreSQL)                          │  │
│  │  - Conversations                                     │  │
│  │  - Messages                                          │  │
│  │  - Tasks                                             │  │
│  │  - Users                                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Tool System

Each tool is defined with:
- **Name**: Unique identifier (e.g., `add_task`)
- **Description**: What the tool does
- **Parameters**: Schema for input validation
- **Implementation**: Python function with database access

Available Tools:
1. **add_task**: Create new tasks with title, description, priority, tags, due date
2. **list_tasks**: Query tasks with filters (status, priority, tags, search)
3. **complete_task**: Mark tasks as complete
4. **update_task**: Modify task properties
5. **delete_task**: Remove tasks

## 🔒 Security

- **JWT Token Authentication**: All requests require valid tokens
- **User Data Isolation**: Users can only access their own data
- **Input Validation**: Pydantic schemas for all requests
- **SQL Injection Protection**: SQLModel ORM with parameterized queries
- **CORS Configuration**: Controlled frontend-backend communication
- **Environment Variables**: Sensitive data stored securely
- **Better Auth Secret**: Cryptographically secure key generation

## 📊 Database Schema

### Core Tables
- **users**: User accounts with email and hashed passwords
- **tasks**: Todo items with priorities, tags, due dates, recurrence
- **tags**: Global tag definitions
- **tasktaglink**: Many-to-many relationship for task tags

### Chat Tables (Phase III)
- **conversations**: Chat sessions per user
- **messages**: Individual messages with role (user/assistant) and tool calls

## 🎨 UI Components

### Chat Components
- **FloatingChatButton**: Persistent chat widget
- **ChatContainer**: Full-page chat interface
- **ChatMessage**: Message bubble with tool results
- **MessageList**: Animated message list with auto-scroll
- **MessageInput**: Text input with send button

### Features
- Gradient backgrounds (blue to purple)
- Smooth animations with Framer Motion
- Dark mode support
- Responsive design
- Loading indicators
- Error handling with dismissible messages

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest -v
```

### Frontend Testing
```bash
cd frontend
npm run test
```

### E2E Testing
```bash
python test_e2e_chatbot.py
```

## 📝 Development Workflow

1. **Feature Specification**: Document in `specs/` directory
2. **Backend Implementation**: Add models, services, API routes
3. **Tool Definition**: Create tool schema and implementation
4. **Frontend Integration**: Build UI components and hooks
5. **Testing**: Write unit and integration tests
6. **Documentation**: Update README and API docs

## 🌐 Deployment

### Backend (Hugging Face Spaces)
- Deployed at: `https://adeelahmed01-todo-chatbot.hf.space`
- Uses Neon PostgreSQL
- Environment variables configured in Space settings

### Frontend (Vercel)
- Next.js optimized build
- Environment variables in Vercel dashboard
- Automatic deployments from git

## 📚 API Documentation

### Chat Endpoints

#### POST /api/v1/chat
Send a message to the AI chatbot.

**Request:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": null
}
```

**Response:**
```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "I've created a task for you to buy groceries."
  },
  "tool_executed": true,
  "tool_results": [
    {
      "tool_name": "add_task",
      "success": true,
      "result": "Task created successfully"
    }
  ]
}
```

#### GET /api/v1/chat/conversations/{conversation_id}
Retrieve conversation history.

### Task Endpoints
- `GET /api/v1/tasks/`: List all tasks
- `POST /api/v1/tasks/`: Create a task
- `GET /api/v1/tasks/{id}`: Get task details
- `PUT /api/v1/tasks/{id}`: Update a task
- `DELETE /api/v1/tasks/{id}`: Delete a task
- `PATCH /api/v1/tasks/{id}/complete`: Mark as complete

Full API documentation: http://localhost:8000/docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Cohere AI**: Natural language processing
- **Neon**: Serverless PostgreSQL
- **Better Auth**: Authentication system
- **FastAPI**: Backend framework
- **Next.js**: Frontend framework
- **Vercel**: Frontend hosting
- **Hugging Face**: Backend hosting

## 💬 Support

For issues and questions:
- Create an issue on GitHub
- Contact: adeelahmed@example.com
- Documentation: Check `/specs` directory for detailed specifications

## 🗺️ Roadmap

### Phase IV - Voice Integration
- Voice input for chat
- Text-to-speech responses

### Phase V - Advanced AI
- Task suggestions based on patterns
- Smart scheduling
- Priority recommendations

### Phase VI - Collaboration
- Share tasks with other users
- Team workspaces
- Real-time updates

---

**Built with ❤️ by Adeel Ahmed**

🌟 Star this repository if you find it helpful!
