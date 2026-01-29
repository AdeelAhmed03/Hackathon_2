# Full-Stack Todo Application

A modern, full-stack todo application built with FastAPI backend and Next.js 16 frontend, featuring JWT authentication, SQLModel ORM, and Better Auth integration.

## Features

- **User Authentication**: Secure JWT-based authentication with Better Auth
- **Task Management**: Complete CRUD operations for todo tasks
- **Multi-User Support**: Each user has isolated data with proper security
- **Modern Tech Stack**: FastAPI, Next.js 16, SQLModel, Neon PostgreSQL
- **Container Support**: Docker Compose for easy local development

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLModel**: SQLAlchemy-based ORM with Pydantic integration
- **Better Auth**: Authentication and authorization
- **Alembic**: Database migrations
- **PostgreSQL**: Production-ready database

### Frontend
- **Next.js 16**: React framework with App Router
- **TailwindCSS**: Utility-first CSS framework
- **Better Auth**: Client-side authentication
- **React Hook Form**: Form management
- **Zod**: Schema validation

## Project Structure

```
todo-app/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── models/         # SQLModel database models
│   │   ├── services/       # Business logic
│   │   ├── api/           # API endpoints
│   │   ├── middleware/    # Authentication middleware
│   │   └── database/      # Database configuration
│   └── pyproject.toml
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   └── lib/          # Shared utilities
│   ├── package.json
│   └── next.config.js
├── shared/                # Shared types and utilities
├── specs/                # Feature specifications
└── docker-compose.yml    # Development environment
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional, for container deployment)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd todo-app
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Backend Setup**
   ```bash
   cd backend
   pip install -e .
   alembic upgrade head
   uvicorn src.main:app --reload
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

### Docker Development

```bash
docker-compose up
```

## Development

### Backend Development
- Run with hot reload: `uvicorn src.main:app --reload`
- Run tests: `pytest`
- Lint code: `ruff check src/`
- Type check: `mypy src/`

### Frontend Development
- Development server: `npm run dev`
- Build production: `npm run build`
- Lint code: `npm run lint`
- Type check: `npm run type-check`

## API Documentation

The backend API is automatically documented with OpenAPI/Swagger:
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication

The application uses JWT-based authentication with Better Auth:
- Users must sign up/sign in before accessing protected resources
- All API endpoints require valid JWT tokens
- User data is isolated per authenticated user

## Database

- **Local Development**: PostgreSQL via Docker
- **Production**: Neon Serverless PostgreSQL
- **Migrations**: Managed with Alembic

## Security

- JWT token-based authentication
- User data isolation
- Input validation with Pydantic
- SQL injection protection with SQLModel
- CORS configuration for frontend-backend communication

## Testing

- Backend: pytest with pytest-asyncio
- Frontend: Jest and React Testing Library (Phase 7)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository or contact the development team.