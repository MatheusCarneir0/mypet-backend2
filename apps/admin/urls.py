# apps/admin/urls.py
"""
URLs para rotas administrativas.
Agrupa dashboard, relatórios, funcionários e formas de pagamento.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardView, RelatorioGerarView
from apps.funcionarios.views import FuncionarioViewSet
from .views import AdminFormaPagamentoViewSet

app_name = 'admin'

# Router para ViewSets
router = DefaultRouter()
router.register('funcionarios', FuncionarioViewSet, basename='admin-funcionario')
router.register('formas-pagamento', AdminFormaPagamentoViewSet, basename='admin-forma-pagamento')

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('relatorios/gerar/', RelatorioGerarView.as_view(), name='relatorios-gerar'),
    path('', include(router.urls)),
]

