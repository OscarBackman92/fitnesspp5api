# Fitness Tracking API

## Overview

This project is a RESTful API for a fitness tracking application built with Django and Django REST Framework. It allows users to register, log in, create profiles, and track their workouts.

## Features

- User registration and authentication
- User profile management
- Workout logging and tracking
- Workout summary statistics

## Technologies Used

- Python 3.12
- Django 5.1.2
- Django REST Framework
- PostgreSQL (for production)
- SQLite (for development)
- Heroku (for deployment)

## Setup and Installation

1. Clone the repository:
   git clone https://github.com/yourusername/fitness-tracking-api.git
   cd fitness-tracking-api

2. Create a virtual environment and activate it:
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate

3. Install the required packages:
   pip install -r requirements.txt

4. Set up environment variables:
Create a `.env` file in the project root and add the following:
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=your_database_url (for production)

5. Run migrations:
   python manage.py migrate

6. Start the development server:
   python manage.py runserver

## API Endpoints

- `POST /api/auth/register/`: User registration
- `POST /api/auth/login/`: User login
- `POST /api/auth/logout/`: User logout
- `GET /api/profiles/`: List user profiles
- `POST /api/profiles/`: Create user profile
- `GET /api/profiles/{id}/`: Retrieve user profile
- `PUT /api/profiles/{id}/`: Update user profile
- `DELETE /api/profiles/{id}/`: Delete user profile
- `GET /api/workouts/`: List workouts
- `POST /api/workouts/`: Create workout
- `GET /api/workouts/{id}/`: Retrieve workout
- `PUT /api/workouts/{id}/`: Update workout
- `DELETE /api/workouts/{id}/`: Delete workout
- `GET /api/workouts/summary/`: Get workout summary

## Testing

To run the test suite:
python manage.py test
Copy
## Deployment

This project is configured for deployment on Heroku. Follow these steps to deploy:

1. Create a new Heroku app
2. Set the necessary environment variables in Heroku's config vars
3. Connect your GitHub repository to the Heroku app
4. Enable automatic deploys or manually deploy your main branch

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
