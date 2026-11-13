from django.shortcuts import render
from .models import Material


def home(request):
    return render(request, "estoque/home.html")


def lista_materiais(request):
    materiais = Material.objects.select_related("categoria").all()

    return render(request, "estoque/lista_materiais.html", {
        "materiais": materiais
    })
