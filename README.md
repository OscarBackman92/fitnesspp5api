# FitPro API Backend

![Python](https://img.shields.io/badge/python-3.12+-brightgreen.svg)
![Django](https://img.shields.io/badge/django-5.0+-brightgreen.svg)
![DRF](https://img.shields.io/badge/DRF-3.15+-brightgreen.svg)

[Live API](https://fitnessapi-d773a1148384.herokuapp.com/)
[Frontend Repository](https://github.com/OscarBackman92/FitPro)

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [User Stories](#user-stories)
4. [API Integration](#api-integration)
5. [Database Design](#database-design)
6. [Technologies](#technologies)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Development Process](#development-process)
10. [Credits](#credits)

## Introduction

FitPro API Backend is a comprehensive Django REST Framework-based API designed to power social fitness applications. It provides robust backend functionality for workout tracking, social interactions, and community building.

### Key Features Overview

- Secure user authentication and profile management
- Comprehensive workout tracking and analytics
- Social interaction capabilities
- Rich API documentation
- Comprehensive test coverage
- Production-ready deployment configuration

## Features

### Core Features

#### 1. User Authentication

- JWT-based authentication system
- Secure password handling with validation
- Token refresh mechanism
- Social authentication integration
- Password reset functionality
- Email verification system
- Session management
- Rate limiting protection

#### 2. Profile Management

- Customizable user profiles
- Profile image upload via Cloudinary
- Activity tracking and history
- Privacy settings configuration
- Preference management
- Stats and achievements
- Data export capabilities
- Profile metrics tracking

#### 3. Workout Tracking

- Multiple workout types support:
  - Cardio
  - Strength Training
  - Flexibility
  - Sports
  - Custom workouts
- Comprehensive metrics:
  - Duration tracking
  - Intensity levels
  - Distance logging
  - Calorie tracking
  - Heart rate zones
- Progress monitoring:
  - Historical data analysis
  - Performance trends
  - Achievement tracking
  - Personal records
  - Goal setting

#### 4. Social Features

- Workout sharing capabilities
- Like and comment system
- Activity feed generation
- User following system
- Community interactions
- Content moderation tools
- Privacy controls
- Social metrics tracking

### Technical Features

#### 1. Security Implementation

- CORS configuration
- Request rate limiting
- XSS protection
- CSRF protection
- Input sanitization
- Data validation
- SQL injection prevention
- Security headers

#### 2. Performance Optimization

- Database query optimization
- Cloudinary media integration
- Redis caching system
- Query efficiency improvements
- Pagination implementation
- Asynchronous tasks
- Background job processing
- Resource monitoring

## API Integration

### Authentication

#### Registration

```http
POST /api/auth/registration/
Content-Type: application/json

{
    "username": "user",
    "email": "user@example.com",
    "password1": "secure_password123",
    "password2": "secure_password123"
}

// Success Response - 201 Created
{
    "key": "auth_token",
    "user": {
        "id": 1,
        "username": "user",
        "email": "user@example.com"
    }
}
```

#### Login

```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "user",
    "password": "secure_password123"
}

// Success Response - 200 OK
{
    "key": "auth_token",
    "user": {
        "id": 1,
        "username": "user",
        "profile": {...}
    }
}
```

### Workout Management

#### Create Workout

```http
POST /api/workouts/
Authorization: Token your-auth-token
Content-Type: application/json

{
    "title": "Morning Run",
    "workout_type": "cardio",
    "duration": 30,
    "intensity": "moderate",
    "notes": "5k run",
    "date_logged": "2024-03-14"
}
```

#### Get Workouts with Filtering

```http
GET /api/workouts/?workout_type=cardio&date_after=2024-01-01
Authorization: Token your-auth-token

// Response includes pagination
{
    "count": 25,
    "next": "http://api.example.com/workouts/?page=2",
    "previous": null,
    "results": [...]
}
```

### Social Interaction

#### Create Post

```http
POST /api/social/feed/
Authorization: Token your-auth-token
Content-Type: application/json

{
    "workout_id": 1,
    "description": "Great session!"
}
```

#### Like/Unlike Post

```http
POST /api/social/feed/1/like/
Authorization: Token your-auth-token

// Response
{
    "status": "liked" // or "unliked"
}
```

### Rate Limiting

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 98
X-RateLimit-Reset: 1627498800
```

- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Premium users: 5000 requests/hour

## Database Design

### Entity Relationship Diagram

![erd](/readme_images/erd_fitness_api.png)

### Core Models

#### UserProfile

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    profile_image = CloudinaryField('image')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
```

#### Workout

```python
class Workout(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    workout_type = models.CharField(max_length=100, choices=WORKOUT_TYPES)
    duration = models.IntegerField()
    intensity = models.CharField(max_length=20, choices=INTENSITY_LEVELS)
    notes = models.TextField(blank=True)
    date_logged = models.DateField()
```

#### Social Models

```python
class WorkoutPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(WorkoutPost, on_delete=models.CASCADE)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(WorkoutPost, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

## Technologies

### Core Stack

- Python 3.12+
- Django 5.1.2
- Django REST Framework 3.15.2
- PostgreSQL
- Redis
- Cloudinary
- JWT Authentication

### Development Tools

- Git & GitHub
- VS Code
- Thunder Client/Postman
- pgAdmin 4
- Docker

### Testing Tools

- Django Test Suite
- Markdown manual testing

### Additional Libraries

```txt
asgiref==3.8.1
certifi==2024.8.30
cloudinary==1.41.0
dj-database-url==2.2.0
dj-rest-auth==6.0.0
django-allauth==65.0.2
django-cors-headers==4.5.0
djangorestframework==3.15.2
gunicorn==23.0.0
psycopg2==2.9.9
PyJWT==2.9.0
python-dotenv==1.0.1
whitenoise==6.7.0
```

## Deployment

### Prerequisites

- Heroku account
- PostgreSQL database
- Cloudinary account
- Email service (optional)

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/your-username/fitnessapi.git
cd fitnessapi

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings:
# SECRET_KEY=your-secret-key
# DATABASE_URL=your-database-url
# CLOUDINARY_URL=your-cloudinary-url

# Run migrations and create superuser
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Version Control

The site was created using the Visual Studio Code editor and pushed to github to the remote repository Battleship_PP3_CI

The following git commands were used throughout development to push code to the remote repo:

- ```git add .``` - This command was used to add the file(s) to the staging area before they are committed.
- ```git commit -m "commit message"``` - This command was used to commit changes to the local repository queue ready for the final step.
- ```git push``` - This command was used to push all committed code to the remote repository on github.

### Heroku Deployment

The below steps were followed to deploy this project to Heroku:

- Go to Heroku and click "New" to create a new app.

- Choose an app name and region region, click "Create app".
- Navigate to Buildpacks and add buildpacks for Python and NodeJS (in that order).
- Navigate to "Deploy". Set the deployment method to Github and enter repository name and connect.
- Scroll down to Manual Deploy, select "main" branch and click "Deploy Branch".
- The app will now be deployed to heroku

## Development Process

### Agile Methodology

- Two-week sprint cycles
- Daily standups
- Sprint planning meetings
- Sprint retrospectives
- Continuous integration/deployment

### Version Control

- Feature branch workflow
- Pull request reviews
- Semantic versioning
- Automated testing
- Deployment automation

### Code Quality

- PEP 8 compliance
- Regular code reviews
- Comprehensive documentation

PEP8 Validation
API Module
<details> <summary>Expand API Module</summary> <img src="readme_images/api_admin.png" alt="API Admin" width="100%"> <img src="readme_images/api_middelware.png" alt="API Middleware" width="100%"> <img src="readme_images/api_models.png" alt="API Models" width="100%"> <img src="readme_images/api_serializer.png" alt="API Serializers" width="100%"> <img src="readme_images/api_url.png" alt="API URLs" width="100%"> <img src="readme_images/api_utils.png" alt="API Utilities" width="100%"> <img src="readme_images/api_views.png" alt="API Views" width="100%"> </details>
Config Module
<details> <summary>Expand Config Module</summary> <img src="readme_images/config_permissions.png" alt="Config Permissions" width="100%"> <img src="readme_images/config_settings.png" alt="Config Settings" width="100%"> <img src="readme_images/config_uls.png" alt="Config URLs" width="100%"> <img src="readme_images/config_views.png" alt="Config Views" width="100%"> </details>
Social Module
<details> <summary>Expand Social Module</summary> <img src="readme_images/social_admin.png" alt="Social Admin" width="100%"> <img src="readme_images/social_models.png" alt="Social Models" width="100%"> <img src="readme_images/social_serializer.png" alt="Social Serializers" width="100%"> <img src="readme_images/social_urls.png" alt="Social URLs" width="100%"> <img src="readme_images/social_view.png" alt="Social Views" width="100%"> </details>
Workouts Module
<details> <summary>Expand Workouts Module</summary> <img src="readme_images/workouts_admin.png" alt="Workouts Admin" width="100%"> <img src="readme_images/workouts_models.png" alt="Workouts Models" width="100%"> <img src="readme_images/workouts_serializers.png" alt="Workouts Serializers" width="100%"> <img src="readme_images/workouts_urls.png" alt="Workouts URLs" width="100%"> <img src="readme_images/workouts_view.png" alt="Workouts Views" width="100%"> </details>

## Testing

Detailed testing documentation is available in [TESTING.md](TESTING.md)

## Credits

### Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Cloudinary Documentation](https://cloudinary.com/documentation)

### Acknowledgements

- Daisy Mentor
- Stack Overflow community
- Django community
- Family for testing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
