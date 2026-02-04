# apps/me/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
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

        try:
            usuario = request.user
            usuario.foto = serializer.validated_data["foto"]
            usuario.save()

            return Response(
                {
                    "message": "Foto atualizada com sucesso.",
                    "usuario": UsuarioSerializer(usuario).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
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

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

