# API Documentation

This document provides comprehensive information about the API endpoints available in the Todo application.

## Base URL

All API endpoints are prefixed with `/api/v1`.

## Authentication

Most endpoints require authentication. Include an Authorization header with a valid JWT token:

```
Authorization: Bearer <jwt-token>
```

## Response Format

Successful responses return data in the following format:

```json
{
  "data": {...},
  "success": true,
  "message": "Optional message"
}
```

Error responses return:

```json
{
  "detail": "Error message",
  "success": false
}
```

## Endpoints

### Authentication

#### Register User
- **Endpoint**: `POST /auth/register`
- **Description**: Register a new user account
- **Request Body**:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "secure_password"
}
```
- **Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```
- **Errors**:
  - 400: Email already registered
  - 422: Invalid input data

#### Login User
- **Endpoint**: `POST /auth/login`
- **Description**: Authenticate user and return JWT token
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```
- **Response**:
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```
- **Errors**:
  - 401: Invalid email or password

### Tasks

#### Get All Tasks
- **Endpoint**: `GET /tasks`
- **Description**: Retrieve all tasks for the authenticated user
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum number of records to return (default: 100)
- **Response**:
```json
[
  {
    "id": 1,
    "title": "Sample Task",
    "description": "Task description",
    "status": "pending",
    "priority": 3,
    "owner_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "completed_at": null
  }
]
```
- **Errors**:
  - 401: Unauthorized

#### Create Task
- **Endpoint**: `POST /tasks`
- **Description**: Create a new task for the authenticated user
- **Request Body**:
```json
{
  "title": "New Task",
  "description": "Task description",
  "priority": 3
}
```
- **Response**:
```json
{
  "id": 1,
  "title": "New Task",
  "description": "Task description",
  "status": "pending",
  "priority": 3,
  "owner_id": 1,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "completed_at": null
}
```
- **Errors**:
  - 401: Unauthorized

#### Get Task
- **Endpoint**: `GET /tasks/{id}`
- **Description**: Retrieve a specific task by ID
- **Path Parameter**: `id` - Task ID
- **Response**:
```json
{
  "id": 1,
  "title": "Sample Task",
  "description": "Task description",
  "status": "pending",
  "priority": 3,
  "owner_id": 1,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "completed_at": null
}
```
- **Errors**:
  - 401: Unauthorized
  - 404: Task not found

#### Update Task
- **Endpoint**: `PUT /tasks/{id}`
- **Description**: Update a specific task by ID
- **Path Parameter**: `id` - Task ID
- **Request Body** (partial updates allowed):
```json
{
  "title": "Updated Task Title",
  "description": "Updated description",
  "status": "completed",
  "priority": 5
}
```
- **Response**:
```json
{
  "id": 1,
  "title": "Updated Task Title",
  "description": "Updated description",
  "status": "completed",
  "priority": 5,
  "owner_id": 1,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z",
  "completed_at": "2023-01-02T00:00:00Z"
}
```
- **Errors**:
  - 401: Unauthorized
  - 404: Task not found

#### Delete Task
- **Endpoint**: `DELETE /tasks/{id}`
- **Description**: Delete a specific task by ID
- **Path Parameter**: `id` - Task ID
- **Response**:
```json
{
  "message": "Task deleted successfully"
}
```
- **Errors**:
  - 401: Unauthorized
  - 404: Task not found

#### Toggle Task Status
- **Endpoint**: `PATCH /tasks/{id}/toggle-status`
- **Description**: Toggle the completion status of a task
- **Path Parameter**: `id` - Task ID
- **Response**:
```json
{
  "id": 1,
  "title": "Sample Task",
  "description": "Task description",
  "status": "completed",
  "priority": 3,
  "owner_id": 1,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z",
  "completed_at": "2023-01-02T00:00:00Z"
}
```
- **Errors**:
  - 401: Unauthorized
  - 404: Task not found

## Error Codes

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource does not exist
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Rate Limiting

The API implements rate limiting to prevent abuse. Limits may vary by endpoint and user role.

## Security

- All sensitive data is encrypted in transit using HTTPS
- Authentication tokens expire after 30 minutes
- User data isolation ensures users can only access their own resources
- Input validation prevents injection attacks
- Request sanitization protects against XSS attacks