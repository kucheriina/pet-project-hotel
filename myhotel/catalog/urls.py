from django.urls import path
from .views import CatalogIndexView

urlpatterns = [
    path('', CatalogIndexView.as_view(), name='catalog-index')
]
