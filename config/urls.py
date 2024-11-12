from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from .views import api_root

schema_view = get_schema_view(
    openapi.Info(
        title="FitTrack API",
        default_version='v1',
        description="API for FitTrack fitness tracking application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@fittrack.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root endpoint redirects to API root
    path('', api_root, name='api-root'),
    
    # Admin site
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include([
        path('', include('api.urls')),  # API root and main endpoints
        path('workouts/', include('workouts.urls', namespace='workouts')),
        path('social/', include('social.urls', namespace='social')),
        # Authentication endpoints
        path('auth/', include([
            path('', include('dj_rest_auth.urls')),
            path('registration/', include('dj_rest_auth.registration.urls')),
        ])),
    ])),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Debug toolbar (only in development)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)