# Testing Documentation

## Overview
Total Tests: 18
Testing Strategy: Each model, view, and component is tested for both successful operations and error handling.

## Manuel Testing/Markdown
| Test Case                    | Steps                                                                               | Expected Result                                                           | Actual Result     | Status |
| ---------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ----------------- | ------ |
| Create new account           | 1\. Click "Sign Up" in navbar 2. Fill in registration form 3. Submit form           | Form submits successfully and redirects to dashboard with success message | Works as expected | Pass   |
| Login to account             | 1\. Click "Sign In" in navbar 2. Enter credentials 3. Submit form                   | Successful login with dashboard redirect and success message              | Works as expected | Pass   |
| Logout from account          | 1\. Click user menu in navbar 2. Select "Logout" 3. Confirm logout                  | Successful logout with redirect to login page and success message         | Works as expected | Pass   |
| Log new workout              | 1\. Click "Log Workout" button 2. Fill workout details 3. Submit form               | Workout saves and appears in list with success message                    | Works as expected | Pass   |
| Modify existing workout      | 1\. Open workout details 2. Click edit button 3. Modify details 4. Save changes     | Changes save and display with success message                             | Works as expected | Pass   |
| Remove workout               | 1\. Open workout details 2. Click delete button 3. Confirm deletion                 | Workout removes from list with success message                            | Works as expected | Pass   |
| Update profile info          | 1\. Navigate to profile 2. Click edit profile 3. Update information 4. Save changes | Changes save and display with success message                             | Works as expected | Pass   |
| Change profile image         | 1\. Go to profile 2. Click profile image 3. Select new image 4. Confirm upload      | Image uploads and displays with success message                           | Works as expected | Pass   |
| Follow another user          | 1\. View user profile 2. Click follow button 3. Confirm follow                      | Follow status updates and user appears in following list                  | Works as expected | Pass   |
| Add comment                  | 1\. Open workout post 2. Type comment 3. Submit comment                             | Comment posts and appears in list                                         | Works as expected | Pass   |
| Test mobile layout           | 1\. Open site on mobile 2. Navigate features 3. Test interactions                   | Layout adjusts with all features accessible                               | Works as expected | Pass   |
| Test tablet layout           | 1\. Open site on tablet 2. Navigate features 3. Test interactions                   | Layout adjusts with proper spacing                                        | Works as expected | Pass   |
| View workout history         | 1\. Navigate to workout history 2. Apply filters if needed                          | List displays with correct information and pagination                     | Works as expected | Pass   |
| Set notification preferences | 1\. Go to settings 2. Navigate to notifications 3. Update preferences               | Settings save and notifications update                                    | Works as expected | Pass   |
| View social feed             | 1\. Navigate to social feed 2. Scroll through posts                                 | Feed loads with posts and images                                          | Works as expected | Pass   |
| Share workout                | 1\. Complete workout 2. Click share button 3. Add caption if desired                | Workout posts to feed and appears for followers                           | Works as expected | Pass   |
| React to shared workout      | 1\. View shared workout 2. Click like/comment                                       | Reaction registers and updates in real-time                               | Works as expected | Pass   |


