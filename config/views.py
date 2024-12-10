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
            'detail': request.build_absolute_uri(
                reverse('profile-detail', kwargs={'pk': 1})),
        },
        'auth': {
            'login': request.build_absolute_uri(reverse('rest_login')),
            'logout': request.build_absolute_uri(reverse('rest_logout')),
            'register': request.build_absolute_uri(reverse('rest_register')),
            'user_details': request.build_absolute_uri(reverse(
                'rest_user_details')),
        },
        'workouts': {
            'list': request.build_absolute_uri(
                reverse('workouts:workout-list')),
            'statistics': request.build_absolute_uri(reverse(
                'workouts:workout-statistics')),
            'detail': request.build_absolute_uri(reverse(
                'workouts:workout-detail', kwargs={'pk': 1})),
        },
        'social': {
            'feed': request.build_absolute_uri(reverse('social:feed-list')),
            'feed_create': request.build_absolute_uri(reverse(
                'social:feed-list')),
            'comments': request.build_absolute_uri(reverse(
                'social:comments-list')),
            'endpoints': {
                'like_post': request.build_absolute_uri(reverse(
                    'social:feed-like', kwargs={'pk': 1})),
                'post_comments': request.build_absolute_uri(reverse(
                    'social:feed-comments', kwargs={'pk': 1})),
            },
        },
        'documentation': {
            'swagger': request.build_absolute_uri(reverse(
                'schema-swagger-ui')),
            'redoc': request.build_absolute_uri(reverse('schema-redoc')),
        }
    })
