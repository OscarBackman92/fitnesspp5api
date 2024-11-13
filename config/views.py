from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.urls import reverse

@api_view(['GET'])
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
            'feed': request.build_absolute_uri(reverse('social:social-feed-list')),
            'comments': request.build_absolute_uri(reverse('social:comments-list')),
            'follows': request.build_absolute_uri(reverse('social:follows-list')),
            'stats': request.build_absolute_uri(reverse('social:stats')),
        }
    })