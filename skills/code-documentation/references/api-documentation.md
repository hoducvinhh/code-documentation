# API Documentation Guide

## Overview

Accurate API documentation (`API.md`) is essential for developers integrating with or maintaining a service. Every endpoint documented must reflect the real route handlers, parameter requirements, authentication policies, and response schemas.

---

## 1. REST Endpoint Specification Standard

For every HTTP endpoint, document:

1. **Method & Path**: `POST /api/v1/auth/login`
2. **Summary**: Brief description of the endpoint's purpose.
3. **Authentication**: Required auth scheme (e.g., `None`, `Bearer JWT`, `API Key`).
4. **Request Parameters**:
   - Path parameters (e.g. `/users/:id`)
   - Query parameters (e.g. `?limit=10&page=1`)
   - Request Headers (e.g. `Content-Type: application/json`)
5. **Request Body**: JSON schema or example payload with field types and validation constraints.
6. **Responses**:
   - Status codes (`200`, `201`, `400`, `401`, `404`, `500`).
   - JSON response payload examples.

---

## 2. Endpoint Template Example

### `POST /api/v1/users`

Creates a new user profile.

- **Authentication**: `Bearer <token>` (Role: `admin`)
- **Headers**:
  - `Content-Type`: `application/json`

#### Request Body

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `email` | `string` | Yes | Valid email address |
| `name` | `string` | Yes | User's full display name |
| `role` | `string` | No | Default: `member`. Allowed: `member`, `admin` |

```json
{
  "email": "user@example.com",
  "name": "Jane Doe",
  "role": "member"
}
```

#### Responses

- **`201 Created`**: User successfully registered.
  ```json
  {
    "id": "usr_99a8b7c6",
    "email": "user@example.com",
    "name": "Jane Doe",
    "role": "member",
    "created_at": "2026-10-30T12:00:00Z"
  }
  ```
- **`400 Bad Request`**: Validation error.
  ```json
  {
    "error": "ValidationError",
    "message": "Field 'email' must be a valid email address"
  }
  ```
- **`409 Conflict`**: Email already exists.

---

## 3. Extracting Endpoints from Code

- **Express**: Search for `router.get(...)`, `router.post(...)`, `app.use('/api', ...)`.
- **FastAPI**: Search for `@app.get(...)`, `@router.post(...)`, response models, and status codes.
- **NestJS**: Inspect `@Controller('path')` and `@Get()`, `@Post()`, `@Body()`.
