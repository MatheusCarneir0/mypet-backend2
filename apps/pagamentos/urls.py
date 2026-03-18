# apps/pagamentos/urls.py
from rest_framework.routers import DefaultRouter
from .views import TransacaoPagamentoViewSet, FormaPagamentoViewSet

router = DefaultRouter()
router.register('transacoes', TransacaoPagamentoViewSet, basename='transacao-pagamento')
# #6: rota pública (IsAuthenticated) para clientes listarem formas de pagamento ao agendar
router.register('formas', FormaPagamentoViewSet, basename='forma-pagamento')

urlpatterns = router.urls

