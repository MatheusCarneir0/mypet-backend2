# apps/relatorios/views.py
"""
Views para geração e listagem de relatórios.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from .models import Relatorio
from .serializers import RelatorioSerializer, RelatorioCreateSerializer
from .services import RelatorioService
from apps.core.permissions import IsAdministrador
from apps.swagger.relatorios import relatorio_view_schema


@relatorio_view_schema
class RelatorioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para relatórios.
    """
    queryset = Relatorio.objects.all().select_related('administrador')
    serializer_class = RelatorioSerializer
    permission_classes = [IsAuthenticated, IsAdministrador]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RelatorioCreateSerializer
        return RelatorioSerializer
    
    def create(self, request):
        """
        Gera um novo relatório.
        """
        serializer = RelatorioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            relatorio = RelatorioService.gerar_relatorio(
                administrador=request.user,
                tipo=serializer.validated_data['tipo'],
                formato=serializer.validated_data['formato'],
                filtros=dict(serializer.validated_data)
            )
            
            return Response(
                RelatorioSerializer(relatorio).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """
        Faz download de um relatório.
        """
        relatorio = self.get_object()
        
        if not relatorio.arquivo:
            return Response({
                'error': 'Arquivo não encontrado.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(
            relatorio.arquivo.open('rb'),
            as_attachment=True,
            filename=f'{relatorio.get_tipo_display()}_{relatorio.id}.{relatorio.formato.lower()}'
        )
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """
        Retorna dados para dashboard gerencial.
        """
        try:
            data = RelatorioService.obter_dashboard_data()
            return Response(data)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
