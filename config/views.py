from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.urls import reverse

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root view showing available endpoints."""
    return Response({
        'profiles': {
            'list': request.build_absolute_uri(reverse('api:profile-list')),
            'detail': request.build_absolute_uri(
                reverse('api:profile-detail', kwargs={'pk': 1})),
        },
        'auth': {
            'login': request.build_absolute_uri(reverse('rest_login')),
            'logout': request.build_absolute_uri(reverse('rest_logout')),
            'register': request.build_absolute_uri(
                reverse('rest_register')),
        },
        'workouts': {
            'list': request.build_absolute_uri(
                reverse('workouts:workout-list')),
            'statistics': request.build_absolute_uri(
                reverse('workouts:workout-statistics')),
        },
        'social': {
            'feed': request.build_absolute_uri(reverse('social:feed-list')),
        },
        'documentation': {
            'swagger': request.build_absolute_uri(reverse('swagger-ui')),
            'redoc': request.build_absolute_uri(reverse('redoc')),
        }
    })