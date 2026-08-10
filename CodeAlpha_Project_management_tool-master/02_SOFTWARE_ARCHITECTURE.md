# STEP 2: SOFTWARE ARCHITECTURE

To ensure high performance, security, maintainability, and scalability, the application will follow a modernized, layered N-Tier architecture combined with Microservices principles where necessary.

## 1. Presentation Layer (The UI/UX)
*   **Technology:** Next.js (App Router), React, Vanilla CSS (CSS Modules), React Three Fiber (Three.js), Zustand.
*   **Responsibilities:**
    *   Render the user interface and handle client-side routing.
    *   Maintain global client state (Zustand) and server-state caching (React Query).
    *   Render the **Premium 3D Workspace** using WebGL. This layer will use techniques like InstancedMesh and Level of Detail (LOD) to ensure 60fps rendering even with thousands of task nodes.
    *   Provide an extremely responsive, glassmorphic, highly animated (framer-motion or CSS transitions) premium experience.

## 2. Business Layer (Domain Logic)
*   **Technology:** TypeScript, Node.js / NestJS.
*   **Responsibilities:**
    *   Execute the core domain rules (e.g., "A task cannot be marked 'Done' if subtasks are pending").
    *   Process the Automation Engine rules (If THIS then THAT).
    *   Calculate reporting metrics and sprint velocities.
    *   This layer sits completely decoupled from the database and presentation layers, ensuring business rules can be tested in isolation (TDD).

## 3. Service Layer (API & Orchestration)
*   **Technology:** tRPC or GraphQL (for complex, nested frontend queries), REST (for webhooks/third parties).
*   **Responsibilities:**
    *   Act as the entry point for the Presentation layer.
    *   Orchestrate calls across different domain services (e.g., calling the Task Service and then the Notification Service).
    *   Manage background jobs (using BullMQ or similar) for heavy tasks like generating large CSV reports or processing video uploads.
    *   Coordinate AI tasks (sending prompts to the AI microservice and waiting for webhooks).

## 4. Repository Layer (Data Access)
*   **Technology:** Prisma ORM or Drizzle ORM.
*   **Responsibilities:**
    *   Abstract the underlying database technologies from the Business Layer.
    *   Handle query optimization, connection pooling, and data serialization.
    *   Enforce structural constraints and complex joins (e.g., retrieving the full task hierarchy).

## 5. Authentication & Authorization Layer
*   **Technology:** NextAuth.js or Clerk, standard JWTs, Redis (Session Store).
*   **Responsibilities:**
    *   **Authentication:** Verify user identity via OAuth providers (Google, Microsoft) or SAML/SSO for enterprise.
    *   **Authorization:** Middleware that runs on *every* request. Implements Attribute-Based Access Control (ABAC) evaluating: User Role + Resource ID + Workspace ID.
    *   Provides secure, HTTP-only cookies to the Presentation Layer.

## 6. Realtime Layer
*   **Technology:** WebSockets / Socket.io, Redis Pub/Sub, Yjs (CRDT).
*   **Responsibilities:**
    *   Maintain persistent connections with the Presentation Layer.
    *   Use Redis Pub/Sub to broadcast events across multiple load-balanced Node.js instances (e.g., User A updates Task 1 -> Node 1 -> Redis -> Node 2 -> User B).
    *   Manage Document Synchronization: When multiple users edit a rich-text block, this layer uses CRDTs to merge changes conflict-free in real-time.

## 7. Database Layer
The system uses a Polyglot Persistence strategy to optimize for different data access patterns:
*   **Primary DB (PostgreSQL):** The source of truth for relational data. Workspaces, Users, Projects, Tasks, and Audit Logs. Optimized with Row-Level Security for multi-tenancy.
*   **Cache & Pub/Sub (Redis):** Handles session data, rate limiting, and the real-time event backplane.
*   **Document DB (MongoDB / DynamoDB):** Stores the schema-less, highly nested JSON structures of the Notion-like collaborative documents and block-editor content.
*   **Vector DB (Pinecone / Milvus):** Stores embedding vectors of all text data. Used by the AI Productivity Engine to power Semantic Search and RAG (Retrieval-Augmented Generation).
*   **Object Storage (AWS S3):** Stores all user-uploaded files, avatars, and exported reports, fronted by a CDN (Cloudflare or AWS CloudFront) for fast global delivery.
