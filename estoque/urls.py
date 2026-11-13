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
]
