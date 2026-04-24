# API Reference

This document only lists the endpoints that are clearly present in the current codebase.

## Web Assistant Runtime

The desktop/web stack currently runs as separate local services:

- Web assistant app: `http://localhost:5000`
- Auth server: `http://localhost:7000`
- Central AI server: `http://localhost:8000`

## Web Assistant App

Source: `web-assistant/app.py`

### `GET /health`

Basic health check for the Flask app.

Example response:

```json
{
  "status": "healthy",
  "service": "web-assistant",
  "version": "1.0.0",
  "components": {
    "ai_server": "online",
    "auth_server": "online",
    "federated_learning": "available"
  }
}
```

### `GET /api/status`

High-level status summary for the web assistant app.

### `POST /chat`

Forwards chat requests to the central AI server.

### `POST /auth/login`

Forwards login requests to the auth server.

## Auth Server

Source: `web-assistant/services/auth/auth_server.py`

### `POST /login`

Validates username and password against the MySQL `users` table.

Request body:

```json
{
  "username": "testuser",
  "password": "test123"
}
```

Success response:

```json
{
  "status": "ok",
  "user_id": 1,
  "username": "testuser"
}
```

### `POST /validate`

Checks whether a username exists and returns the stable numeric `user_id`.

### `GET /health`

Reports auth server status and MySQL connection status.

## Central AI Server

Source: `web-assistant/services/central_server/ai_server.py`

### `POST /chat`

Main local AI chat endpoint.

Request body:

```json
{
  "user_id": 1,
  "message": "Hello"
}
```

Notes:

- `user_id` must be numeric.
- Memory is stored per user.
- The server routes by topic and uses local Ollama-backed inference.

### `GET /health`

Simple health check for the AI service.

## PHP Frontend Notes

The PHP frontend in `web-assistant/frontend/php/` talks to these local services directly.

Important client-side integrations:

- `loginPage.php` calls `http://localhost:7000/login`
- `aiAssistant.php` calls `http://localhost:8000/chat`
- Notes and reminders are file-backed per user in the PHP frontend folder

## Not Documented Here

This file intentionally does not list speculative or unfinished endpoints.

If an endpoint is not clearly present in the current source, it is omitted from this document.

### Games

#### List Games
```
GET /api/games
```

Get list of available interactive games.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "game_id": "game_1",
      "name": "Memory Challenge",
      "description": "Test your memory with increasingly difficult patterns",
      "duration_minutes": 10,
      "difficulty": "medium"
    },
    {
      "game_id": "game_2",
      "name": "Logic Puzzles",
      "description": "Solve logical puzzles to keep your mind sharp",
      "duration_minutes": 15,
      "difficulty": "hard"
    }
  ]
}
```

#### Start Game
```
POST /api/games/{game_id}/start
```

Start a game session.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "session_id": "session_xyz",
    "game_id": "game_1",
    "started_at": "2026-04-01T12:05:00Z",
    "first_challenge": "Pattern: [1, 2, 3, 5, 8, ...] - What's next?"
  }
}
```

#### Submit Game Answer
```
POST /api/games/{session_id}/answer
```

Submit an answer to a game challenge.

**Request Body:**
```json
{
  "answer": "13"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "correct": true,
    "score": 100,
    "next_challenge": "Pattern: [2, 4, 8, 16, ...] - What's next?",
    "level": 2
  }
}
```

#### End Game
```
POST /api/games/{session_id}/end
```

End a game session and get final score.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "final_score": 850,
    "duration_seconds": 600,
    "challenges_completed": 8,
    "accuracy": 87.5
  }
}
```

### Knowledge Base

#### Query Knowledge
```
GET /api/knowledge/search
```

Search the shared knowledge base.

**Query Parameters:**
- `q` - Search query
- `category` - Filter by category (tutorials, procedures, reference)

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "doc_id": "doc_1",
      "title": "Spectrometer Calibration Procedure",
      "category": "procedures",
      "relevance": 0.95,
      "preview": "To calibrate the spectrometer..."
    }
  ]
}
```

#### Get Knowledge Document
```
GET /api/knowledge/{doc_id}
```

Retrieve a full knowledge document.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "doc_id": "doc_1",
    "title": "Spectrometer Calibration Procedure",
    "category": "procedures",
    "content": "1. Turn on the device...",
    "last_updated": "2025-12-15T00:00:00Z"
  }
}
```

### Tutorials

#### List Tutorials
```
GET /api/tutorials
```

List available tutorial content.

**Query Parameters:**
- `category` - Filter by topic
- `difficulty` - Filter by difficulty level

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "tutorial_id": "tut_1",
      "title": "Zero-G Movement Basics",
      "category": "training",
      "duration_minutes": 15,
      "format": "video",
      "available_offline": true
    }
  ]
}
```

#### Play Tutorial
```
POST /api/tutorials/{tutorial_id}/play
```

Start playing a tutorial.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "tutorial_id": "tut_1",
    "player_url": "/media/tutorials/zero_g_basics.mp4",
    "duration_seconds": 900,
    "has_captions": true
  }
}
```

---

## Error Responses

### Example Error Response

```json
{
  "status": "error",
  "error_code": "INVALID_REQUEST",
  "message": "Missing required parameter: query",
  "timestamp": "2026-04-01T12:00:00Z"
}
```

### Common Error Codes

- `INVALID_REQUEST` - Malformed request
- `UNAUTHORIZED` - Missing or invalid token
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource already exists
- `RATE_LIMITED` - Too many requests
- `SERVER_ERROR` - Internal server error

---

## Rate Limiting

API endpoints are rate limited:
- **Authenticated Requests**: 100 requests per minute
- **Unauthenticated Requests**: 10 requests per minute

Rate limit info in response headers:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp of reset time

---

## Webhooks

Both services support webhooks for event updates:

```
POST /api/webhooks/subscribe
```

**Request Body:**
```json
{
  "event": "task.completed",
  "url": "https://your-server.com/webhook",
  "secret": "webhook_secret_key"
}
```

### Supported Events

**Web Assistant:**
- `task.created`
- `task.updated`
- `task.completed`
- `note.created`
- `ai.response_ready`

**Pi Robot:**
- `query.received`
- `game.started`
- `game.completed`
- `tutorial.started`
