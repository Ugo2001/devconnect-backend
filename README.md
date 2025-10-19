readme = """
# DevConnect - Developer Community Platform

A full-featured developer networking platform built with Django, React, PostgreSQL, and Redis.

## Features

- 🔐 User authentication with OAuth and JWT
- 📝 Markdown editor for blog posts with syntax highlighting
- 💬 Real-time notifications using WebSockets
- 🔍 Advanced search with full-text search capabilities
- 🎯 RESTful API with pagination and filtering
- 👥 Role-based access control (RBAC)
- 📊 Code snippet sharing with syntax highlighting
- ⚡ Redis caching for improved performance

## Tech Stack

- **Backend:** Django 4.2, Django REST Framework
- **Database:** PostgreSQL with full-text search
- **Cache:** Redis
- **Real-time:** Django Channels (WebSockets)
- **Task Queue:** Celery
- **Storage:** AWS S3 (optional)
- **Frontend:** React (separate repo/folder)
- **Deployment:** Docker, Docker Compose

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+ (if running locally)
- Redis (if running locally)

### Quick Start with Docker

1. Clone the repository
2. Copy `.env.example` to `.env` and update values
3. Run: `docker-compose up --build`
4. Access the API at `http://localhost:8000`

### Local Development Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup PostgreSQL and Redis (ensure they're running)

4. Copy `.env.example` to `.env` and configure

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run development server:
   ```bash
   python manage.py runserver
   ```

8. In separate terminals, run Celery:
   ```bash
   celery -A devconnect worker -l info
   celery -A devconnect beat -l info
   ```

## API Documentation

Once running, visit:
- Admin panel: `http://localhost:8000/admin/`
- API root: `http://localhost:8000/api/`
- API docs: `http://localhost:8000/api/docs/` (if configured)

## Testing

Run tests with pytest:
```bash
pytest
pytest --cov=apps  # With coverage
```

## Project Structure

See the code artifact for complete project structure details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

MIT License
"""
