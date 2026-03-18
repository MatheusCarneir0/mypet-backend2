# apps/funcionarios/urls.py
from rest_framework.routers import DefaultRouter
from .views import FuncionarioViewSet, HorarioTrabalhoViewSet

router = DefaultRouter()
router.register('horarios', HorarioTrabalhoViewSet, basename='horario-trabalho')
router.register('', FuncionarioViewSet, basename='funcionario')

urlpatterns = router.urls

