# recc-constructions

A small FastAPI service for tracking construction projects.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn recc_constructions.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## API

- `GET /health` checks that the service is running.
- `GET /api/v1/projects` lists projects.
- `POST /api/v1/projects` creates a project.
- `GET /api/v1/projects/{project_id}` reads a project.
- `PATCH /api/v1/projects/{project_id}` updates a project.
- `DELETE /api/v1/projects/{project_id}` deletes a project.

Project records include the client, site address, project type, status, budget,
and optional start and target completion dates. Data is held in memory, so it
resets when the service restarts; this keeps the starter app easy to run and
can be replaced with a database as the project grows.
