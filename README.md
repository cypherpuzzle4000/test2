# Task API: a small backend service

This is a deliberately small backend project for learning how a service runs in production-like conditions.

It gives you a real request path:

```text
HTTP client -> FastAPI -> SQLAlchemy -> PostgreSQL
										\-> health checks
```

The application is a task list API. It is intentionally boring in the useful way: configuration comes from the environment, the database is a separate service, the API has a health endpoint, and everything runs through Docker Compose.

## What you will learn

- How an HTTP API is structured with FastAPI
- How application code connects to PostgreSQL
- How a Docker image differs from a running container
- How Compose networks multiple services together
- Why health checks and non-root containers matter
- How to inspect logs, shell into a container, and recover from failures

## Prerequisites

- Docker Desktop or Docker Engine with Compose v2
- An HTTP client such as `curl`, Postman, or the Swagger UI

Python is only required if you want to run the tests outside Docker.

## Run it

```bash
cp .env.example .env
docker compose up --build
```

## Open in GitHub Codespaces

Create a Codespace from this repository and wait for the post-create setup to finish. It starts both projects automatically:

- Task API: `http://localhost:8000`
- PostgreSQL playground: `localhost:5433`

The Codespace includes Docker, the PostgreSQL extension, and the forwarded ports. To restart either project manually:

```bash
docker compose up -d --build
docker compose -f postgres-test/compose.yaml up -d
```

Use the Ports panel to open port `8000` for the API. The PostgreSQL extension connects to the separate playground on port `5433` as described in [postgres-test/README.md](postgres-test/README.md).
The API is available at <http://localhost:8000>. Interactive API documentation is at <http://localhost:8000/docs>.

This Compose file uses host networking because some GitHub Codespaces Docker runtimes block traffic between bridge-networked containers. That makes the API reachable through the Codespaces port forwarder while keeping the API and database as separate Compose services. On Docker Desktop or a standard Docker Engine, you can switch back to the usual service-network setup and use `db` as the database hostname.

Try it:

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

curl -X POST http://localhost:8000/tasks \
	-H 'Content-Type: application/json' \
	-d '{"title":"Read the Compose logs"}'

curl http://localhost:8000/tasks
```

Stop the services with `Ctrl+C`. To also delete the database volume and start from an empty database:

```bash
docker compose down -v
```

## Useful operations

```bash
docker compose ps                         # service status and health
docker compose logs -f api                # follow API logs
docker compose exec api sh                # open a shell in the API container
docker compose exec db psql -U app -d tasks # inspect PostgreSQL directly
docker compose run --rm api pytest        # run tests in a disposable container
```

Break it on purpose. Stop the database with `docker compose stop db`, call `/health/ready`, then start it again with `docker compose start db`. The readiness endpoint should expose the difference between “the process is alive” and “the service can do its work.”

## Project map

```text
app/
	config.py   environment-backed settings
	db.py       SQLAlchemy engine and session dependency
	main.py     routes and application startup
	models.py   database table definition
	schemas.py  request and response validation
tests/        fast API tests
Dockerfile    image build instructions
compose.yaml  API + PostgreSQL orchestration
```

## Production lessons and deliberate shortcuts

This is **semi-production**, not a finished production platform.

- The API runs as a non-root user and has a health check.
- Secrets and connection details are injected through environment variables.
- PostgreSQL data lives in a named volume, so container recreation does not erase it.
- The API waits for the database health check before starting.
- SQLAlchemy creates tables on startup to keep the example approachable. A real service should use versioned migrations, usually with Alembic.
- There is no authentication, rate limiting, TLS termination, structured log shipping, or backup policy. Those are the next fires to face after the basics work.
- The sample uses one API process. In a real deployment, scale behind a reverse proxy or platform load balancer and size the database connection pool deliberately.

## Run tests locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest
```

The included tests check the health contract and do not need PostgreSQL. The Compose smoke test is the important next exercise: bring the stack up and make a real request against the database-backed endpoints.