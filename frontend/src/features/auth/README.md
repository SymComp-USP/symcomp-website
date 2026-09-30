# Auth feature

The client uses the FastAPI auth endpoints under `/api/v1`. Access tokens stay
in memory; the backend refresh token remains an HttpOnly cookie and restores a
session when the Semana shell loads.
