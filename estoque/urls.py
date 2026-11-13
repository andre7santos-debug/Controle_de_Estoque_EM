from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "materiais/",
        views.lista_materiais,
        name="lista_materiais"
    ),

    path(
        "materiais/novo/",
        views.cadastrar_material,
        name="cadastrar_material"
    ),

    path(
        "materiais/<int:pk>/editar/",
        views.editar_material,
        name="editar_material"
    ),

    path(
        "materiais/<int:pk>/excluir/",
        views.excluir_material,
        name="excluir_material"
    ),
        path(
        "categorias/",
        views.lista_categorias,
        name="lista_categorias"
    ),
    path(
        "categorias/nova/",
        views.cadastrar_categoria,
        name="cadastrar_categoria"
    ),
    path(
        "categorias/<int:pk>/editar/",
        views.editar_categoria,
        name="editar_categoria"
    ),
    path(
        "categorias/<int:pk>/excluir/",
        views.excluir_categoria,
        name="excluir_categoria"
    ),
    path(
        "equipamentos/",
        views.lista_equipamentos,
        name="lista_equipamentos"
    ),
    path(
        "equipamentos/novo/",
        views.cadastrar_equipamento,
        name="cadastrar_equipamento"
    ),
    path(
        "equipamentos/<int:pk>/editar/",
        views.editar_equipamento,
        name="editar_equipamento"
    ),
    path(
        "equipamentos/<int:pk>/excluir/",
        views.excluir_equipamento,
        name="excluir_equipamento"
    ),
    path(
    "movimentacoes/nova/",
    views.registrar_movimentacao,
    name="registrar_movimentacao"
    ),
]
