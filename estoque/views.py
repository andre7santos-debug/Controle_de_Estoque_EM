from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Material
from .forms import MaterialForm


def home(request):
    return render(request, "estoque/home.html")


def lista_materiais(request):
    materiais = Material.objects.select_related(
        "categoria"
    ).all()

    return render(
        request,
        "estoque/lista_materiais.html",
        {"materiais": materiais}
    )


@login_required(login_url="/admin/login/")
def cadastrar_material(request):
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.method == "POST":
        form = MaterialForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Material cadastrado com sucesso!"
            )
            return redirect("lista_materiais")
    else:
        form = MaterialForm()

    return render(
        request,
        "estoque/cadastrar_material.html",
        {"form": form}
    )
