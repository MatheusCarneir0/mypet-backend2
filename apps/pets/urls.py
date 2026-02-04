# apps/pets/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import PetViewSet

router = DefaultRouter()
router.register('', PetViewSet, basename='pet')

urlpatterns = [
    path('', include(router.urls)),
    # Rota manual para o histórico sem precisar da lib nested
    path('<int:pet_pk>/historico/', PetViewSet.as_view({'get': 'historico'}), name='pet-historico'),
]