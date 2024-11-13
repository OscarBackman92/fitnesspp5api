from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.urls import reverse

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root view showing available endpoints."""
    return Response({
        'auth': {
            'login': request.build_absolute_uri(reverse('rest_login')),
            'logout': request.build_absolute_uri(reverse('rest_logout')),
            'register': request.build_absolute_uri(reverse('rest_register')),
            'user': request.build_absolute_uri(reverse('rest_user_details')),
            'password_reset': request.build_absolute_uri(reverse('rest_password_reset')),
        },
        'workouts': {
            'list': request.build_absolute_uri(reverse('workouts:workout-list')),
            'stats': request.build_absolute_uri(reverse('workouts:workout-statistics')),
            'summary': request.build_absolute_uri(reverse('workouts:workout-summary')),
        },
        'social': {
            'feed': request.build_absolute_uri(reverse('social:social-feed-list')),
            'posts': request.build_absolute_uri(reverse('social:workout-post-list')),  # Correct URL name
            'stats': request.build_absolute_uri(reverse('social:stats')),
            'follows': request.build_absolute_uri(reverse('social:follow-list')),
            'likes': request.build_absolute_uri(reverse('social:like-list')),
            'comments': request.build_absolute_uri(reverse('social:comment-list')),
            'toggle_follow': request.build_absolute_uri(reverse('social:toggle-follow')),
            'toggle_like': request.build_absolute_uri(reverse('social:toggle-like')),
        },
        'profiles': request.build_absolute_uri(reverse('profile-list')),
        'goals': request.build_absolute_uri(reverse('goal-list')),
        'docs': {
            'swagger': request.build_absolute_uri(reverse('schema-swagger-ui')),
            'redoc': request.build_absolute_uri(reverse('schema-redoc')),
        }
    })
