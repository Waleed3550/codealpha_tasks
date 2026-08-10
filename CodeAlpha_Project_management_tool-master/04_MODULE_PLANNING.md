# STEP 4: MODULE PLANNING

The platform is divided into the following highly cohesive modules.

## 1. Authentication & Authorization
*   **Authentication:** Handles user registration, login, 2FA/MFA, password resets, and SSO integrations (SAML, Google). Issues JWTs and manages Redis sessions.
*   **Authorization (IAM):** Evaluates whether a user can perform an action. Implements strict RBAC (Roles: Owner, Admin, Member, Guest) and ABAC (checking attributes like "Is Assignee").

## 2. Tenancy & Hierarchy
*   **Organizations:** Top-level billing and global security policy container.
*   **Workspaces:** Distinct operational areas within an Organization. Data is strictly isolated between workspaces.
*   **Teams:** Groupings of Users within a workspace to allow bulk assignment and permission mapping.

## 3. Work Management
*   **Projects:** Containers for tasks. Can be viewed as Boards, Lists, Gantt charts, etc.
*   **Tasks:** The fundamental work unit. Contains titles, descriptions (rich text), assignees, statuses, custom fields, and tags.
*   **Subtasks:** Nestable tasks. Supports infinite nesting (trees), though UI may cap display depth for usability.
*   **Dependencies:** Tracks relationships (Blocking, Blocked By, Relates To) to calculate Gantt critical paths and alert users of cascading delays.

## 4. Communication
*   **Comments:** Threaded conversations on tasks and documents. Supports rich text, attachments, and emoji reactions.
*   **Notifications:** The inbox system. Aggregates @mentions, task assignments, and dependency alerts. Users can mark as read/unread or snooze.
*   **Realtime Collaboration:** Handles multiplayer presence (who is viewing what), typing indicators, and CRDT-based rich-text block editing for Notion-like docs.

## 5. Planning & Visualization
*   **Calendar:** Visualizes tasks by due date or custom date fields. Supports drag-and-drop rescheduling.
*   **3D Workspace:** A WebGL interactive module rendering project architectures, team graphs, and bottlenecks in a spatial 3D UI for high-level management overview.

## 6. Insights
*   **Reports:** Generates burn-down charts, cumulative flow diagrams, and sprint velocity metrics.
*   **Analytics:** Customizable dashboards where users can pin widgets tracking custom KPIs (e.g., "Bugs reported this week").

## 7. Platform Features
*   **Files:** Handles uploading, scanning for viruses, CDN caching, and versioning of attachments on tasks and docs.
*   **Settings & Profile:** User preferences (Dark/Light mode, timezone, notification channels) and Workspace preferences (custom statuses, billing).
*   **Admin Panel:** Super-admin view for Organization owners to audit security logs, manage billing, and enforce SSO.
*   **AI Assistant:** The context-aware copilot. Integrates via RAG to answer queries like "What is the status of the Backend rewrite?", auto-generates task sub-steps, and predicts project risks based on historical velocity.
