# 🧞 Math Microservice
## Author names
* 👨‍💻Agape Ioan, Data Engineer
* 👨‍💻Munteanu Daniela, Data Engineer
* 👨‍💻Uliuliuc Serafim, Data Engineer

---

A production-ready, containerized microservice built with **FastAPI**, designed to perform secure and observable mathematical computations: **power, Fibonacci, and factorial**. The system leverages **Redis for caching and streaming logs**, uses **JWT and API keys for security**, and integrates **Prometheus** for monitoring.

---

## ✅ Requirements Coverage

### Core Features
* `pow` operation →  implemented via `/api/v1/power`
* `n-th Fibonacci number` →  via `/api/v1/fibonacci`
* `factorial of number` →  via `/api/v1/factorial`
* Request persistence → audit saved in `api_requests` DB table
* REST API →  built with FastAPI (OpenAPI 3.1 spec)
* Database →  SQLite + SQLAlchemy (async)

### Nice to Haves

* Containerization →  via Docker & `docker-compose`
* Monitoring →  Prometheus `/metrics` exposed via middleware
* Caching →  Redis with `@cache_result` decorator
* Authorization →  JWT + API Key protection
* Logging →  Redis Streams (structured JSON)

---

## 📂 Project Structure

| Path                 | Description                                       |
| -------------------- | ------------------------------------------------- |
| `main.py`            | App entrypoint: sets up DB, Redis, metrics        |
| `api/v1/endpoints/`  | Route modules: `math`, `auth`, `users`, `apikeys` |
| `core/`              | Logging, config, decorators, Redis, security      |
| `db/`                | Database models, session, repository              |
| `services/`          | Business logic for math operations                |
| `schemas.py`         | Pydantic models for request/response              |
| `Dockerfile`         | Container spec for the app                        |
| `docker-compose.yml` | Redis + App composition                           |
| `.env`               | Environment variables                             |

---

## Math Endpoints

| Route               | Description                                  |
| ------------------- | -------------------------------------------- |
| `/api/v1/fibonacci` | `GET`, returns Fibonacci number at index `n` |
| `/api/v1/power`     | `GET`, computes exponentiation (complex OK)  |
| `/api/v1/factorial` | `GET`, returns `n!`                          |

All endpoints are **secured** using:
* 🔐 Bearer Token (JWT)
* 🔑 `X-API-Key` header
---

## 🔒 Security
| Mechanism | Used for                  | Implementation                 |
| --------- | ------------------------- | ------------------------------ |
| JWT       | Authenticated user access | `/auth/login`, `/auth/signup`  |
| API Key   | Protected route access    | `/apikeys` generation per user |

Passwords are hashed using `argon2`.
All keys are hashed and stored securely.
---

## ♻️ Caching with Redis
Results of heavy computations are cached:

| Operation | TTL      | Storage      |
| --------- | -------- | ------------ |
| Fibonacci | 1 hour   | Redis (DB 0) |
| Factorial | 24 hours | Redis (DB 0) |

> Cache logic is abstracted via `@cache_result`, allowing easy reuse.
---

## Logging with Redis Streams

Each API event is logged to a Redis Stream (`log_stream`) with structured entries:

```json
{
  "timestamp": "...",
  "level": "INFO",
  "message": "Power calculated",
  "extra": {
    "base": "2",
    "exponent": "10"
  }
}
```
These logs can be consumed in real-time or analyzed externally (ELK, Logstash, etc.)
---

##  Monitoring
Integrated with **Prometheus** via:

```http
GET /metrics
```

The app includes:

* Request count
* Response status codes
* Latency metrics

Use `docker-compose` to spin up both Redis and the app for full observability.

---

## Persistence Layer
* Uses **SQLAlchemy async ORM**
* Models:

  * `User`: auth user
  * `ApiKey`: hashed API keys per user
  * `ApiRequest`: audit log per API call
* Audit includes input params, result, client IP

---


#### 1. Build and start:
```bash
docker-compose up --build
```

#### 2. Access:

* Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
* Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

## 🔐 Example `.env`

```dotenv
APP_NAME=Math Microservice
DATABASE_URL=sqlite:///./math_service.db
API_KEY=super_secret_api_key
API_KEY_NAME=admin_key
REDIS_HOST=redis
REDIS_PORT=6379
SECRET_KEY=your_super_secure_key
```

---

## 📦 Dependencies (requirements.txt)

Key packages used:

* `fastapi`, `uvicorn[standard]`
* `sqlalchemy`, `aiosqlite`
* `pydantic-settings`, `python-jose`, `passlib[argon2]`
* `redis`, `structlog`
* `starlette-exporter`, `prometheus`
* `pytest`, `httpx`, `pytest-asyncio`

---

##  Technologies Used

| Category         | Technology                      |
| ---------------- | ------------------------------- |
| Web Framework    | FastAPI                         |
| Web Server       | Uvicorn (ASGI)                  |
| ORM              | SQLAlchemy (Async)              |
| Database         | SQLite                          |
| Caching          | Redis (via `redis.asyncio`)     |
| Logging          | Structlog (JSON), Redis Streams |
| Monitoring       | Starlette Exporter (Prometheus) |
| Auth             | JWT (via python-jose), API Keys |
| Password Hashing | Argon2 (via passlib)            |
| Serialization    | Pydantic                        |
| Configuration    | pydantic-settings               |
| Testing          | Pytest, httpx, pytest-asyncio   |
| Containerization | Docker, docker-compose          |

---

##  Assignment Mapping

| Requirement                                | Status |
| ------------------------------------------ | ------ |
| Math operations: pow, fibonacci, factorial | ✅      |
| Persist requests to DB                     | ✅      |
| Expose as REST API                         | ✅      |
| Production-ready design                    | ✅      |
| Micro framework (Flask-like)               | ✅      |
| Follow MVCS, modular structure             | ✅      |
| Use SQL/NoSQL (SQLite OK)                  | ✅      |
| Containerization                           | ✅      |
| Caching                                    | ✅      |
| Authorization                              | ✅      |
| Logging via streaming (Redis Stream)       | ✅      |
| Monitoring (Prometheus)                    | ✅      |

---

## 👨 Author Notes

This project is fully functional, extensible, and designed using clean architecture principles. It is suitable for:

* learning how to build production-grade FastAPI services
* designing testable microservices
* integrating Redis, Prometheus, and structured logs
* demonstrating best practices in modern Python API development

---


