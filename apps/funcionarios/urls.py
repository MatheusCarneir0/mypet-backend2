# apps/funcionarios/urls.py
from rest_framework.routers import DefaultRouter
from .views import FuncionarioViewSet

router = DefaultRouter()
router.register('', FuncionarioViewSet, basename='funcionario')

urlpatterns = router.urls

