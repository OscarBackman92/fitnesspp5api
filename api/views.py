import logging
import traceback
from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.reverse import reverse
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserProfile, Goal
from .serializers import UserProfileSerializer, UserRegistrationSerializer, UserInfoSerializer, GoalSerializer
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'name']

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            if created:
                logger.info(f"Created new UserProfile for user: {request.user.username}")
            serializer = UserInfoSerializer(user_profile)
            data = serializer.data
            logger.info(f"User info retrieved for user: {request.user.username}")
            return Response(data)
        except Exception as e:
            logger.error(f"Error retrieving user info for {request.user.username}: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                "error": "An error occurred while retrieving user info",
                "details": str(e),
                "trace": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['PUT'])
    def update_profile_picture(self, request):
        try:
            user_profile = self.get_queryset().first()
            if 'profile_picture' in request.FILES:
                user_profile.profile_picture = request.FILES['profile_picture']
                user_profile.save()
                serializer = self.get_serializer(user_profile)
                return Response({
                    'message': 'Profile picture updated successfully',
                    'profile_picture_url': serializer.data.get('profile_picture')
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'No profile picture provided'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating profile picture for user {request.user.username}: {str(e)}")
            return Response({
                'error': 'An error occurred while updating the profile picture',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserRegistrationSerializer(user, context=self.get_serializer_context()).data,
                "message": "User Created Successfully. Now perform Login to get your token",
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'profiles': reverse('profile-list', request=request, format=format),
        'workouts': reverse('workout-list', request=request, format=format),
        'goals': reverse('goal-list', request=request, format=format),
        'register': reverse('rest_register', request=request, format=format),
        'login': reverse('rest_login', request=request, format=format),
        'logout': reverse('rest_logout', request=request, format=format),
        'token': reverse('token_obtain_pair', request=request, format=format),
        'token_refresh': reverse('token_refresh', request=request, format=format),
        'social_feed': reverse('social-feed', request=request, format=format),
        'follows': reverse('social-follow-list', request=request, format=format),
        'likes': reverse('social-like-list', request=request, format=format),
        'comments': reverse('social-comment-list', request=request, format=format),
    })

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        print("Getting goals for user:", self.request.user)  # Debug print
        return Goal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        print("Creating goal for user:", self.request.user)  # Debug print
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        print("Create request data:", request.data)  # Debug print
        return super().create(request, *args, **kwargs)