## Contents
1. [API Tests](#api-tests)
2. [Social Tests](#social-tests)
3. [Workout Tests](#workout-tests)

## Test Results Summary
```bash
Found 18 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.......OK
```

## API Tests

### UserProfileModelTestCase
```python
def test_user_profile_creation(self):
    """Tests automatic profile creation when user is created"""
    profile = UserProfile.objects.get(user=self.user)
    self.assertIsNotNone(profile)
    self.assertEqual(profile.user, self.user)

def test_date_of_birth_validation(self):
    """Tests that date of birth cannot be in the future"""
    profile = UserProfile.objects.get(user=self.user)
    profile.date_of_birth = date.today() + timedelta(days=1)  # Future date
    with self.assertRaises(Exception):
        profile.clean()
```

### UserProfileAPITestCase
```python
def test_retrieve_user_profile(self):
    """Tests retrieving a user profile"""
    url = reverse("api:profile-detail", kwargs={"pk": self.profile.id})
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["username"], "testuser")

def test_update_user_profile(self):
    """Tests updating a user profile"""
    url = reverse("api:profile-detail", kwargs={"pk": self.profile.id})
    response = self.client.patch(url, {"bio": "Updated bio"})
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.profile.refresh_from_db()
    self.assertEqual(self.profile.bio, "Updated bio")

def test_upload_profile_image(self):
    """Tests profile image upload functionality"""
    url = reverse("api:profile-upload-image", kwargs={"pk": self.profile.id})
    with open(image_path, "rb") as image_file:
        image_data = SimpleUploadedFile(
            name="test_image.png",
            content=image_file.read(),
            content_type="image/png"
        )
        response = self.client.post(url, {"profile_image": image_data}, format="multipart")
    self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## Social Tests

### SocialModelTests
```python
def test_workout_post_creation(self):
    """Tests WorkoutPost model creation"""
    self.assertEqual(self.workout_post.user, self.user1)
    self.assertEqual(self.workout_post.workout, self.workout)
    self.assertTrue(isinstance(self.workout_post, WorkoutPost))
    self.assertEqual(str(self.workout_post), f"{self.user1.username}'s cardio workout")

def test_like_creation(self):
    """Tests Like model creation"""
    like = Like.objects.create(user=self.user2, post=self.workout_post)
    self.assertEqual(like.user, self.user2)
    self.assertEqual(like.post, self.workout_post)
    self.assertTrue(isinstance(like, Like))

def test_comment_creation(self):
    """Tests Comment model creation"""
    comment = Comment.objects.create(
        user=self.user2,
        post=self.workout_post,
        content="Great workout!"
    )
    self.assertEqual(comment.user, self.user2)
    self.assertEqual(comment.post, self.workout_post)
    self.assertEqual(comment.content, "Great workout!")
    self.assertTrue(isinstance(comment, Comment))
```

### SocialViewTests
```python
def test_list_workout_posts(self):
    """Tests listing workout posts"""
    url = reverse('social:feed-list')
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.data['results']), 1)

def test_create_workout_post(self):
    """Tests creating a workout post"""
    url = reverse('social:feed-list')
    data = {'workout_id': self.workout.id}
    response = self.client.post(url, data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

def test_like_workout_post(self):
    """Tests liking and unliking a workout post"""
    url = reverse('social:feed-like', kwargs={'pk': self.workout_post.id})
    # Test liking
    response = self.client.post(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['status'], 'liked')
    # Test unliking
    response = self.client.post(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['status'], 'unliked')

def test_comment_on_post(self):
    """Tests commenting on a workout post"""
    url = reverse('social:feed-comments', kwargs={'pk': self.workout_post.id})
    data = {'content': 'Great workout!'}
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data['content'], 'Great workout!')
```

## Workout Tests

### WorkoutTests
```python
def test_create_workout(self):
    """Tests creating a new workout"""
    response = self.client.post(reverse('workouts:workout-list'), self.workout_data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(Workout.objects.count(), 2)
    self.assertEqual(response.data['title'], 'Morning Run')

def test_list_workouts(self):
    """Tests listing workouts for the logged-in user"""
    response = self.client.get(reverse('workouts:workout-list'))
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.data['results']), 1)

def test_get_workout_detail(self):
    """Tests retrieving a specific workout"""
    response = self.client.get(
        reverse('workouts:workout-detail', kwargs={'pk': self.workout.id})
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['title'], 'Morning Run')
    self.assertEqual(response.data['duration'], 30)

def test_update_workout(self):
    """Tests updating a workout"""
    update_data = {
        "title": "Updated Run",
        "duration": 35
    }
    response = self.client.patch(
        reverse('workouts:workout-detail', kwargs={'pk': self.workout.id}),
        update_data
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.workout.refresh_from_db()
    self.assertEqual(self.workout.title, "Updated Run")
    self.assertEqual(self.workout.duration, 35)

def test_delete_workout(self):
    """Tests deleting a workout"""
    response = self.client.delete(
        reverse('workouts:workout-detail', kwargs={'pk': self.workout.id})
    )
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    self.assertEqual(Workout.objects.count(), 0)

def test_unauthorized_workout_access(self):
    """Tests unauthorized access to another user's workout"""
    other_workout = Workout.objects.create(
        owner=self.other_user,
        title="Other's Workout",
        workout_type="strength",
        duration=40,
        intensity="high"
    )
    
    # Try to update another user's workout
    response = self.client.patch(
        reverse('workouts:workout-detail', kwargs={'pk': other_workout.id}),
        {"title": "Unauthorized Update"}
    )
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    # Try to delete another user's workout
    response = self.client.delete(
        reverse('workouts:workout-detail', kwargs={'pk': other_workout.id})
    )
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

## Test Coverage

To run tests with coverage:
```bash
coverage run manage.py test
coverage report
coverage html  # For detailed HTML report
```

## Running Tests
To run all tests:
```bash
python manage.py test
```

To run tests for a specific app:
```bash
python manage.py test api
python manage.py test social
python manage.py test workouts
```

To run a specific test case:
```bash
python manage.py test api.tests.UserProfileAPITestCase
```

## Validation
All test files have been validated against PEP8 standards using pycodestyle. See validation screenshots in the README.md file.