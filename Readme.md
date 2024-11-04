# URL Shortener

Simple URL shortening service built with FastAPI and React. Creates shortened versions of long URLs with an easy-to-use interface.

## Features
- URL shortening with configurable length
- Automatic duplicate detection
- URL validation
- Copy-to-clipboard functionality
- Docker support
- API documentation
- Pytest testing

## Running the Application

Start the application using Docker Compose:
```bash
docker compose up --build
```

Application endpoints:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Running Tests

Backend tests:
```bash
docker compose exec backend poetry run pytest -v
```