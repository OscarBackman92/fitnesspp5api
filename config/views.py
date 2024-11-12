from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.urls import reverse

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root view showing available endpoints."""
    return Response({
        'profiles': request.build_absolute_uri(reverse('profile-list')),
        'goals': request.build_absolute_uri(reverse('goal-list')),
        'auth': {
            'login': request.build_absolute_uri(reverse('rest_login')),
            'logout': request.build_absolute_uri(reverse('rest_logout')),
            'register': request.build_absolute_uri(reverse('rest_register')),
            'user_details': request.build_absolute_uri(reverse('rest_user_details')),
        },
        'workouts': {
            'list': request.build_absolute_uri(reverse('workouts:workout-list')),
            'statistics': request.build_absolute_uri(reverse('workouts:workout-statistics')),
            'summary': request.build_absolute_uri(reverse('workouts:workout-summary')),
        },
        'social': {
            'feed': request.build_absolute_uri(reverse('social:socialfeed-list')),
            'share_workout': request.build_absolute_uri(reverse('social:socialfeed-share_workout')),
            'comments': request.build_absolute_uri(reverse('social:workoutcomment-list')),  # Corrected reference
            'likes': request.build_absolute_uri(reverse('social:workoutlike-list')),
            'follows': request.build_absolute_uri(reverse('social:userfollow-list')),
            'toggle_follow': request.build_absolute_uri(reverse('social:userfollow-toggle-follow')),
        },
        'documentation': {
            'swagger': request.build_absolute_uri(reverse('schema-swagger-ui')),
            'redoc': request.build_absolute_uri(reverse('schema-redoc')),
        },
    })
