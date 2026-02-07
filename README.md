# LRWebsiteBackend

Backend API for the Église LaRencontre church website. Built with FastAPI and powered by Google Sheets as a CMS.

## Features

- 🚀 **FastAPI** - Modern, fast Python web framework
- 📊 **Google Sheets CMS** - Content managed via public Google Sheets
- 📝 **Google Docs Articles** - Rich article content with preserved formatting
- 🌍 **Multi-language Support** - French (primary) and English
- ⚡ **Caching** - In-memory TTL cache to minimize API calls
- 🔒 **No Authentication Required** - Uses public sheets/docs (read-only)

## Quick Start

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)

### Installation

```bash
# Clone the repository
cd LRWebsiteBackend

# Install dependencies
poetry install

# Copy environment file and configure
cp .env.example .env
# Edit .env with your Google Sheet IDs
```

### Running the Server

```bash
# Development mode with auto-reload
poetry run uvicorn app.main:app --reload

# Production mode
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/articles` | GET | List all articles (metadata) |
| `/api/articles/{slug}` | GET | Get article with full HTML content |
| `/api/boutique` | GET | List all products |
| `/api/boutique/{id}` | GET | Get single product |
| `/api/church-info` | GET | Get church information |
| `/api/events` | GET | List all events |
| `/api/events/upcoming` | GET | List upcoming events |
| `/api/home-groups` | GET | List home groups |
| `/api/pastoral-team` | GET | List pastoral team |
| `/api/services` | GET | List services (filter: `?lang=fr`) |
| `/api/vision` | GET | List vision sections |

## Google Sheets Setup

Each sheet must be **publicly accessible** (Anyone with the link can view).

### Required Sheets

| Sheet Name | Purpose |
|------------|---------|
| `articles` | Blog posts with `content_doc_url` column linking to Google Docs |
| `boutique` | Church merchandise |
| `church_information` | Contact info, social links |
| `events` | Upcoming events |
| `home_groups` | Small group meetings |
| `pastoral_team` | Staff and leadership |
| `services` | Weekly service times |
| `vision` | Mission/vision statements |

### Articles with Google Docs

For articles, store the content in Google Docs to preserve formatting:

1. Create a Google Doc for each article
2. Make it publicly viewable
3. Add the doc URL to the `content_doc_url` column in the articles sheet
4. The API will fetch and return the HTML content

## Configuration

Environment variables (`.env`):

```env
# Google Sheet IDs
SHEET_ID_ARTICLES=your-sheet-id
SHEET_ID_BOUTIQUE=your-sheet-id
# ... (see .env.example for all options)

# Cache TTL in seconds (default: 600 = 10 minutes)
CACHE_TTL_SECONDS=600

# Default language
DEFAULT_LANGUAGE=fr

# CORS origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Running Tests

```bash
poetry run pytest tests/ -v
```

## Project Structure

```
LRWebsiteBackend/
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Settings
│   ├── models/           # Pydantic models
│   ├── routers/          # API endpoints
│   └── services/         # Business logic
├── tests/                # Test files
├── pyproject.toml        # Poetry config
└── .env.example          # Environment template
```

## License

MIT
