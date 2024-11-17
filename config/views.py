from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.urls import reverse

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root view showing available endpoints."""
    return Response({
        'profiles': {
            'list': request.build_absolute_uri(reverse('profile-list')),
            'detail': request.build_absolute_uri(reverse('profile-detail', kwargs={'pk': 1})),  # Example with a pk
        },
        'goals': {
            'list': request.build_absolute_uri(reverse('goal-list')),
            'create': request.build_absolute_uri(reverse('goal-list')),  # Can use the same URL for creating
            'detail': request.build_absolute_uri(reverse('goal-detail', kwargs={'pk': 1})),
        },
        'auth': {
            'login': request.build_absolute_uri(reverse('rest_login')),
            'logout': request.build_absolute_uri(reverse('rest_logout')),
            'register': request.build_absolute_uri(reverse('rest_register')),  # Register via dj_rest_auth
            'user_details': request.build_absolute_uri(reverse('rest_user_details')),
        },
        'workouts': {
            'list': request.build_absolute_uri(reverse('workouts:workout-list')),
            'statistics': request.build_absolute_uri(reverse('workouts:workout-statistics')),
            'summary': request.build_absolute_uri(reverse('workouts:workout-summary')),
        },
        'social': {
            'feed': request.build_absolute_uri(reverse('social:feed-list')),
            'feed_create': request.build_absolute_uri(reverse('social:feed-list')),
            'comments': request.build_absolute_uri(reverse('social:comments-list')),
            'endpoints': {
                'like_post': '/api/social/feed/{id}/like/',
                'post_comments': '/api/social/feed/{id}/comments/',
                'delete_comment': '/api/social/comments/{id}/',
            },
        },
        'documentation': {
            'swagger': request.build_absolute_uri(reverse('schema-swagger-ui')),
            'redoc': request.build_absolute_uri(reverse('schema-redoc')),
        }
    })
