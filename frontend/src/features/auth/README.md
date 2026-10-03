# Auth feature

The client uses the FastAPI auth endpoints under `/api/v1`. Access tokens stay
in memory; the backend refresh token remains an HttpOnly cookie and restores a
session when the Semana shell loads.

OAuth login is handled by the API at `/api/v1/auth/oauth/{google|github}/login`.
Configure the provider credentials in the backend environment and register callback
URLs `/api/v1/auth/oauth/google/callback` and `/api/v1/auth/oauth/github/callback`
under the public API origin. OAuth accounts are marked in `users.oauth_provider`;
verified email is required, and an existing password account is never linked by email.
Google and GitHub can both authenticate an OAuth-origin account with the same verified email.
