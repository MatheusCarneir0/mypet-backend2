# apps/servicos/admin.py
from django.contrib import admin
from .models import Servico, ServicoCargo


class ServicoCargoInline(admin.TabularInline):
    model = ServicoCargo
    extra = 1
    fields = ['cargo']


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'duracao_minutos', 'lista_cargos', 'ativo', 'data_criacao']
    list_filter = ['cargos__cargo', 'ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    inlines = [ServicoCargoInline]

    def lista_cargos(self, obj):
        return ', '.join(c.get_cargo_display() for c in obj.cargos.all())
    lista_cargos.short_description = 'Cargos'


@admin.register(ServicoCargo)
class ServicoCargoAdmin(admin.ModelAdmin):
    list_display = ['servico', 'cargo']
    list_filter = ['cargo']
    search_fields = ['servico__nome']
