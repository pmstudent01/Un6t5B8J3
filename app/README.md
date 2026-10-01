# Vehicle Service App (Python)

A Python application that **implements** the Vehicle Service API (from the
Postman *Vehicle Service Collection*) and demonstrates consuming it through
the generated `vehicle_service_sdk`.

## Contents

| File | Purpose |
|---|---|
| `server.py` | Reference HTTP server implementing all 5 endpoints (stdlib only, no deps) |
| `demo.py` | Starts the server and drives every endpoint via the SDK |
| `requirements.txt` | App dependencies (`requests`, used by the SDK) |

## Endpoints

| HTTP | Path | Status |
|---|---|---|
| POST | `/vehicles` | 201 |
| GET | `/vehicles` | 200 |
| GET | `/vehicles/{id}` | 200 / 404 |
| PATCH | `/vehicles/{id}` | 200 / 404 |
| DELETE | `/vehicles/{id}` | 204 / 404 |

## Quick start

```bash
# from the repo root
pip install -r app/requirements.txt

# Option A: run the full demo (server + SDK calls)
python app/demo.py

# Option B: run the server, then point the SDK (or Postman) at it
python app/server.py --port 8000
```

When running the server standalone, set your Postman `baseUrl` /
environment variable to `http://localhost:8000` to exercise the collection
against this implementation.
