# apps/relatorios/urls.py
from rest_framework.routers import DefaultRouter
from .views import RelatorioViewSet

router = DefaultRouter()
router.register('', RelatorioViewSet, basename='relatorio')

urlpatterns = router.urls

