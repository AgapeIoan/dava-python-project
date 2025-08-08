# Math Microservice

![Website](https://img.shields.io/website?url=http%3A%2F%2Fdava-api.home.agapeioan.ro%2Fdocs&up_message=online&down_message=offline&label=API%20Status)

A production-ready, containerized microservice built with **FastAPI**, designed to perform secure and observable mathematical computations. This project demonstrates best practices in modern API development, including a clean architecture, asynchronous operations, JWT and hashed API key authentication, Redis caching, structured logging via Redis Streams, and Prometheus monitoring.

**Authors:**
*   👨‍💻 Agape Ioan, Data Engineer
*   👨‍💻 Munteanu Daniela, Data Engineer
*   👨‍💻 Uliuliuc Serafim, Data Engineer

---

## ☁️ Live Demo & Architecture

This application is deployed in a secure, self-hosted environment using a **Cloudflare Tunnel**, demonstrating a robust private cloud architecture. The stack runs on a local Proxmox server and is managed via Portainer and Docker Compose.
This setup makes the service publicly and securely accessible at **[dava-api.home.agapeioan.ro](http://dava-api.home.agapeioan.ro)** without exposing any ports on the local network.

---

## 🚀 Live Endpoints

The service is live and accessible at the following endpoints:

*   🚀 **API Server & Interactive Docs (Swagger UI):** **[http://dava-api.home.agapeioan.ro/docs](http://dava-api.home.agapeioan.ro/docs)**
*   📊 **Monitoring Metrics (Prometheus):** **[http://dava-api.home.agapeioan.ro/metrics](http://dava-api.home.agapeioan.ro/metrics)**
*   ❤️ **Health Check:** **[http://dava-api.home.agapeioan.ro/healthcheck](http://dava-api.home.agapeioan.ro/healthcheck)**

---

## 🛠️ Running the Project Locally

If you wish to run the stack on your own machine, follow these steps.

### Prerequisites
*   Git
*   Docker & Docker Compose

### Step 1: Clone the Repository
```sh
git clone https://github.com/AgapeIoan/dava-python-project
cd dava-python-project
```

### Step 2: Configure Your Environment
The application uses a `.env` file for configuration. A template is provided.
```sh
# Copy the example file
cp .env.example .env
```
**Important:** Open the newly created `.env` file and **generate a new `SECRET_KEY`**. This is crucial for security. You can generate one with:
```sh
openssl rand -hex 32
```

### Step 3: Build and Run with Docker Compose
This single command builds all Docker images and starts the API server, Redis, and the log consumer.
```sh
docker-compose up --build
```
The services will now be running:
*   🚀 **API Server:** `http://localhost:8000`
*   📄 **Interactive Docs (Swagger UI):** `http://localhost:8000/docs`
*   📊 **Monitoring Metrics:** `http://localhost:8000/metrics`

### Step 4: Your First API Call (User Flow)
Use the [Interactive Docs](http://localhost:8000/docs) to follow this flow:
1.  **Create a User:** Go to `POST /auth/signup`. Click "Try it out", provide a `username`, `email`, and `password`, then "Execute".
2.  **Log In (Get JWT Token):** Click the "Authorize" button. In the `OAuth2PasswordBearer` section, enter your `username` and `password` and click "Authorize". You are now authenticated for user-protected endpoints.
3.  **Generate an API Key:** Go to the now-unlocked `POST /apikeys` endpoint. "Try it out", set an expiration, and execute. **Copy the `key` value** from the response—it will not be shown again.
4.  **Authorize with API Key:** Click the "Authorize" button again. In the `APIKeyHeader` section, paste the full API key you just copied. Click "Authorize". You can now access service-protected endpoints.
5.  **Make a Secured Math Call:** Go to `GET /api/v1/power`, "Try it out", provide the `base` and `exponent` as query parameters (e.g., `base`: "-1", `exponent`: "0.5"), and execute. You should receive a `200 OK` response.

---

## ✅ Features & Design Philosophy

*   **Mathematical Operations:** `pow`, `fibonacci`, and `factorial` endpoints. The `power` function fully supports complex numbers.
*   **Persistent Auditing:** All API requests are logged to a persistent SQLite database for auditing purposes. This is treated as a server-side effect, allowing math endpoints to maintain `GET` semantics from the client's perspective.
*   **Dual Authentication System:**
    *   🔐 **JWT Tokens:** For user-centric flows (signup/login), following the OAuth2 Password Flow.
    *   🔑 **Hashed API Keys:** For service-to-service communication. Keys are generated per user, the secret is shown only once, and only its `argon2` hash is stored, ensuring high security.
*   **High-Performance Caching:** Uses Redis and a reusable `@cache_result` decorator to cache results of expensive computations (Fibonacci, Factorial), significantly reducing latency on subsequent requests.
*   **Decoupled Logging:** Emits structured JSON logs to **Redis Streams**. A separate, containerized **log consumer** processes these logs asynchronously, ensuring that logging operations never block the main application.
*   **Monitoring:** Exposes a `/metrics` endpoint for **Prometheus** scraping, providing instant observability into request rates, errors, and latencies.
*   **Asynchronous Core:** Built from the ground up with `async/await` using FastAPI and an async database stack (`aiosqlite`) for high concurrency.
*   **Clean Architecture:** Follows a modular `endpoints`, `services`, `db`, `core` structure, ensuring a clear separation of concerns and high maintainability.
*   **Containerized:** Fully containerized with **Docker** for consistent development, testing, and deployment environments.

---

## 📂 Project Structure

| Path                 | Description                                       |
| -------------------- | ------------------------------------------------- |
| `main.py`            | App entrypoint: manages `lifespan`, middleware, and routers. |
| `api/v1/endpoints/`  | Route modules: `math`, `auth`, `users`, `apikeys`. |
| `core/`              | Shared logic: logging, config, decorators, Redis, security. |
| `db/`                | Database models (`models.py`) and async session management. |
| `services/`          | Core business logic for mathematical operations. |
| `schemas.py`         | Pydantic models for request/response validation. |
| `docker-compose.yml` | Defines the multi-container environment (API, Redis, Log Consumer). |
| `tests/`             | `pytest` suite with unit and integration tests using fixtures. |

---

## 🛠️ Technologies Used

| Category         | Technology / Library            |
| ---------------- | ------------------------------- |
| Web Framework    | FastAPI                         |
| Web Server       | Uvicorn (ASGI)                  |
| Database         | SQLite & SQLAlchemy (Async)     |
| Caching & Stream | Redis (via `redis.asyncio`)     |
| Logging          | Structlog (JSON), Redis Streams |
| Monitoring       | Starlette Exporter (Prometheus) |
| Authentication   | JWT (`python-jose`), API Keys   |
| Hashing          | Argon2 (`passlib`)              |
| Validation       | Pydantic                        |
| Testing          | Pytest, HTTPX, pytest-asyncio   |
| Containerization | Docker, docker-compose          |

