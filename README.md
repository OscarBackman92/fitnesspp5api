# FitTrack API Backend

[![Python](https://img.shields.io/badge/python-3.12+-brightgreen.svg)](https://python.org)
[![Django](https://img.shields.io/badge/django-5.0+-brightgreen.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15+-brightgreen.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Project Strategy & Goals

The FitTrack API aims to provide a robust backend infrastructure for fitness tracking with:
- Secure user authentication and data management
- Real-time workout tracking capabilities
- Social features for community engagement
- Performance optimized data retrieval
- Scalable architecture

## Agile Development Methodology

This project follows Agile principles with:
- Two-week sprint cycles
- Daily stand-ups
- Sprint retrospectives
- Continuous integration/deployment
- Feature-based branching strategy

### Sprint Planning
Sprints are organized into:
- Must-have features
- Should-have features
- Could-have features
- Won't-have features

## Database Schema

```mermaid
erDiagram
    User ||--|| Profile : has
    User ||--o{ Workout : creates
    User ||--o{ Goal : sets
    Workout ||--o{ Like : receives
    Workout ||--o{ Comment : has
    User ||--o{ Follow : follows
```

## Security Considerations

### Authentication
- JWT token authentication
- Token refresh mechanism
- Password validation requirements
- Session management

### Data Protection
- CORS configuration
- XSS protection
- CSRF protection
- SQL injection prevention

### API Security
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## Development vs Production Settings

### Development
```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Production
```python
DEBUG = False
ALLOWED_HOSTS = ['fittrack-api.herokuapp.com']
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL')
    )
}
```

## Environment Variables Setup

Required environment variables:
```env
# Development
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost:5432/dbname

# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name

# Email Configuration
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password

# Redis Configuration
REDIS_URL=redis://localhost:6379/1
```

## Data Models

### Profile Model
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images', blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Stats fields
    total_workouts = models.IntegerField(default=0)
    workout_streak = models.IntegerField(default=0)
    last_workout = models.DateTimeField(null=True)
```

### Workout Model
```python
class Workout(models.Model):
    WORKOUT_TYPES = [
        ('cardio', 'Cardio'),
        ('strength', 'Strength'),
        ('flexibility', 'Flexibility'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=WORKOUT_TYPES)
    duration = models.IntegerField()
    intensity = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Caching Strategy

Redis is used for caching with different TTLs:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache timeouts
CACHE_TTL = {
    'workout_list': 300,  # 5 minutes
    'profile': 3600,      # 1 hour
    'stats': 1800        # 30 minutes
}
```

## Performance Optimizations

### Database Optimizations
- Indexed fields for frequent queries
- Select_related for foreign keys
- Prefetch_related for reverse relations
- Pagination for large datasets

### Query Optimizations
```python
# Efficient querying
Workout.objects.select_related('user')\
    .prefetch_related('likes', 'comments')\
    .filter(created_at__gte=start_date)\
    .order_by('-created_at')
```

## API Documentation

Swagger/ReDoc integration:
```python
INSTALLED_APPS += ['drf_yasg']

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}
```

Access API documentation at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Error Handling

Custom exception handler:
```python
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data['status_code'] = response.status_code
        response.data['message'] = str(exc)
    
    return response
```

## Backup and Recovery

### Automated Backups
- Daily database backups
- Media files backup to S3
- Logs backup

### Recovery Procedures
1. Database restoration
2. Media files recovery
3. Application state verification

## Version Control Workflow

1. Feature branches:
```bash
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

2. Pull requests:
- Create PR from feature branch
- Code review required
- CI/CD checks pass
- Merge to main

## Contributing Guidelines

1. Fork the repository
2. Create feature branch
3. Follow coding standards:
   - PEP 8 for Python
   - DRF best practices
   - Test coverage required
4. Submit PR with:
   - Description
   - Testing steps
   - Screenshots if applicable

## Cross-Browser Testing

Tested on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

Using Browserstack for compatibility testing.

## Credits

### Tools & Libraries
- Django Rest Framework
- dj-rest-auth
- django-filter
- django-cors-headers
- django-redis
- Cloudinary

### Tutorials & Resources
- DRF Official Documentation
- Django Documentation
- Real Python Tutorials
- TestDriven.io

## Acknowledgments

Special thanks to:
- Django community
- Code Institute tutors
- Project mentors
- Testing volunteers