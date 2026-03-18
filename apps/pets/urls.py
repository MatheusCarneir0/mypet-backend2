# apps/pets/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetViewSet

router = DefaultRouter()
router.register('', PetViewSet, basename='pet')

urlpatterns = [
    path('', include(router.urls)),
]