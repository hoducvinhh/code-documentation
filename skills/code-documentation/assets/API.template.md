# API Reference: <PROJECT_NAME>

Base URL: `http://localhost:<PORT>/api/v1`

---

## Table of Contents

- [Authentication](#authentication)
- [Error Responses](#error-responses)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Resource Collection](#resource-collection)

---

## Authentication

All protected endpoints require an `Authorization` header containing a valid Bearer token:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

---

## Error Responses

Errors follow a consistent JSON format:

```json
{
  "error": "ErrorType",
  "message": "Detailed description of the error condition.",
  "status_code": 400
}
```

Common status codes:
- `400 Bad Request`: Invalid parameters or payload validation failed.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: Authenticated user lacks permission.
- `404 Not Found`: Requested resource does not exist.
- `500 Internal Server Error`: Unhandled server exception.

---

## Endpoints

### Health Check

Checks service uptime and connectivity.

- **URL**: `/health`
- **Method**: `GET`
- **Auth Required**: No

#### Response: `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2026-10-30T12:00:00Z"
}
```

---

### Resource Collection

#### List Resources

Retrieve a paginated list of resources.

- **URL**: `/<RESOURCES>`
- **Method**: `GET`
- **Auth Required**: Yes

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `page` | Integer | No | `1` | Page number |
| `limit` | Integer | No | `20` | Items per page (max 100) |

**Response: `200 OK`**
```json
{
  "data": [],
  "total": 0,
  "page": 1,
  "limit": 20
}
```

---

#### Create Resource

Create a new resource record.

- **URL**: `/<RESOURCES>`
- **Method**: `POST`
- **Auth Required**: Yes

**Request Body:**
```json
{
  "name": "Sample Name",
  "description": "Sample description"
}
```

**Response: `201 Created`**
```json
{
  "id": "res_12345",
  "name": "Sample Name",
  "description": "Sample description",
  "created_at": "2026-10-30T12:00:00Z"
}
```
