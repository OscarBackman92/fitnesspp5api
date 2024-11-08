# FitTrack - Fitness Activity Tracking API

[PROJECT LOGO PLACEHOLDER]

A comprehensive Django REST Framework-powered fitness tracking platform that enables users to track workouts, set goals, and build a fitness community.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-brightgreen.svg)](https://python.org)
[![Django](https://img.shields.io/badge/django-5.0+-brightgreen.svg)](https://www.djangoproject.com/)
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)](https://coverage.readthedocs.io/)
[![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/yourusername/fitnesspp5api/actions)

[DASHBOARD SCREENSHOT PLACEHOLDER]

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Dependencies](#dependencies)
4. [API Documentation](#api-documentation)
5. [Installation & Setup](#installation--setup)
6. [Testing](#testing)
7. [Development](#development)
8. [Database Schema](#database-schema)
9. [User Stories](#user-stories)
10. [Security](#security)
11. [Deployment](#deployment)
12. [Contributing](#contributing)
13. [Troubleshooting](#troubleshooting)
14. [License](#license)
15. [Contact](#contact)

## Overview

FitTrack is a robust REST API designed to provide a comprehensive fitness tracking solution. The platform enables users to monitor various types of workouts, track progress, and engage with a fitness community.

[ARCHITECTURE DIAGRAM PLACEHOLDER]

## Features

### Core Functionality
1. User Management and Authentication
2. Workout Tracking and Analysis
3. Social Interaction Features
4. Progress Monitoring
5. Goal Setting and Achievement

## Dependencies

### Core Requirements
```txt
# Core Django
Django==5.1.2
asgiref==3.8.1
sqlparse==0.5.1
typing_extensions==4.12.2
tzdata==2024.2

# Django REST Framework & Extensions
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
drf-nested-routers==0.94.1
drf-yasg==1.21.8

# Database
psycopg2==2.9.9
psycopg2-binary==2.9.10
dj-database-url==2.2.0

# Authentication & Authorization
dj-rest-auth==6.0.0
django-allauth==65.0.0
PyJWT==2.9.0

# Storage & Media
cloudinary==1.41.0
django-cloudinary-storage==0.3.0
whitenoise==6.7.0
pillow==11.0.0

# Additional Dependencies
[... rest of dependencies ...]
```

## API Documentation

### Authentication Endpoints

#### Registration
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "string",
    "email": "user@example.com",
    "password": "string"
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "string"
}
```

### Workout Endpoints

#### Create Workout
```http
POST /api/workouts/
Authorization: Bearer <token>
Content-Type: application/json

{
    "workout_type": "cardio",
    "duration": 30,
    "intensity": "moderate",
    "notes": "Morning run"
}
```

## Installation & Setup

### Prerequisites
- Python 3.12+
- PostgreSQL
- Redis
- Node.js 18+ (for frontend development)

### Local Development Setup

1. Clone the Repository
```bash
git clone https://github.com/yourusername/fitnesspp5api.git
cd fitnesspp5api
```

2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Environment Configuration
```bash
# Create .env file
cp .env.example .env

# Update .env with your values
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
CLOUDINARY_URL=cloudinary://your_cloudinary_url
REDIS_URL=redis://localhost:6379/0
```

5. Database Setup
```bash
# Create database
createdb fitnessdb

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

6. Start Development Server
```bash
python manage.py runserver
```

### Docker Setup

1. Build Container
```bash
docker build -t fitnessapp .
```

2. Run Container
```bash
docker run -p 8000:8000 fitnessapp
```

## Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test workouts.tests.test_views

# Run with coverage
coverage run manage.py test
coverage report
```

### Test Categories
1. Unit Tests
2. Integration Tests
3. API Tests
4. Performance Tests

## Development

### Code Style
- Follow PEP 8
- Use Black for formatting
- Maximum line length: 88 characters

### Git Workflow
1. Create feature branch
2. Implement changes
3. Run tests
4. Submit pull request

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run hooks
pre-commit run --all-files
```

## Database Schema

### Tables
1. Users
2. Workouts
3. Goals
4. Social Interactions

[DETAILED ERD DIAGRAM PLACEHOLDER]

## User Stories

[Detailed user stories documentation continues...]

## User Stories

### Epic 1: Authentication & Profile Management

#### User Registration (#1)
```
As a new user
I want to register an account
So that I can access the fitness tracking features

Acceptance Criteria:
- User can fill out registration form
- User receives confirmation email
- User can verify email address
- User can set initial profile information
```

#### User Login (#2)
```
As a registered user
I want to login to my account
So that I can access my fitness data

Acceptance Criteria:
- User can login with email/password
- User receives authentication token
- User stays logged in across sessions
- User can reset password if forgotten
```

### Epic 2: Workout Management

#### Log Workout (#3)
```
As a logged-in user
I want to record my workouts
So that I can track my fitness activities

Acceptance Criteria:
- User can input workout details
- User can add workout duration
- User can specify intensity
- User can add notes
- User can attach images
```

[Additional user stories continue...]

## Security

### Authentication
- JWT-based authentication
- Token refresh mechanism
- Password hashing using Argon2
- Rate limiting on auth endpoints

### Data Protection
```python
# Security Middleware Configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

# Security Settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### API Security
- Request validation
- Input sanitization
- SQL injection protection
- XSS protection

### CORS Configuration
```python
CORS_ALLOWED_ORIGINS = [
    "https://yourfrontend.com",
    "http://localhost:3000",
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
```

## Deployment

### Production Checklist

1. Environment Configuration
```bash
# Production settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECURE_SSL_REDIRECT=True
```

2. Database Setup
```bash
# Run migrations
python manage.py migrate --no-input

# Create superuser
python manage.py createsuperuser --no-input
```

3. Static Files
```bash
# Collect static files
python manage.py collectstatic --no-input

# Configure whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Deployment Options

#### Heroku Deployment
```bash
# Create Heroku app
heroku create your-app-name

# Add buildpacks
heroku buildpacks:add heroku/python

# Configure environment
heroku config:set DJANGO_SETTINGS_MODULE=config.settings.production

# Deploy
git push heroku main
```

#### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "config.wsgi:application"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
```

## Performance Optimization

### Caching Strategy
```python
# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache usage example
@method_decorator(cache_page(60 * 15))
def get_queryset(self):
    return super().get_queryset()
```

### Database Optimization
- Proper indexing
- Query optimization
- Connection pooling
- Efficient relationships

### API Optimization
- Pagination
- Field filtering
- Eager loading
- Response compression

## Contributing

### Getting Started
1. Fork the repository
2. Create feature branch
3. Install dependencies
4. Run tests

### Development Process
1. Write tests first
2. Implement features
3. Document changes
4. Submit pull request

### Code Style Guidelines
```bash
# Install development dependencies
pip install -r requirements.dev.txt

# Run formatter
black .

# Run linter
flake8
```

### Commit Message Format
```
type(scope): subject

body

footer
```

Example:
```
feat(auth): add password reset functionality

- Add password reset endpoints
- Implement email notification
- Add password reset templates

Closes #123
```

## Troubleshooting

### Common Issues

#### Database Connections
```bash
# Check database connection
python manage.py dbshell

# Reset database
python manage.py reset_db
python manage.py migrate
```

#### Cache Issues
```bash
# Clear cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

#### Static Files
```bash
# Collect static files
python manage.py collectstatic --no-input

# Check static files directory
python manage.py findstatic css/main.css
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```text
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software...
```

## Contact

- Author: Your Name
- Email: your.email@example.com
- Project Link: https://github.com/yourusername/fitnesspp5api

### Support
For support, email support@yourproject.com or join our Slack channel.

