# apps/funcionarios/admin.py
from django.contrib import admin
from .models import Funcionario


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'cargo', 'horario_trabalho', 'ativo', 'data_criacao']
    list_filter = ['cargo', 'ativo', 'data_criacao']
    search_fields = ['usuario__nome', 'usuario__email']
    readonly_fields = ['data_criacao', 'data_atualizacao']

