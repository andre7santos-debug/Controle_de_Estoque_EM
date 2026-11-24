
from django.contrib import admin
from .models import (
    Categoria,
    Material,
    Equipamento,
    Movimentacao,
    Emprestimo,
    Manutencao,
)


class ConsultaAdmin(admin.ModelAdmin):

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Categoria)
class CategoriaAdmin(ConsultaAdmin):

    list_display = ("id", "nome", "descricao")
    search_fields = ("nome",)


@admin.register(Material)
class MaterialAdmin(ConsultaAdmin):

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
class EquipamentoAdmin(ConsultaAdmin):

    list_display = (
        "id",
        "nome",
        "categoria",
        "numero_patrimonio",
        "status",
    )

    search_fields = ("nome", "numero_patrimonio")
    list_filter = ("categoria", "status")


@admin.register(Movimentacao)
class MovimentacaoAdmin(ConsultaAdmin):

    list_display = (
        "id",
        "material",
        "tipo",
        "quantidade",
        "data",
        "responsavel",
    )

    search_fields = ("material__nome", "responsavel__username")
    list_filter = ("tipo", "data")
    ordering = ("-data",)


@admin.register(Emprestimo)
class EmprestimoAdmin(ConsultaAdmin):

    list_display = (
        "id",
        "equipamento",
        "solicitante",
        "data_emprestimo",
        "previsao_devolucao",
        "data_devolucao",
        "responsavel",
    )

    search_fields = ("equipamento__nome", "solicitante")
    list_filter = ("data_emprestimo", "previsao_devolucao")
    ordering = ("-data_emprestimo",)


@admin.register(Manutencao)
class ManutencaoAdmin(ConsultaAdmin):

    list_display = (
        "id",
        "equipamento",
        "motivo",
        "data_inicio",
        "data_fim",
        "responsavel",
    )

    search_fields = ("equipamento__nome", "motivo")
    list_filter = ("data_inicio", "data_fim")
    ordering = ("-data_inicio",)


admin.site.site_header = "Administração do Estoque Maker"
admin.site.site_title = "Estoque Maker"
admin.site.index_title = "Painel de administração"
admin.site.has_permission = lambda request: (
    request.user.is_active and request.user.is_superuser
)
