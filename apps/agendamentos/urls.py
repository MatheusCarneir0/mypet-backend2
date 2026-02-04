# apps/agendamentos/urls.py
from rest_framework.routers import SimpleRouter
from .views import AgendamentoViewSet

router = SimpleRouter()
router.register('', AgendamentoViewSet, basename='agendamento')

urlpatterns = router.urls

