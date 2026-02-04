# apps/relatorios/services.py
"""
Services para geração de relatórios.
"""
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Relatorio


class RelatorioService:
    """
    Service para geração de relatórios gerenciais.
    """
    
    @staticmethod
    def gerar_relatorio(administrador, tipo, formato, filtros):
        """
        Gera um relatório baseado nos parâmetros fornecidos.
        
        Args:
            administrador: Usuário administrador solicitante
            tipo: Tipo do relatório
            formato: Formato de saída (PDF, Excel, CSV)
            filtros: Dicionário com filtros aplicados
        
        Returns:
            Relatorio: Instância do relatório gerado
        """
        # Criar registro do relatório
        relatorio = Relatorio.objects.create(
            administrador=administrador,
            tipo=tipo,
            formato=formato,
            filtros=filtros
        )
        
        # Por enquanto, apenas criar o registro
        # Em produção, implementar generators completos
        
        return relatorio
    
    @staticmethod
    def obter_dashboard_data():
        """
        Retorna dados para dashboard gerencial.
        """
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)
        
        # Agendamentos do mês
        from apps.agendamentos.models import Agendamento
        agendamentos_mes = Agendamento.objects.filter(
            data_hora__gte=inicio_mes,
            ativo=True
        )
        
        # Faturamento do mês
        from apps.historico.models import HistoricoAtendimento
        faturamento_mes = HistoricoAtendimento.objects.filter(
            data_atendimento__gte=inicio_mes
        ).aggregate(
            total=Sum('valor_pago')
        )['total'] or 0
        
        # Novos clientes do mês
        from apps.clientes.models import Cliente
        novos_clientes_mes = Cliente.objects.filter(
            data_criacao__gte=inicio_mes,
            ativo=True
        ).count()
        
        # Serviços mais realizados
        servicos_top = HistoricoAtendimento.objects.filter(
            data_atendimento__gte=inicio_mes
        ).values('tipo_servico').annotate(
            quantidade=Count('id')
        ).order_by('-quantidade')[:5]
        
        return {
            'total_agendamentos_mes': agendamentos_mes.count(),
            'faturamento_mes': float(faturamento_mes),
            'novos_clientes_mes': novos_clientes_mes,
            'servicos_top': list(servicos_top),
            'agendamentos_hoje': agendamentos_mes.filter(
                data_hora__date=hoje
            ).count(),
        }

