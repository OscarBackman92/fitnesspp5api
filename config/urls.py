from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views import api_root

schema_view = get_schema_view(
    openapi.Info(
        title="FitPro API",
        default_version='v1',
        description=(
            "API for FitPro fitness tracking application"
        ),
        terms_of_service=(
            "https://www.google.com/policies/terms/"
        ),
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api-root'),
    path('api/', include('api.urls')),
    path('api/workouts/', include('workouts.urls')),
    path('api/social/', include('social.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),
    path(
        'api/auth/registration/',
        include('dj_rest_auth.registration.urls')
    ),
    # Swagger URLs
    path(
        'swagger<format>/',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json',
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='swagger-ui',
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='redoc',
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls', namespace='djdt'))
    ] + urlpatterns
