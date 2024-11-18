# FitTrack API

A Django REST Framework-powered fitness tracking API that enables workout tracking, social interactions, and community building around fitness goals.

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