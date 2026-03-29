# apps/authentication/views.py
"""
Views para autenticação.
"""
from rest_framework import status, generics
import logging
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .models import Usuario
from .serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .services import AuthenticationService
from .throttles import LoginRateThrottle, RegisterRateThrottle
from apps.swagger.authentication import (
    obter_token,
    refresh_token,
    registro,
)
from drf_spectacular.utils import extend_schema


@obter_token
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View customizada para obtenção de token JWT.
    Rate limiting: 5 tentativas por minuto por IP (proteção brute-force).
    """
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]


@refresh_token
class CustomTokenRefreshView(TokenRefreshView):
    """
    View customizada para renovação de token JWT.
    """
    pass


@registro
class RegistroView(generics.CreateAPIView):
    """
    View para registro público de novos clientes.
    Cria automaticamente: Usuario + Cliente + adiciona ao grupo CLIENTE.
    Rate limiting: 10 registros por hora por IP (proteção contra spam).
    Endpoint público - não requer autenticação.
    """
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def get_serializer_class(self):
        """Usa ClienteCreateSerializer para cadastro completo."""
        from apps.clientes.serializers import ClienteCreateSerializer
        return ClienteCreateSerializer


@extend_schema(tags=["Autenticação"])
class PasswordResetRequestView(APIView):
    """
    Solicita o envio de email para redefinição de senha.
    Endpoint público — não requer autenticação.
    Sempre retorna 200 para não vazar se o email existe.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        logger = logging.getLogger(__name__)
        try:
            usuario = Usuario.objects.get(email=email, is_active=True)
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)

            # URL que o frontend vai abrir para o usuário redefinir a senha
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            reset_link = f"{frontend_url}/redefinir-senha?uid={uid}&token={token}"

            # Enviar e-mail via service
            from apps.notificacoes.services import NotificacaoService
            try:
                NotificacaoService.enviar_recuperacao_senha(usuario, reset_link)
            except Exception as e:
                logger.error(f"ERRO ao enviar email de recuperação: {e}", exc_info=True)
        except Usuario.DoesNotExist:
            pass  # Silencia para não vazar e-mails cadastrados

        return Response(
            {'detail': 'Se este email estiver cadastrado, você receberá as instruções em breve.'},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Autenticação"])
class PasswordResetConfirmView(APIView):
    """
    Confirma a redefinição de senha usando uid + token gerados no passo anterior.
    Endpoint público — não requer autenticação.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG: Serializer inválido: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        senha_nova = serializer.validated_data['senha_nova']
        print(f"DEBUG: Tentando confirmar reset. UID: {uid}, Token: {token}")

        try:
            pk = force_str(urlsafe_base64_decode(uid))
            usuario = Usuario.objects.get(pk=pk, is_active=True)
        except (Usuario.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response(
                {'detail': 'Link inválido ou expirado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(usuario, token):
            return Response(
                {'detail': 'Link inválido ou expirado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario.set_password(senha_nova)
        usuario.save()

        return Response(
            {'detail': 'Senha redefinida com sucesso! Você já pode fazer login.'},
            status=status.HTTP_200_OK,
        )
