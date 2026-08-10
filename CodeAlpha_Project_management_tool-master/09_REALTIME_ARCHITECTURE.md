# STEP 9: REALTIME ARCHITECTURE

## 1. Core Architecture (Django Channels & Redis)
Given the enterprise scale and the requirement for robust backend integration, the real-time layer will be powered by **Django Channels** running on an ASGI server (like Daphne or Uvicorn). 
*   **Redis as the Channel Layer:** Redis will serve as the high-speed pub/sub backplane. This allows multiple Django ASGI instances to communicate. If User A is connected to Node 1 and User B is connected to Node 2, a message sent to a specific "Channel Group" will seamlessly route through Redis to reach both users.

## 2. Realtime Features & Flows

### Presence System & Connection Management
*   **Heartbeat (Ping/Pong):** The Next.js frontend sends a WebSocket `ping` every 30 seconds. The server responds with `pong`. If missed, the connection is assumed dead.
*   **Presence Groups:** When a user opens a project or task, they subscribe to a specific group (e.g., `task_123_presence`). Redis tracks active connections. The UI displays avatar bubbles showing exactly who is viewing the document right now.
*   **Disconnects:** `disconnect()` handlers in the Django Consumer explicitly remove users from Presence groups and broadcast an "offline" event.

### Typing Indicators
*   When a user types in a comment box or block editor, a lightweight WebSocket event `{"action": "typing", "user_id": "xyz", "status": true}` is fired to the `task_123` group.
*   The frontend debounces this event and displays "User X is typing..." for 3 seconds unless renewed.

### Realtime Notifications & Task Updates
*   **Django Signals Integration:** When a Task is updated in the PostgreSQL database (e.g., via a standard REST API call), a `post_save` Django signal is triggered.
*   This signal pushes an event to the corresponding Channel Group (e.g., `project_456_updates`).
*   The frontend receives the JSON payload: `{"type": "task.updated", "data": {...}}` and uses React Query's `setQueryData` to optimistically and instantly update the Kanban board or 3D workspace without requiring a full page refresh.

### Realtime Comments & Collaborative Editing
*   **Comments:** New comments are broadcast immediately to all users in the task group.
*   **Rich Text/Block Editing:** For Notion-style collaborative editing, Django Channels will act as the signaling server for a CRDT algorithm (like Yjs). The server will broadcast delta updates (`Uint8Array` binary payloads) between clients to ensure conflict-free merges of text blocks.
