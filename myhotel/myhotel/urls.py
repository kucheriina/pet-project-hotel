"""
URL configuration for myhotel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from booking.views import BookingViewSet
from catalog.views import RoomViewSet

schema_view = get_schema_view(
    openapi.Info(
        title='Hotel Booking API',
        default_version='v1',
        description='API документация для проекта бронирования номеров в отеле',
    ),
    public=True,
    permission_classes=[permissions.AllowAny,],
)

router = DefaultRouter()
router.register(r'catalog', RoomViewSet, basename='room')
router.register(r'booking', BookingViewSet, basename='booking')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)