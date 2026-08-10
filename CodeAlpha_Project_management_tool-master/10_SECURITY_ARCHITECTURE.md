# STEP 10: SECURITY ARCHITECTURE

## 1. Authentication & API Security
*   **JWT Authentication:** Short-lived Access Tokens (15m) are sent via the `Authorization: Bearer` header. Refresh Tokens (7d) are strictly stored in **Secure, HttpOnly, SameSite=Strict cookies**. This prevents XSS attacks from stealing the refresh token while allowing seamless silent rotation.
*   **CSRF Protection:** Because we use an HttpOnly cookie for refresh tokens, we must protect the refresh endpoint against Cross-Site Request Forgery (CSRF). We will implement Double Submit Cookie or utilize Django's built-in CSRF middleware where applicable.
*   **CORS (Cross-Origin Resource Sharing):** The API will enforce a strict whitelist of allowed origins (the Next.js production domains). No wildcard (`*`) CORS headers will be allowed.

## 2. Injection & Payload Protection
*   **XSS Protection:** 
    *   React/Next.js automatically escapes values rendered in the DOM.
    *   For the rich-text block editor, all HTML output will be strictly sanitized on the backend using **DOMPurify** (or bleach in Python) before being saved to the database.
    *   A strict Content Security Policy (CSP) header will block execution of unauthorized inline scripts.
*   **SQL Injection Protection:** The backend will strictly use the ORM (Django ORM / Prisma) which parameterizes all queries automatically. Raw SQL is strictly forbidden unless reviewed and parameterized manually.

## 3. Availability & Denial of Service
*   **Rate Limiting:** Implemented at the API Gateway / Nginx level, and within the application using Redis. 
    *   Standard APIs: 100 requests per minute per IP/User.
    *   Authentication APIs: 5 requests per minute per IP to prevent brute-force password attacks.

## 4. Authorization & Compliance
*   **Role-Based Access Control (RBAC):** Users are assigned roles (Admin, Member, Guest) at the Workspace level. 
*   **Object-Level Permissions:** Using libraries like `django-guardian` (or custom middleware), every API request checks if the user has permission for the *specific row ID* they are trying to access, guaranteeing multi-tenant isolation.
*   **Audit Trail:** A specialized middleware logs every destructive action (POST, PUT, PATCH, DELETE) to an append-only `audit_logs` table. 
*   **Logging:** All logs (which go to the ELK stack) are scrubbed of Personally Identifiable Information (PII) like passwords and credit card tokens before leaving the server.
