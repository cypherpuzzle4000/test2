# Standalone PostgreSQL playground

This is separate from the Task API project in the parent directory. It gives you a disposable PostgreSQL database to explore with the VS Code PostgreSQL extension.

## Start PostgreSQL

From this directory:

```bash
docker compose up -d
docker compose ps
```

When opened through the repository's GitHub Codespaces configuration, this playground starts automatically. Run the commands above if you stopped it or created the Codespace before the configuration was added.

This test database uses port `5433` so it does not collide with the Task API project.

## Connect with the VS Code PostgreSQL extension

Choose **Add Connection** and use:

```text
Host:      localhost
Port:      5433
Database:  playground
Username:  learner
Password:  learner
SSL:       disable or prefer
```

After connecting, open a query window and try:

```sql
CREATE TABLE practice_notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO practice_notes (note)
VALUES ('Created from the PostgreSQL extension');

SELECT * FROM practice_notes;
```

You can also connect from the terminal:

```bash
docker compose exec postgres psql -h localhost -p 5433 -U learner -d playground
```

## Reset the playground

Stop it and keep the data:

```bash
docker compose down
```

Delete the data and start fresh:

```bash
docker compose down -v
```