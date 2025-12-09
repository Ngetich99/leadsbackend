from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger / OpenAPI schema view
schema_view = get_schema_view(
    openapi.Info(
        title="CRM Backend API",
        default_version='v1',
        description="API for CRM system with Vue.js frontend integration",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@crm.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Root view: redirect to Swagger UI
def root(request):
    return redirect('schema-swagger-ui')

urlpatterns = [
    # Root URL
    path('', root),

    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenObtainPairView.as_view(), name='token_verify'),

    # API endpoints
    path('api/', include('accounts.urls')),
    path('api/', include('leads.urls')),

    # API Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
