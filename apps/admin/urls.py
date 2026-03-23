# apps/admin/urls.py
"""
URLs para rotas administrativas.
Agrupa dashboard, relatórios e formas de pagamento.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardView, RelatorioGerarView
from .views import AdminFormaPagamentoViewSet

app_name = 'backoffice'

# Router para ViewSets

router = DefaultRouter()

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('relatorios/gerar/', RelatorioGerarView.as_view(), name='relatorios-gerar'),
    path('', include(router.urls)),
]

