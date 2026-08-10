# STEP 6: FRONTEND PLANNING

## 1. Page Structure & Route Map (Next.js App Router)

*   **Public Routes**
    *   `/` - Landing Page (Features 3D Hero section)
    *   `/pricing` - Pricing & Plans
*   **Authentication Routes**
    *   `/login` - Login Form
    *   `/register` - Signup Form
    *   `/forgot-password` - Password Reset
*   **App Routes (Protected - under `/(app)`)**
    *   `/w/[workspaceId]` - **Dashboard:** The main workspace overview (Recent Activity, Assigned to Me).
    *   `/w/[workspaceId]/projects` - **Projects List:** Directory of all projects.
    *   `/w/[workspaceId]/p/[projectId]` - **Project View:** Defaults to Kanban or List based on user preference.
    *   `/w/[workspaceId]/p/[projectId]/task/[taskId]` - **Task Details (Modal/Drawer or Page):** Full task view with comments, subtasks, and files.
    *   `/w/[workspaceId]/calendar` - **Calendar:** Global workspace calendar view.
    *   `/w/[workspaceId]/reports` - **Reports/Analytics:** Sprint velocity, burn-down charts.
    *   `/w/[workspaceId]/notifications` - **Notifications:** Dedicated inbox page.
    *   `/settings/profile` - **Profile:** User-specific settings.
    *   `/w/[workspaceId]/settings` - **Workspace Settings:** Org management, members, billing.
    *   `/admin` - **Admin Panel:** Super-admin organization overview.

## 2. Navigation Flow

*   **Global Sidebar (Left):** Context-aware based on the active Workspace. Contains links to Dashboard, Projects (expandable list), Notifications (with badge), and Settings.
*   **Top Navbar:** Search Bar (Cmd/Ctrl + K to open command palette), Quick Add Button (+), AI Assistant Toggle, and User Avatar/Profile menu.
*   **Project Sub-nav:** When inside a Project, a sub-navigation bar appears for switching between Views (List, Kanban, Gantt, 3D View).

## 3. Responsive Layout Strategy

*   **Desktop (1024px+):** Full Sidebar + Main Content + Optional Right Sidebar (Task Details Drawer or AI Chat).
*   **Tablet (768px - 1024px):** Collapsed Left Sidebar (icons only) + Main Content. Modals instead of side drawers for task details.
*   **Mobile (< 768px):** Bottom Navigation Bar (Home, Projects, Search, Notifications). Heavy use of full-screen modals for task creation and editing. Kanban boards switch to a vertical stacked list or require horizontal swiping.

## 4. The User Journey (Happy Path)
1. User lands on `/` and is wowed by the 3D interactive hero section.
2. User clicks "Get Started", routes to `/register`.
3. Completes onboarding (creates Organization and first Workspace).
4. Routes to `/w/[workspaceId]`. Empty state prompts them to "Create First Project" or "Ask AI to generate a project template".
5. User interacts with the Kanban board, opens a task, tags a colleague, and uploads a file.
6. User clicks the "3D Workspace" toggle to view their newly created project architecture spatially.
