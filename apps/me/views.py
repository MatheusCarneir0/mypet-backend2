# apps/me/views.py
import logging
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)
from apps.authentication.models import Usuario
from apps.authentication.serializers import (
    UsuarioSerializer,
    AlterarSenhaSerializer,
    UploadFotoSerializer,
)
from apps.authentication.services import AuthenticationService
from apps.swagger.me import (
    perfil_view_schema,
    upload_foto,
    alterar_senha,
)


@perfil_view_schema
class PerfilView(generics.RetrieveUpdateAPIView):
    """
    View para visualizar e atualizar perfil do usuário autenticado.
    """
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@upload_foto
class UploadFotoView(APIView):
    """
    View para upload de foto de perfil.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Faz upload de foto de perfil do usuário.
        """
        serializer = UploadFotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        foto = serializer.validated_data["foto"]
        
        # Validar tipo
        TIPOS_PERMITIDOS = ['image/jpeg', 'image/png']
        if foto.content_type not in TIPOS_PERMITIDOS:
            return Response(
                {'error': 'Formato inválido. Use JPG ou PNG.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            usuario = request.user
            usuario.foto = foto
            usuario.save()

            return Response(
                {
                    "message": "Foto atualizada com sucesso.",
                    "usuario": UsuarioSerializer(usuario).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception('Erro ao fazer upload de foto')
            return Response(
                {"error": "Erro interno ao atualizar foto. Tente novamente."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@alterar_senha
class AlterarSenhaView(APIView):
    """
    View para alteração de senha.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AlterarSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            AuthenticationService.alterar_senha(
                usuario=request.user,
                senha_atual=serializer.validated_data["senha_atual"],
                senha_nova=serializer.validated_data["senha_nova"],
            )

            return Response(
                {"message": "Senha alterada com sucesso."},
                status=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception('Erro ao alterar senha')
            return Response(
                {"error": "Erro interno ao alterar senha. Tente novamente."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

