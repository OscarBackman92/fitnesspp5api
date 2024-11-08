# FitPro - Fitness Activity Tracking API

A robust, scalable RESTful API for fitness tracking, built with Django REST Framework. This application enables users to track workouts, set fitness goals, monitor progress, and participate in a fitness-focused social community.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-brightgreen.svg)
![Django](https://img.shields.io/badge/django-5.0+-brightgreen.svg)
![DRF](https://img.shields.io/badge/DRF-3.14+-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)

## 📑 Table of Contents
- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#%EF%B8%8F-technology-stack)
- [Installation](#-installation)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [Security](#-security)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)

## 🚀 Features

### Core Features

#### User Management
- **Authentication**
  - JWT-based token authentication
  - Refresh token mechanism
  - Password reset via email
  - Social authentication (Google, Facebook)
  - Account verification
  - Session management

- **Authorization**
  - Role-based access control
  - Permission management
  - API key authentication for external services
  - Token expiration and renewal

- **Profile Management**
  - Customizable user profiles
  - Profile picture upload
  - Personal information management
  - Privacy settings

#### Workout Tracking
- **Workout Types**
  ```python
  WORKOUT_TYPES = [
      ('cardio', 'Cardio'),
      ('strength', 'Strength Training'),
      ('flexibility', 'Flexibility'),
      ('sports', 'Sports'),
      ('other', 'Other'),
  ]
  ```

- **Workout Attributes**
  - Duration tracking
  - Intensity levels
  - Distance metrics
  - Calorie calculation
  - Custom notes
  - Image attachments

- **Progress Monitoring**
  - Weekly/monthly/yearly statistics
  - Personal records tracking
  - Goal achievement monitoring
  - Streak calculation
  - Performance analytics

#### Social Features
- **Community Interaction**
  - Follow system
  - Activity feed
  - Workout sharing
  - Achievement badges
  - Challenge participation

- **Social Engagement**
  - Comments
  - Likes
  - Shares
  - User mentions
  - Custom reactions

## 🏗 Architecture

### System Architecture
```
├── Frontend (Separate Repository)
│   ├── React.js
│   └── Tailwind CSS
│
├── Backend (This Repository)
│   ├── Django
│   ├── Django REST Framework
│   └── Celery
│
├── Database
│   ├── PostgreSQL
│   └── Redis (Caching)
│
└── Cloud Services
    ├── Cloudinary (Media)
    └── AWS S3 (Static Files)
```

### Database Schema
```sql
-- Core Tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE,
    email VARCHAR(254) UNIQUE,
    password VARCHAR(128)
);

CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50),
    duration INTEGER,
    intensity VARCHAR(20),
    date_logged DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Social Tables
CREATE TABLE follows (
    id SERIAL PRIMARY KEY,
    follower_id INTEGER REFERENCES users(id),
    following_id INTEGER REFERENCES users(id)
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    workout_id INTEGER REFERENCES workouts(id),
    user_id INTEGER REFERENCES users(id),
    content TEXT,
    created_at TIMESTAMP
);
```

## 🛠️ Technology Stack

### Backend Framework
- **Django 5.0+**
  - URL routing
  - ORM
  - Admin interface
  - Authentication
  - Middleware

- **Django REST Framework 3.14+**
  - Serialization
  - ViewSets
  - Authentication classes
  - Permissions
  - Filtering

### Database & Caching
- **PostgreSQL 14+**
  - Connection pooling
  - Full-text search
  - JSON field support
  - Indexing strategies

- **Redis 6+**
  - Session storage
  - Caching layer
  - Rate limiting
  - Real-time features

### Task Processing
- **Celery**
  - Async task processing
  - Scheduled tasks
  - Email sending
  - Report generation

### Cloud Services
- **Cloudinary**
  - Image optimization
  - Transformation
  - Delivery
  - Storage

### Development Tools
- **Git**
  - Version control
  - Feature branching
  - PR workflow
  - Git hooks

- **Docker**
  ```dockerfile
  # Example Dockerfile
  FROM python:3.12-slim
  
  WORKDIR /app
  
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  
  COPY . .
  
  CMD ["gunicorn", "config.wsgi:application"]
  ```

## 📦 Installation

### Local Development Setup

1. **Clone and Setup**
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/fitnesspp5api.git
   cd fitnesspp5api

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```env
   # .env file
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgres://user:password@localhost:5432/dbname
   CLOUDINARY_URL=cloudinary://api-key:api-secret@cloud-name
   REDIS_URL=redis://localhost:6379/0
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

3. **Database Setup**
   ```bash
   # Create database
   createdb fitnessapp

   # Run migrations
   python manage.py makemigrations
   python manage.py migrate

   # Create superuser
   python manage.py createsuperuser
   ```

### Docker Setup
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
      - DATABASE_URL=postgres://postgres:postgres@db:5432/fitnessapp
      - REDIS_URL=redis://redis:6379/0

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=fitnessapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 📚 API Documentation

### Authentication Endpoints

```python
# Authentication URLs
urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/password/reset/', PasswordResetView.as_view()),
]
```

### Workout Endpoints

#### Create Workout
```http
POST /api/workouts/workouts/

{
    "workout_type": "cardio",
    "duration": 30,
    "intensity": "moderate",
    "notes": "Morning run"
}
```

#### Get Workout List
```http
GET /api/workouts/workouts/

Response:
{
    "count": 10,
    "next": "http://api.example.com/workouts/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "workout_type": "cardio",
            "duration": 30,
            "intensity": "moderate",
            "date_logged": "2024-01-01"
        }
        // ... more workouts
    ]
}
```

## 🔒 Security

### Authentication Flow
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database
    
    Client->>API: POST /auth/login/
    API->>Database: Validate Credentials
    Database-->>API: User Found
    API-->>Client: JWT Token
    
    Client->>API: Request + JWT
    API->>API: Validate Token
    API-->>Client: Protected Resource
```

### Security Measures
```python
# settings.py security configurations
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## ⚡ Performance

### Caching Strategy
```python
# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
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
```python
# Optimized queries
from django.db.models import Prefetch

class WorkoutViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Workout.objects.select_related('user')\
                            .prefetch_related(
                                Prefetch('comments'),
                                Prefetch('likes')
                            )
```

## 🔧 Troubleshooting

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

#### Permission Issues
```bash
# Check file permissions
chmod -R 755 .
chmod -R 777 media/

# Check log files
tail -f logs/debug.log
```

## 📈 Monitoring

### Health Checks
```python
# health_check/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'healthy',
        'database': check_database(),
        'cache': check_cache(),
        'storage': check_storage()
    })
```

### Performance Monitoring
- New Relic integration
- Sentry error tracking
- Custom middleware for request timing
- Prometheus metrics

## 🚀 Deployment

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Set up SSL certificates
- [ ] Configure CORS properly
- [ ] Set up proper logging
- [ ] Configure email backend
- [ ] Set up backup system
- [ ] Configure monitoring

Would you like me to expand on any of these sections further or add more specific implementation details?