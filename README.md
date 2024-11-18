# FitPro API

A Django REST Framework-powered fitness tracking API that enables workout tracking, social interactions, and community building around fitness goals.

## Table of Contents
1. [Database Schema](#database-schema)
2. [Technology Stack](#technology-stack)
3. [Core Features](#core-features)
4. [API Endpoints](#api-endpoints)
5. [Installation](#installation)
6. [Development Setup](#development-setup)
7. [Security Features](#security-features)
8. [Caching Strategy](#caching-strategy)
9. [Testing](#testing)
10. [License](#license)

## Database Schema

### Entity Relationship Diagram

![Entity Relationship Diagram](./readme_images/api_erd.png)

The ERD illustrates the relationships between:
- Users and Profiles (1:1)
- Users and Workouts (1:Many)
- Users and Followers (Many:Many)
- Workouts and Comments (1:Many)
- Workouts and Likes (1:Many)

## PEP8 Validation

Here are the results from the PEP8 validation for the codebase:

<details>
  <summary>Click to expand PEP8 Validation Results</summary>

  ### Validation Overview
  ![PEP8 Validation 1](./readme_images/config_setting.png)

  ### URLs Configuration
  ![PEP8 Validation 2](./readme_images/config_urls.png)

  ### Views Configuration
  ![PEP8 Validation 3](./readme_images/config_views.png)

  ### Core Permissions
  ![PEP8 Validation 4](./readme_images/core_permissons.png)

  ### Core Serializers
  ![PEP8 Validation 5](./readme_images/core_serializers.png)

  ### Followers Model
  ![PEP8 Validation 6](./readme_images/followers_model.png)

  ### Followers Serializers
  ![PEP8 Validation 7](./readme_images/followers_serializers.png)

  ### Followers Test
  ![PEP8 Validation 8](./readme_images/followers_test.png)

  ### Followers URLs
  ![PEP8 Validation 9](./readme_images/followers_urls.png)

  ### Followers Views
  ![PEP8 Validation 10](./readme_images/followers_view.png)

  ### Likes Model
  ![PEP8 Validation 11](./readme_images/likes_model.png)

  ### Likes Serializers
  ![PEP8 Validation 12](./readme_images/likes_serializers.png)

  ### Likes Test
  ![PEP8 Validation 13](./readme_images/likes_test.png)

  ### Likes URLs
  ![PEP8 Validation 14](./readme_images/likes_urls.png)

  ### Likes Views
  ![PEP8 Validation 15](./readme_images/likes_views.png)

  ### Profile Admin
  ![PEP8 Validation 16](./readme_images/profile_admin.png)

  ### Profile Middleware
  ![PEP8 Validation 17](./readme_images/profile_middleware.png)

  ### Profile Model
  ![PEP8 Validation 18](./readme_images/profile_model.png)

  ### Profile Serializers
  ![PEP8 Validation 19](./readme_images/profile_serializers.png)

  ### Profile URLs
  ![PEP8 Validation 20](./readme_images/profile_urls.png)

  ### Profile Utilities
  ![PEP8 Validation 21](./readme_images/profile_utils.png)

  ### Profile Views
  ![PEP8 Validation 22](./readme_images/profile_views.png)

  ### Workout Model
  ![PEP8 Validation 23](./readme_images/workout_model.png)

  ### Workout Serializers
  ![PEP8 Validation 24](./readme_images/workout_serializers.png)

  ### Workout Test
  ![PEP8 Validation 25](./readme_images/workout_test.png)

  ### Workout URLs
  ![PEP8 Validation 26](./readme_images/workout_urls.png)

</details>

## Technology Stack

- **Python**: 3.12+
- **Django**: 5.1.2
- **Django REST Framework**: 3.15.2
- **Database**: PostgreSQL (via dj-database-url)
- **Caching**: Redis (django-redis 5.4.0)
- **Media Storage**: Cloudinary
- **Authentication**: dj-rest-auth 6.0.0
- **API Documentation**: drf-yasg 1.21.8

## Core Features

### Authentication & Authorization

- Custom user authentication using Token-based system
- Registration and login via dj-rest-auth
- Secure authorization middleware
- Session support with Redis backend

### Profile Management

- User profiles with customizable fields:
  - Basic info (name, bio)
  - Fitness metrics (weight, height)
  - Profile image (stored in Cloudinary)
- Automatic profile creation on user registration

### Workout Tracking

- CRUD operations for workouts
- Support for different workout types:
  - Cardio
  - Strength Training
  - Flexibility
  - Sports
  - Other
- Workout attributes:
  - Title and description
  - Duration tracking
  - Optional image uploads
  - Timestamps (created/updated)

### Social Features

- Follow system for connecting with other users
- Like and comment on workouts
- Activity feed for following users' workouts
- User interaction tracking

## API Endpoints

### Authentication

- `POST /dj-rest-auth/registration/` - Register new user
- `POST /dj-rest-auth/login/` - Login
- `POST /dj-rest-auth/logout/` - Logout

### Profiles

- `GET /profiles/` - List all profiles
- `GET /profiles/{id}/` - Get specific profile
- `PUT /profiles/{id}/` - Update profile (owner only)

### Workouts

- `GET /workouts/` - List workouts (with filtering & search)
- `POST /workouts/` - Create workout
- `GET /workouts/{id}/` - Get specific workout
- `PUT /workouts/{id}/` - Update workout (owner only)
- `DELETE /workouts/{id}/` - Delete workout (owner only)

### Comments

- `GET /comments/` - List comments
- `POST /comments/` - Create comment
- `GET /comments/{id}/` - Get specific comment
- `PUT/DELETE /comments/{id}/` - Manage comment (owner only)

### Likes & Following

- `POST /likes/` - Like a workout
- `DELETE /likes/{id}/` - Remove like
- `POST /followers/` - Follow a user
- `DELETE /followers/{id}/` - Unfollow user

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd fitnessapp
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables (.env):

```
DEVELOPMENT=True
DATABASE_URL=your-database-url
SECRET_KEY=your-secret-key
CLOUDINARY_URL=your-cloudinary-url
```

5. Run migrations:

```bash
python manage.py migrate
```

## Development Setup

### Required Environment Variables

```env
# Core Settings
DEVELOPMENT=True/False
SECRET_KEY=your-secret-key

# Database Configuration
DATABASE_URL=your-database-url

# Cloudinary Configuration
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

### Running the Development Server

```bash
python manage.py runserver
```

### API Documentation Access

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Security Features

- CORS configuration with whitelisted origins
- CSRF protection with trusted origins
- Rate limiting middleware
- Security headers implementation
- SSL/HTTPS enforcement in production
- Cloudinary secure media handling

## Caching Strategy

Redis caching is implemented for:

- Session storage
- API response caching
- Rate limiting counters

Configuration:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## Testing

Run the test suite:

```bash
python manage.py test
```

Run specific test files:

```bash
python manage.py test workouts.tests
python manage.py test profiles.tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

For major changes, please open an issue first to discuss what you would like to change.

## Support

For support, please open an issue in the repository.
