# NexusProject Enterprise

NexusProject is an enterprise-grade, immersive 3D project management tool built with Next.js 15, Django 5, and Three.js. It features realtime collaboration, advanced Kanban boards, AI-powered productivity tools, and a bank-grade security architecture.

## 🚀 Key Features
*   **Immersive 3D Workspace:** Spatially organize tasks, dependencies, and teams using our custom WebGL engine built on React Three Fiber and GSAP.
*   **Realtime Collaboration:** Multi-player editing, live cursors, typing indicators, and instant comment sync powered by Django Channels and Redis.
*   **Enterprise Architecture:** Clean Architecture backend utilizing PostgreSQL for strict ACID compliance, coupled with a highly scalable Next.js frontend deployed via Docker.
*   **AI Productivity:** Smart task assignments, risk prediction, workload analysis, and automated meeting summaries.

## 🛠️ Technology Stack
*   **Frontend:** Next.js 15 (App Router), React 19, Tailwind CSS, Shadcn UI, Zustand, React Query
*   **3D Engine:** Three.js, React Three Fiber (R3F), Drei, Framer Motion 3D
*   **Backend:** Python 3.13, Django 5.x, Django Rest Framework, Celery Workers
*   **Realtime & Cache:** Django Channels (ASGI), Redis
*   **Database:** PostgreSQL 15
*   **DevOps:** Docker, Docker Compose, GitHub Actions CI/CD, Nginx Reverse Proxy

## 📦 Local Setup (Docker)
The fastest way to spin up the entire microservices architecture is via Docker Compose.

1.  Clone the repository.
2.  Ensure Docker and Docker Compose are installed on your machine.
3.  Run the orchestration command:
    ```bash
    docker-compose up --build -d
    ```
4.  Access the Frontend Application at: `http://localhost:3000`
5.  Access the Backend API at: `http://localhost:8000/api/v1`
6.  Access the Swagger OpenAPI Docs at: `http://localhost:8000/api/docs/`// or run bat directly

## 🛡️ Security & Compliance
*   Strict JWT-based Authentication with sliding window token refresh.
*   Granular Role-Based Access Control (RBAC) via `django-guardian`.
*   Object-level data isolation for multi-tenancy workspaces.
*   Immutable Audit Logging for all critical entity mutations.
*   OWASP-compliant middleware protecting against XSS, CSRF, and SQL Injection.

## 🧪 Testing
The CI/CD pipeline enforces 100% passing tests before deployment.
To run the test suite locally:
```bash
# Backend Tests
cd backend && python manage.py test

# Frontend Linting
cd frontend && npm run lint
```

username:codealpha@gmail.com
passowrd:Code@123