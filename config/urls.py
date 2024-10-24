from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from dj_rest_auth.views import LoginView, LogoutView
from api.views import UserRegistrationView, api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include([
        path('', include('api.urls')),
        path('', include('workouts.urls')),
        path('', include('social.urls')),
        path('auth/', include([
            path('register/', UserRegistrationView.as_view(), name='rest_register'),
            path('login/', LoginView.as_view(), name='rest_login'),
            path('logout/', LogoutView.as_view(), name='rest_logout'),
            path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        ])),
    ])),
]