# Travel Planner API

A RESTful API for managing travel projects. Plan trips, collect places to visit (powered by the [Art Institute of Chicago API](https://api.artic.edu/docs/)), add personal notes, and track your visits.

## Features

- **Travel Projects**: Create, read, update, and delete travel projects
- **Places Management**: Add artworks from the Art Institute of Chicago as places to visit
- **Notes & Tracking**: Attach notes to places and mark them as visited
- **Auto-completion**: Projects automatically marked as "completed" when all places are visited
- **Validation**: External artwork validation, duplicate prevention, place limits (max 10)
- **Pagination & Filtering**: Paginated lists with search and status filters
- **API Caching**: In-memory TTL cache for external API responses
- **Interactive Docs**: Swagger UI at `/docs` and ReDoc at `/redoc`

## Tech Stack

| Component | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | SQLite (dev) / PostgreSQL (Docker) |
| Validation | Pydantic v2 |
| HTTP Client | httpx |
| Testing | pytest |
| Containerization | Docker + docker-compose |

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd travel_planner
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```

5. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Open the API docs**:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Docker

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. The API will be available at [http://localhost:8000](http://localhost:8000)

3. **Stop the containers**:
   ```bash
   docker-compose down
   ```

## API Endpoints

### Projects

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/projects` | Create a project (optionally with places) |
| `GET` | `/api/v1/projects` | List projects (paginated) |
| `GET` | `/api/v1/projects/{id}` | Get a single project |
| `PUT` | `/api/v1/projects/{id}` | Update a project |
| `DELETE` | `/api/v1/projects/{id}` | Delete a project |

### Places

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/projects/{id}/places` | Add a place to a project |
| `GET` | `/api/v1/projects/{id}/places` | List places in a project |
| `GET` | `/api/v1/projects/{id}/places/{place_id}` | Get a single place |
| `PATCH` | `/api/v1/projects/{id}/places/{place_id}` | Update notes / mark visited |

## Example Requests

### Create a project with places

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chicago Art Tour",
    "description": "Visit famous artworks",
    "start_date": "2026-08-01",
    "places": [
      {"external_id": 129884},
      {"external_id": 27992}
    ]
  }'
```

### Add a place to an existing project

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/places \
  -H "Content-Type: application/json" \
  -d '{"external_id": 28560}'
```

### Update notes and mark as visited

```bash
curl -X PATCH http://localhost:8000/api/v1/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Amazing painting!",
    "visited": true
  }'
```

### List projects with filtering

```bash
curl "http://localhost:8000/api/v1/projects?status=planning&search=chicago&page=1&per_page=5"
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./travel_planner.db` | Database connection string |
| `DEBUG` | `false` | Enable debug mode |
| `ARTIC_API_BASE_URL` | `https://api.artic.edu/api/v1` | Art Institute API base URL |
| `ARTIC_API_TIMEOUT` | `10` | API request timeout (seconds) |
| `CACHE_TTL` | `300` | Cache TTL in seconds |
| `CACHE_MAX_SIZE` | `100` | Maximum cache entries |
| `DEFAULT_PER_PAGE` | `10` | Default pagination size |
| `MAX_PER_PAGE` | `100` | Maximum pagination size |

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Postman Collection

Import the Postman collection from `postman/travel_planner.postman_collection.json` to test all endpoints interactively. The collection includes:

- Health check endpoints
- All project CRUD operations
- All place operations
- Pre-configured variables (`base_url`, `project_id`, `place_id`)

## Project Structure

```
travel_planner/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application settings
│   ├── database.py          # Database configuration
│   ├── exceptions.py        # Custom exception handlers
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic validation schemas
│   ├── services/            # Business logic layer
│   └── api/                 # API route handlers
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── postman/                 # Postman collection
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Business Rules

- A project **cannot** be deleted if any of its places are marked as **visited**
- A project can have a **minimum of 1** and **maximum of 10** places
- The same artwork **cannot** be added to the same project twice
- When **all places** in a project are marked as visited, the project is **automatically** set to **completed**
- Places are validated against the **Art Institute of Chicago API** before being added
