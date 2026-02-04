# apps/pagamentos/urls.py
from rest_framework.routers import DefaultRouter
from .views import TransacaoPagamentoViewSet

router = DefaultRouter()
router.register('transacoes', TransacaoPagamentoViewSet, basename='transacao-pagamento')

urlpatterns = router.urls

