# Fitness Tracker API

## Overview

The Fitness Tracker API is a web application designed to help users track their workouts and monitor their fitness goals. Built using Django REST Framework, this API allows for user authentication, workout logging, and user profile management.

## Technologies Used

- **Backend**: Django 5.1.2
- **Django REST Framework**: 3.15.2
- **Authentication**: dj-rest-auth, Django Allauth, Simple JWT
- **Database**: SQLite (for development)
- **Deployment**: Heroku
- **Web Server**: Gunicorn

## Features

- User authentication (login/logout)
- User profile management
- Workout tracking (logging workouts with date, duration, calories burned, and workout type)

## User Stories

1. **User Registration**: As a user, I want to register for an account so that I can access the Fitness Tracker features.
2. **User Login**: As a user, I want to log in to my account to access my profile and workout data.
3. **Profile Management**: As a user, I want to create and update my profile, including a bio and profile picture.
4. **Log Workouts**: As a user, I want to log my workouts, including the type, duration, calories burned, and date of the workout.
5. **View Workout History**: As a user, I want to view my workout history to track my progress over time.
6. **User Logout**: As a user, I want to log out of my account to ensure my data remains secure.

## Milestones

1. **MVP (Minimum Viable Product)**:
   - Set up the Django project structure.
   - Implement user registration and authentication.
   - Create user profile and workout models.
   - Set up RESTful API endpoints for user profiles and workouts.

2. **User Profile Features**:
   - Implement profile creation and updates.
   - Add profile picture upload functionality.

3. **Workout Logging Features**:
   - Implement logging of workouts with duration, calories burned, and workout type.
   - Create endpoints to retrieve and update workout records.

4. **Deployment**:
   - Prepare the application for deployment on Heroku.
   - Configure environment variables and database settings.

5. **Testing**:
   - Write unit tests for API endpoints and models.
   - Ensure all features are covered by tests before final release.

6. **Future Enhancements**:
   - Implement user statistics and analytics.
   - Integrate third-party fitness APIs for enhanced functionality.

## Getting Started

To set up the project locally, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd fitnesspp5api
