# STEP 5: API PLANNING (CONTINUED)

## 4. Error Format & Handling

All API errors will follow a standardized, predictable format so the frontend can map them directly to UI components (e.g., toast notifications or form field errors).

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The provided data is invalid.",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address."
      },
      {
        "field": "password",
        "message": "Must be at least 8 characters long."
      }
    ],
    "trace_id": "req_5f8b9d2a1c"
  }
}
```
*   **`code`**: A machine-readable, constant string (e.g., `RESOURCE_NOT_FOUND`, `FORBIDDEN`, `RATE_LIMITED`).
*   **`trace_id`**: For debugging; allows the user to report an error that developers can look up in Datadog/ELK.

## 5. Validation Strategy

*   **Server-Side Validation:** Use **Zod** schema validation at the API controller boundary (NestJS Pipes or Express Middleware). If a payload fails Zod validation, the request is immediately rejected with a `400 Bad Request` and the `VALIDATION_ERROR` structure above, before any business logic is executed.
*   **Client-Side Validation:** The exact same **Zod** schemas are shared with the frontend (via the Monorepo/Turborepo workspace) to power React Hook Form validation. This ensures the frontend and backend are never out of sync regarding validation rules.
*   **Database Constraints:** As the final line of defense, database-level constraints (NOT NULL, UNIQUE, VARCHAR lengths) enforce data integrity even if validation logic has a bug.
