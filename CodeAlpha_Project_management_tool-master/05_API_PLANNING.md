# STEP 5: API PLANNING

## 1. API Architecture & Structure
*   **Architecture:** RESTful design for standard CRUD operations and webhooks. (GraphQL may be used internally for complex frontend views, but the public-facing and core API is REST).
*   **Versioning:** URI-based versioning (e.g., `/api/v1/`).
*   **Response Format:** Standard JSON envelope for predictable parsing.
    ```json
    {
      "success": true,
      "data": { ... },
      "meta": { "page": 1, "total": 50 } // optional pagination
    }
    ```
    Error format:
    ```json
    {
      "success": false,
      "error": { "code": "VALIDATION_FAILED", "message": "Invalid email" }
    }
    ```

## 2. Authentication & Authorization Flows

### Authentication Flow (Login)
1. Client POSTs credentials to `/api/v1/auth/login`.
2. Server verifies password hash against DB.
3. Server generates a short-lived `access_token` (JWT, 15m) and a cryptographically secure, opaque `refresh_token` (7d).
4. Server returns `access_token` in JSON and sets `refresh_token` as a secure, HTTP-only cookie.

### JWT & Refresh Token Flow
1. Client attaches `access_token` to the `Authorization: Bearer <token>` header for all requests.
2. When the `access_token` expires, the API returns `401 Unauthorized`.
3. Client silently calls `/api/v1/auth/refresh` (which sends the HTTP-only refresh cookie).
4. Server verifies the refresh token against the Redis session store. If valid, issues a new `access_token`.
5. If the refresh token is expired or revoked, Client receives `403 Forbidden` and forces a logout.

### Permission Flow
1. Request arrives with valid `access_token`.
2. Middleware extracts `user_id`.
3. Middleware queries Redis/DB to determine user's role in the requested `workspace_id`.
4. ABAC engine checks if the Role has permission for the specific action (e.g., `UPDATE_TASK`). If not, returns `403 Forbidden`.

## 3. Core REST Endpoint List

### Auth & Users
*   `POST /api/v1/auth/register` - Create account
*   `POST /api/v1/auth/login` - Authenticate
*   `POST /api/v1/auth/refresh` - Rotate tokens
*   `GET /api/v1/users/me` - Get current user profile

### Workspaces
*   `GET /api/v1/workspaces` - List user's workspaces
*   `POST /api/v1/workspaces` - Create workspace
*   `GET /api/v1/workspaces/:workspaceId/members` - List workspace members

### Projects
*   `GET /api/v1/workspaces/:workspaceId/projects` - List projects
*   `POST /api/v1/workspaces/:workspaceId/projects` - Create project
*   `GET /api/v1/projects/:projectId` - Get project details

### Tasks
*   `GET /api/v1/projects/:projectId/tasks` - List tasks (supports `?status=DONE&sort=-created_at`)
*   `POST /api/v1/projects/:projectId/tasks` - Create task
*   `PATCH /api/v1/tasks/:taskId` - Update task (title, status, assignee)
*   `DELETE /api/v1/tasks/:taskId` - Soft delete task

### Comments & Collaboration
*   `GET /api/v1/tasks/:taskId/comments` - List comments
*   `POST /api/v1/tasks/:taskId/comments` - Add comment

### AI & 3D Workspace
*   `POST /api/v1/ai/ask` - Send a query to the AI Assistant context engine
*   `POST /api/v1/ai/generate-subtasks` - Auto-generate task breakdown
*   `GET /api/v1/workspaces/:workspaceId/3d-graph-data` - Fetch optimized node/edge JSON payload for WebGL rendering.
