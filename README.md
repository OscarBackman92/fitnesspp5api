# FitTrack API

A comprehensive Django REST Framework-powered fitness tracking platform that enables users to track workouts, set goals, and build a fitness community.

[![Python](https://img.shields.io/badge/python-3.12+-brightgreen.svg)](https://python.org)
[![Django](https://img.shields.io/badge/django-5.0+-brightgreen.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15+-brightgreen.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Table of Contents
1. [Description](#description)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [API Endpoints](#api-endpoints)
8. [Authentication](#authentication)
9. [Testing](#testing)
10. [License](#license)

## Description

FitTrack API is a robust REST API designed to provide a comprehensive fitness tracking solution. The platform enables users to monitor various types of workouts, track progress, set and achieve fitness goals, and engage with a fitness community.

## Features

- User Authentication and Authorization
- Profile Management with Image Upload
- Workout Tracking and Analysis
- Goal Setting and Progress Monitoring
- Social Features (Following, Likes, Comments)
- Statistical Analysis and Progress Visualization
- Cloudinary Integration for Image Storage
- Redis Caching for Performance
- Comprehensive Test Coverage

## Prerequisites

- Python 3.12+
- PostgreSQL
- Redis
- Cloudinary Account
- Git

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fitnesspp5api
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

4. Set up environment variables (create .env file):
```env
DEVELOPMENT=True
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
SECRET_KEY=your-secret-key
CLOUDINARY_URL=cloudinary://your-cloudinary-url
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

## Configuration

### Required Environment Variables:

```env
# Development Settings
DEVELOPMENT=True/False

# Database Configuration
DATABASE_URL=postgres://user:pass@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key

# Cloudinary Configuration
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Cloudinary Setup:
1. Create a Cloudinary account
2. Get your Cloudinary URL from the dashboard
3. Add to .env file
4. Images will automatically be stored in Cloudinary

## Usage

1. Start the development server:
```bash
python manage.py runserver
```

2. Access the API at `http://localhost:8000/api/`

3. View API documentation:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user
- `GET /api/auth/user/` - Get current user info

### Profiles
- `GET /api/profiles/` - List all profiles
- `GET /api/profiles/{id}/` - Get specific profile
- `PUT /api/profiles/{id}/` - Update profile
- `POST /api/profiles/{id}/upload_image/` - Upload profile image

### Workouts
- `GET /api/workouts/` - List all workouts
- `POST /api/workouts/` - Create new workout
- `GET /api/workouts/{id}/` - Get specific workout
- `PUT /api/workouts/{id}/` - Update workout
- `DELETE /api/workouts/{id}/` - Delete workout
- `GET /api/workouts/statistics/` - Get workout statistics
- `GET /api/workouts/summary/` - Get workout summary

### Goals
- `GET /api/goals/` - List all goals
- `POST /api/goals/` - Create new goal
- `GET /api/goals/{id}/` - Get specific goal
- `PUT /api/goals/{id}/` - Update goal
- `DELETE /api/goals/{id}/` - Delete goal
- `POST /api/goals/{id}/toggle_completion/` - Toggle goal completion

### Social
- `GET /api/social/feed/` - Get social feed
- `POST /api/social/feed/{id}/like/` - Like a workout
- `POST /api/social/feed/{id}/comments/` - Comment on workout

## Authentication

The API uses Token Authentication. Include the token in the Authorization header:

```http
Authorization: Token your-auth-token
```

To get a token:
1. Register a new user
2. Login with credentials
3. Save the returned token
4. Include token in subsequent requests

Example using curl:
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username":"your_username","password":"your_password"}'

# Use token
curl http://localhost:8000/api/workouts/ \
     -H "Authorization: Token your-auth-token"
```

## Testing

1. Run all tests:
```bash
python manage.py test
```

2. Run specific test file:
```bash
python manage.py test workouts.tests
```

3. Run with coverage:
```bash
coverage run manage.py test
coverage report
```

4. Test specific features:
```bash
# Test authentication
python manage.py test api.tests.UserProfileAPITests

# Test workouts
python manage.py test workouts.tests.WorkoutViewSetTests
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```text
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Rest of MIT License text...]
```

For additional information or support, please open an issue in the repository.