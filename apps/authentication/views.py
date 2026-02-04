# apps/authentication/views.py
"""
Views para autenticação.
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Usuario
from .serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioCreateSerializer,
    GoogleLoginSerializer,
)
from .services import AuthenticationService
from apps.swagger.authentication import (
    obter_token,
    refresh_token,
    registro,
    google_login
)


@obter_token
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View customizada para obtenção de token JWT.
    """
    serializer_class = CustomTokenObtainPairSerializer


@refresh_token
class CustomTokenRefreshView(TokenRefreshView):
    """
    View customizada para renovação de token JWT.
    """
    pass


@registro
class RegistroView(generics.CreateAPIView):
    """
    View para registro de novo usuário.
    Endpoint público.
    """
    serializer_class = UsuarioCreateSerializer
    permission_classes = [AllowAny]


@google_login
class GoogleLoginView(APIView):
    """
    View para login social com Google.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Autentica ou cria usuário via Google OAuth.
        """
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Aqui você implementaria a validação do token do Google
            # Por enquanto, vamos criar/login básico
            email = serializer.validated_data['email']
            nome = serializer.validated_data['nome']
            foto_url = serializer.validated_data.get('foto_url', '')
            
            # Buscar ou criar usuário
            usuario, created = Usuario.objects.get_or_create(
                email=email,
                defaults={
                    'nome': nome,
                    'telefone': '',  # Pode ser preenchido depois
                    'tipo_usuario': Usuario.TipoUsuario.CLIENTE
                }
            )
            
            if not created:
                # Atualizar nome se necessário
                if usuario.nome != nome:
                    usuario.nome = nome
                    usuario.save()
            
            # Gerar token JWT
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(usuario)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'usuario': UsuarioSerializer(usuario).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)



