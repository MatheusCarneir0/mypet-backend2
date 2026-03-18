# apps/funcionarios/models.py
"""
Modelo de Funcionário.
Estende Usuario com informações específicas de funcionários.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import Usuario
from apps.core.models import BaseModel


class Funcionario(BaseModel):
    """
    Modelo de Funcionário da FarmaVet.
    Relacionamento 1:1 com Usuario.
    """
    class Cargo(models.TextChoices):
        ATENDENTE = 'ATENDENTE', _('Atendente')
        TOSADOR = 'TOSADOR', _('Tosador')
        VETERINARIO = 'VETERINARIO', _('Veterinário')
        GERENTE = 'GERENTE', _('Gerente')
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='funcionario',
        verbose_name=_('Usuário')
    )
    cargo = models.CharField(
        _('Cargo'),
        max_length=20,
        choices=Cargo.choices
    )
    horario_trabalho = models.CharField(
        _('Horário de Trabalho'),
        max_length=100,
        help_text='Ex: Segunda a Sexta, 08:00-17:00'
    )

    class Meta:
        db_table = 'funcionarios'
        verbose_name = _('Funcionário')
        verbose_name_plural = _('Funcionários')
        ordering = ['usuario__nome']
        indexes = [
            models.Index(fields=['cargo', 'ativo']),
        ]
    
    def __str__(self):
        return f'{self.usuario.nome} - {self.get_cargo_display()}'

    @property
    def total_atendimentos(self):
        """Retorna o número total de atendimentos realizados."""
        return self.agendamentos.filter(status='CONCLUIDO').count()

    @staticmethod
    def _parse_horario_trabalho_string(horario_str):
        """
        Parser simples para strings de horário como:
        - "Segunda a Sexta, 08:00-17:00"
        - "Segunda a Domingo, 08:00-18:00"
        - "8h as 18h"
        Retorna lista de tuplas (dia_semana_int, hora_inicio(time), hora_fim(time)).
        """
        if not horario_str or not isinstance(horario_str, str):
            return []

        import re
        from datetime import datetime, time

        s = horario_str.strip().lower()
        # Normalizações
        s = s.replace('às', 'as')
        s = s.replace('–', '-')
        s = s.replace('—', '-')

        parts = [p.strip() for p in s.split(',') if p.strip()]
        days_part = None
        times_part = None
        if len(parts) == 1:
            # Pode ser apenas dias ou apenas horas. Tentaremos inferir.
            if re.search(r'\d', parts[0]):
                times_part = parts[0]
            else:
                days_part = parts[0]
        else:
            days_part = parts[0]
            times_part = parts[1]

        # Map de nomes de dia para int conforme DiaSemana (DOMINGO=0, SEGUNDA=1,...)
        day_map = {
            'domingo': 0, 'dom': 0,
            'segunda': 1, 'segunda-feira': 1, 'seg': 1,
            'terca': 2, 'terça': 2, 'terca-feira': 2, 'ter': 2,
            'quarta': 3, 'quarta-feira': 3, 'qua': 3,
            'quinta': 4, 'quinta-feira': 4, 'qui': 4,
            'sexta': 5, 'sexta-feira': 5, 'sex': 5,
            'sabado': 6, 'sábado': 6, 'sab': 6
        }

        day_ranges = []
        if days_part:
            # Exemplos: 'segunda a sexta', 'segunda-feira a sexta-feira', 'segunda'
            # Remover plurais/abreviações
            days_part = days_part.replace('dias', '').strip()
            # Substituir ' a ' ou ' - ' por ' a ' para unificar
            days_part = days_part.replace('-', ' a ')
            # Procurar range
            if ' a ' in days_part:
                try:
                    start, end = [d.strip() for d in days_part.split(' a ', 1)]
                    start_key = start
                    end_key = end
                    if start_key in day_map and end_key in day_map:
                        start_idx = day_map[start_key]
                        end_idx = day_map[end_key]
                        # Criar lista inclusiva (cuidando de wrap se necessário)
                        if start_idx <= end_idx:
                            day_ranges = list(range(start_idx, end_idx + 1))
                        else:
                            # ex: sexta a segunda
                            day_ranges = list(range(start_idx, 7)) + list(range(0, end_idx + 1))
                    else:
                        # Tentar palavras individuais
                        tokens = re.findall(r'[a-zá-ú]+', days_part)
                        for t in tokens:
                            if t in day_map:
                                day_ranges.append(day_map[t])
                except Exception:
                    day_ranges = []
            else:
                # Lista de dias separados por / ou espaço
                tokens = re.findall(r'[a-zá-ú]+', days_part)
                for t in tokens:
                    if t in day_map and day_map[t] not in day_ranges:
                        day_ranges.append(day_map[t])
        
        # Default se não foi identificado dia: segunda a sábado
        if not day_ranges:
            day_ranges = [1,2,3,4,5,6]

        # Parse de horas
        start_time = time(7, 0)
        end_time = time(17, 30)
        if times_part:
            t = times_part
            # Normalizar ' as ' para '-' e 'h' para ':00'
            t = t.replace(' as ', '-')
            t = t.replace(' as', '-')
            t = t.replace('as ', '-')
            t = t.replace('h', ':00')
            t = t.replace('.', ':')
            t = t.replace(' ', '')
            # Agora separar por '-'
            if '-' in t:
                a, b = t.split('-', 1)
                def _parse_time(tok):
                    tok = tok.strip()
                    fmts = ['%H:%M', '%H%M', '%H']
                    for f in fmts:
                        try:
                            dt = datetime.strptime(tok, f)
                            return time(dt.hour, dt.minute)
                        except Exception:
                            continue
                    return None
                st = _parse_time(a)
                en = _parse_time(b)
                if st:
                    start_time = st
                if en:
                    end_time = en

        results = []
        # Intervalo de almoço padrão: 12:00-13:00
        # Se a jornada cruza esse intervalo, dividir em dois turnos
        almoco_inicio = time(12, 0)
        almoco_fim = time(13, 0)
        for d in day_ranges:
            if start_time < almoco_inicio and end_time > almoco_fim:
                # Turno manhã: start_time até 12:00
                results.append((d, start_time, almoco_inicio))
                # Turno tarde: 13:00 até end_time
                results.append((d, almoco_fim, end_time))
            else:
                results.append((d, start_time, end_time))

        return results

    def save(self, *args, **kwargs):
        """
        Ao salvar funcionário, tentar normalizar/criar horários em HorarioTrabalho
        a partir do campo `horario_trabalho` (string legível). Isso mantém o sistema
        consistente e permite o cálculo correto de disponibilidade.
        """
        super().save(*args, **kwargs)

        try:
            # Importar localmente para evitar problemas de referência circular durante a carga do módulo
            from apps.funcionarios.models import HorarioTrabalho
            parsed = self._parse_horario_trabalho_string(self.horario_trabalho)
            if parsed:
                # Remover antigos e criar novos registros
                HorarioTrabalho.objects.filter(funcionario=self).delete()
                to_create = []
                for dia, inicio, fim in parsed:
                    to_create.append(HorarioTrabalho(
                        funcionario=self,
                        dia_semana=dia,
                        hora_inicio=inicio,
                        hora_fim=fim
                    ))
                HorarioTrabalho.objects.bulk_create(to_create)
        except Exception:
            # Não falhar a criação do funcionário se por algum motivo o parser der erro
            pass


class HorarioTrabalho(BaseModel):
    """
    Representa os horários de expediente de um funcionário para dias da semana.
    """
    class DiaSemana(models.IntegerChoices):
        DOMINGO = 0, _('Domingo')
        SEGUNDA = 1, _('Segunda-feira')
        TERCA = 2, _('Terça-feira')
        QUARTA = 3, _('Quarta-feira')
        QUINTA = 4, _('Quinta-feira')
        SEXTA = 5, _('Sexta-feira')
        SABADO = 6, _('Sábado')

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='horarios_trabalho',
        verbose_name=_('Funcionário')
    )
    dia_semana = models.IntegerField(
        _('Dia da Semana'),
        choices=DiaSemana.choices
    )
    hora_inicio = models.TimeField(_('Hora de Início do Expediente'))
    hora_fim = models.TimeField(_('Hora de Fim do Expediente'))

    class Meta:
        db_table = 'horarios_trabalho'
        verbose_name = _('Horário de Trabalho')
        verbose_name_plural = _('Horários de Trabalho')
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ['funcionario', 'dia_semana', 'hora_inicio', 'hora_fim']

    def __str__(self):
        return f'{self.funcionario.usuario.nome} - {self.get_dia_semana_display()} ({self.hora_inicio.strftime("%H:%M")} às {self.hora_fim.strftime("%H:%M")})'


