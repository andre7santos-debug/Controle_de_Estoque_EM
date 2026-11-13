from django.contrib import admin
from .models import Categoria, Material, Equipamento


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "descricao")
    search_fields = ("nome",)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "categoria",
        "quantidade",
        "unidade_medida",
        "estoque_minimo",
    )
    search_fields = ("nome",)
    list_filter = ("categoria",)


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "categoria",
        "numero_patrimonio",
        "status",
    )
    search_fields = ("nome", "numero_patrimonio")
    list_filter = ("categoria", "status")
