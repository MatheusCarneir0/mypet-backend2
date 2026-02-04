# apps/me/urls.py
"""
URLs para rotas do perfil do usuário autenticado (me/).
User Context: Criar rotas para o usuário logado gerir o próprio perfil.
"""
from django.urls import path
from .views import PerfilView, UploadFotoView, AlterarSenhaView

app_name = 'me'

urlpatterns = [
    # GET /me/profile/ - Dados atuais (Frame 437)
    # PATCH /me/profile/ - Atualização de dados
    path('profile/', PerfilView.as_view(), name='profile'),
    
    # POST /me/profile/photo/ - Upload dedicado de foto (Frame 437)
    path('profile/photo/', UploadFotoView.as_view(), name='profile-photo'),
    
    # POST /me/change-password/ - Alteração de senha via AuthenticationService
    path('change-password/', AlterarSenhaView.as_view(), name='change-password'),
]

