# FitPro API Backend

![Python](https://img.shields.io/badge/python-3.12+-brightgreen.svg)
![Django](https://img.shields.io/badge/django-5.0+-brightgreen.svg)
![DRF](https://img.shields.io/badge/DRF-3.15+-brightgreen.svg)

[Live API](https://fitnessapi-d773a1148384.herokuapp.com/)
[Frontend Repository](#) <!-- Add your frontend repo link -->

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

### Project Goals

- Provide secure user authentication and profile management
- Enable detailed workout tracking and progress monitoring
- Support social interactions between users
- Ensure data privacy and security
- Facilitate seamless frontend integration
- Maintain comprehensive documentation

## Features

### Core Features

1. User Authentication
   - JWT-based authentication
   - Secure password handling
   - Token refresh mechanism

2. Profile Management
   - Customizable user profiles
   - Profile image upload via Cloudinary
   - Activity tracking

3. Workout Tracking
   - Multiple workout types
   - Duration and intensity tracking
   - Progress monitoring
   - Workout statistics

4. Social Features
   - Workout sharing
   - Likes and comments
   - Activity feed

### Technical Features

1. Security
   - CORS configuration
   - Request rate limiting
   - Proper permission handling

2. Performance
   - Database query optimization
   - Cloudinary integration for media
   - Redis caching (optional)

## User Stories

### Authentication & Profiles

1. As a new user, I want to create an account
   ```
   Acceptance Criteria:
   - Register with username/password
   - Receive confirmation
   - Automatic profile creation
   - Set initial preferences
   ```

2. As a registered user, I want to manage my profile
   ```
   Acceptance Criteria:
   - Edit profile information
   - Update profile picture
   - View activity history
   - Manage privacy settings
   ```

[Additional user stories...]

## API Integration

### Authentication

```python
# Register
POST /api/auth/registration/
{
    "username": "user",
    "password1": "pass123!@#",
    "password2": "pass123!@#",
    "email": "user@example.com"
}

# Login
POST /api/auth/login/
{
    "username": "user",
    "password": "pass123!@#"
}

# Response
{
    "key": "Token..."
}
```

### Workouts

```python
# Create Workout
POST /api/workouts/
{
    "title": "Morning Run",
    "workout_type": "cardio",
    "duration": 30,
    "intensity": "moderate",
    "notes": "5k run",
    "date_logged": "2024-03-14"
}

# Get Workouts with Filtering
GET /api/workouts/?workout_type=cardio&date_after=2024-01-01

# Get Workout Statistics
GET /api/workouts/statistics/
```

[Additional endpoint documentation...]

## Database Design

### Entity Relationship Diagram

[Mermaid diagram appears here automatically]

### Models Documentation

<details>
<summary>Complete Model Documentation</summary>

#### UserProfile Model
```python
class UserProfile(models.Model):
    """
    Extends the User model with additional profile information.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    profile_image = CloudinaryField('image', folder='profile_images')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

[Additional model documentation...]

</details>

## Technologies

### Core Technologies

- Python 3.12+
- Django 5.1.2
- Django REST Framework 3.15.2
- PostgreSQL
- Cloudinary
- JWT Authentication

### Development Tools

- Git & GitHub
- VS Code
- Thunder Client/Postman
- pgAdmin 4

### Python Libraries

```txt
asgiref==3.8.1
certifi==2024.8.30
cloudinary==1.41.0
dj-database-url==2.2.0
dj-rest-auth==6.0.0
Django==5.1.2
django-allauth==65.0.2
django-cors-headers==4.5.0
djangorestframework==3.15.2
psycopg2==2.9.9
PyJWT==2.9.0
python-dotenv==1.0.1
```

[Full requirements.txt contents...]

## Testing

### Automated Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test workouts
python manage.py test social

# Run with coverage
coverage run manage.py test
coverage report
coverage html
```

### Manual Testing Process

<details>
<summary>API Endpoint Testing Procedures</summary>

1. Authentication Testing
   - Registration process
   - Login/logout flow
   - Token refresh
   - Password reset

2. Workout Operations
   - Create workout
   - Update workout
   - Delete workout
   - List workouts with filters

[Additional testing procedures...]

</details>

## Deployment

### Local Development Setup

1. Clone the Repository
   ```bash
   git clone https://github.com/your-username/fitnessapi.git
   cd fitnessapi
   ```

2. Create Virtual Environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix
   venv\Scripts\activate     # Windows
   ```

3. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Environment Variables
   Create a `.env` file:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=your-database-url
   CLOUDINARY_URL=your-cloudinary-url
   ```

5. Database Setup
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create Superuser
   ```bash
   python manage.py createsuperuser
   ```

7. Run Development Server
   ```bash
   python manage.py runserver
   ```

### Heroku Deployment

1. Prerequisites
   - Heroku account
   - Heroku CLI installed
   - PostgreSQL database
   - Cloudinary account

2. Prepare the Application
   ```bash
   # Create Procfile
   echo "web: gunicorn config.wsgi:application" > Procfile
   
   # Create runtime.txt
   echo "python-3.12.0" > runtime.txt
   
   # Update requirements.txt
   pip freeze > requirements.txt
   ```

3. Create Heroku App
   ```bash
   heroku create your-app-name
   ```

4. Configure Environment Variables
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=.herokuapp.com
   heroku config:set DATABASE_URL=your-database-url
   heroku config:set CLOUDINARY_URL=your-cloudinary-url
   ```

5. Database Setup
   ```bash
   heroku run python manage.py makemigrations
   heroku run python manage.py migrate
   ```

6. Create Superuser
   ```bash
   heroku run python manage.py createsuperuser
   ```

7. Deploy Code
   ```bash
   git push heroku main
   ```

### Forking the Repository

1. Go to the GitHub repository
2. Click the "Fork" button in the top right
3. Choose your account as the destination

### Cloning the Repository

1. Go to the GitHub repository
2. Click the "Code" button
3. Copy the HTTPS or SSH URL
4. Open terminal and run:
   ```bash
   git clone [URL]
   ```

## Development Process

### Version Control

- Regular commits with clear messages
- Feature branches for development
- Pull requests for code review
- Main branch protection

### Code Quality

- PEP 8 compliance
- Regular code reviews
- Comprehensive documentation
- Automated testing

## Credits

### Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Cloudinary Documentation](https://cloudinary.com/documentation)

### Acknowledgements
- Code Institute tutors and mentors
- Stack Overflow community
- GitHub community
- Fellow developers who provided feedback