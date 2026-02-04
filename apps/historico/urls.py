# apps/historico/urls.py
"""
URLs para histórico de atendimentos.
"""
from rest_framework.routers import DefaultRouter
from .views import HistoricoAtendimentoViewSet

router = DefaultRouter()
router.register('', HistoricoAtendimentoViewSet, basename='historico')

urlpatterns = router.urls

