# Django Fitness API

A comprehensive RESTful API for fitness tracking and user profile management, built with Django REST Framework. The API enables user registration, profile management with physical attributes, and detailed workout tracking.

## Features

### User Management

- User registration and authentication with JWT
- Customizable user profiles with physical attributes
- Profile picture management via Cloudinary
- Automatic BMI and age calculations
- Secure password handling

### Workout Tracking

- Multiple workout types (cardio, strength, flexibility, sports)
- Duration and calorie tracking
- Workout intensity levels
- Detailed notes and timestamps
- Comprehensive workout statistics and summaries

### API Features

- Token-based authentication
- Custom permissions for object ownership
- Filtering, searching, and ordering capabilities
- Cloudinary integration for media storage
- CORS support for frontend integration

## Technical Stack

- **Python:** 3.x
- **Framework:** Django 5.1.2
- **API Framework:** Django REST Framework 3.15.2
- **Database:**
  - Development: SQLite
  - Production: PostgreSQL
- **Authentication:** JWT via djangorestframework-simplejwt
- **Media Storage:** Cloudinary
- **Additional Tools:**
  - django-filter for advanced querying
  - django-cors-headers for CORS support
  - whitenoise for static file handling
  - gunicorn for production serving

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd fitness-api
```

2.  Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create .env file:

```env
SECRET_KEY=your_secret_key
DEVELOPMENT=True
CLOUDINARY_URL=your_cloudinary_url
DATABASE_URL=your_database_url  # For production
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Start development server:

```bash
python manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token

### User Profiles

- `GET /api/profiles/me/` - Get current user profile
- `PUT /api/profiles/update_profile_picture/` - Update profile picture
- `GET /api/profiles/` - List user profiles (authenticated users only)
- `PUT/PATCH /api/profiles/{id}/` - Update user profile

### Workouts

- `GET /api/workouts/` - List user's workouts
- `POST /api/workouts/` - Create new workout
- `GET /api/workouts/{id}/` - Retrieve specific workout
- `PUT/PATCH /api/workouts/{id}/` - Update workout
- `DELETE /api/workouts/{id}/` - Delete workout
- `GET /api/workouts/summary/` - Get workout statistics

## Models

### UserProfile

```python
- user (OneToOneField to User)
- name (CharField)
- weight (FloatField)
- height (FloatField)
- fitness_goals (TextField)
- profile_picture (CloudinaryField)
- date_of_birth (DateField)
- gender (CharField)
```

### Workout

```python
- user (ForeignKey to User)
- workout_type (CharField)
- date_logged (DateField)
- duration (IntegerField)
- calories (IntegerField)
- notes (TextField)
- intensity (CharField)
```

## Testing

Run the test suite:

```bash
python manage.py test
```

The project includes comprehensive tests for:

- Models
- Serializers
- Views
- API endpoints
- Permissions

## Security Features

- JWT Authentication
- Custom permission classes for object ownership
- CORS configuration
- SSL/TLS support
- Secure cookie handling
- CSRF protection
- HTTP Strict Transport Security (HSTS)

## Development Features

- Detailed error logging
- Django Debug Toolbar in development
- Comprehensive test coverage
- DRF browsable API
- Filtering and search capabilities

## Production Deployment

1. Update .env with production settings:

```env
DEVELOPMENT=False
DATABASE_URL=your_production_db_url
CLOUDINARY_URL=your_cloudinary_url
```

2. Configure production settings:

- SSL/TLS certificates
- ALLOWED_HOSTS
- Static file serving
- Database configuration

3. Additional security measures enabled in production:

- Secure SSL redirect
- Secure cookies
- HSTS
- CSRF protection

## API Documentation

The API provides built-in documentation through the Django REST Framework browsable API interface, accessible when running the server in development mode.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]
