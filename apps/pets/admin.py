# apps/pets/admin.py
from django.contrib import admin
from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cliente', 'especie', 'raca', 'idade', 'peso', 'porte', 'ativo']
    list_filter = ['especie', 'porte', 'ativo', 'data_criacao']
    search_fields = ['nome', 'cliente__usuario__nome', 'raca']
    readonly_fields = ['data_criacao', 'data_atualizacao', 'porte']

