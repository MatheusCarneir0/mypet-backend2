# apps/servicos/urls.py
from rest_framework.routers import DefaultRouter
from .views import ServicoViewSet

router = DefaultRouter()
router.register('', ServicoViewSet, basename='servico')

urlpatterns = router.urls

