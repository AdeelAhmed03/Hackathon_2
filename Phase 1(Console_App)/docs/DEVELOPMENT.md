# Development Guide

This document provides comprehensive information about the full-stack todo application development process.

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
│   │   ├── contexts/     # React contexts
│   │   ├── hooks/        # Custom hooks
│   │   ├── lib/          # Shared utilities
│   │   └── types/        # TypeScript types
│   ├── package.json
│   └── next.config.js
├── shared/                # Shared types and utilities
├── specs/                # Feature specifications
├── docs/                 # Documentation
└── docker-compose.yml    # Development environment
```

## Backend Development

### Database Models

The application uses SQLModel for database modeling:

- **User Model**: Stores user information with email, name, password hash, and role
- **Task Model**: Stores task information with title, description, status, priority, and owner reference

### Authentication

The application implements JWT-based authentication:

1. User credentials are verified against the database
2. A JWT token is generated and returned upon successful login
3. All protected endpoints require a valid JWT token in the Authorization header
4. User data isolation is enforced by checking the owner_id for each request

### API Endpoints

#### Authentication Endpoints
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token

#### Task Endpoints
- `GET /api/v1/tasks` - Get all tasks for the current user
- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks/{id}` - Get a specific task
- `PUT /api/v1/tasks/{id}` - Update a specific task
- `DELETE /api/v1/tasks/{id}` - Delete a specific task
- `PATCH /api/v1/tasks/{id}/toggle-status` - Toggle task completion status

## Frontend Development

### Architecture

The frontend follows a component-based architecture with:

- **Layout Components**: Page structure and navigation
- **Feature Components**: Task management functionality
- **UI Components**: Reusable elements like buttons, forms, etc.
- **Context Providers**: Global state management

### State Management

The application uses React Context for state management:

- **Auth Context**: Manages user authentication state
- **Notification Context**: Handles user notifications
- **API Client**: Centralized API request management

### Components

#### Task Components
- **TaskList**: Displays all tasks with CRUD operations
- **TaskItem**: Individual task display and management
- **TaskForm**: Task creation and editing form
- **TaskStats**: Task statistics and analytics

#### Authentication Components
- **SignInForm**: User sign-in functionality
- **SignUpForm**: User registration functionality
- **AuthProvider**: Authentication context provider

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/todo_app
BETTER_AUTH_SECRET=your-secret-key-here
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

## Development Commands

### Backend
```bash
# Install dependencies
cd backend
pip install -e .

# Run development server
uvicorn src.main:app --reload

# Run tests
pytest
```

### Frontend
```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Docker
```bash
# Start development environment
docker-compose up

# Start specific services
docker-compose up postgresql  # Database only
```

## Security Features

### Authentication
- JWT tokens with expiration
- Secure password hashing with bcrypt
- Session management

### Authorization
- User data isolation (users can only access their own tasks)
- Role-based access control
- Input validation and sanitization

### API Security
- Rate limiting (to be implemented)
- CORS configuration
- Input validation with Pydantic
- SQL injection protection with SQLModel

## Testing Strategy

### Backend Testing
- Unit tests for models and services
- Integration tests for API endpoints
- Authentication flow tests
- Data isolation tests

### Frontend Testing
- Component unit tests
- Integration tests for user flows
- API integration tests
- End-to-end tests (to be implemented)

## Deployment

### Backend
- Containerized with Docker
- Environment-specific configurations
- Health checks and monitoring endpoints

### Frontend
- Static site generation
- Environment-specific API endpoints
- Asset optimization

## Troubleshooting

### Common Issues

#### Database Connection
- Ensure PostgreSQL is running
- Verify DATABASE_URL in environment variables
- Check database migrations are applied

#### Authentication Issues
- Verify JWT secret is consistent between services
- Check token expiration times
- Ensure HTTPS is used in production

#### API Communication
- Verify API endpoints are correct
- Check CORS configuration
- Ensure proper authentication headers are sent

### Debugging Tips

#### Frontend
- Check browser console for JavaScript errors
- Verify network requests in developer tools
- Use React Developer Tools for component inspection

#### Backend
- Check server logs for error messages
- Verify database connection status
- Use debugging tools like pdb for Python debugging

## Performance Considerations

### Backend
- Database indexing on frequently queried fields
- Connection pooling
- Caching strategies (to be implemented)
- Asynchronous request handling

### Frontend
- Component lazy loading
- API request optimization
- Client-side caching (to be implemented)
- Bundle size optimization

## Future Enhancements

### Planned Features
- Real-time updates with WebSockets
- Task sharing between users
- Advanced filtering and search
- Task categorization and tags
- Email notifications
- Mobile app support

### Improvements
- Enhanced security measures
- Performance optimization
- Comprehensive testing coverage
- Better error handling
- Accessibility improvements
- Internationalization support