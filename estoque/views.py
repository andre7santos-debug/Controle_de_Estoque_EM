from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import Material
from .forms import MaterialForm


def home(request):
    return render(request, "estoque/home.html")


def lista_materiais(request):
    materiais = Material.objects.select_related("categoria").all()

    return render(
        request,
        "estoque/lista_materiais.html",
        {"materiais": materiais}
    )


@login_required(login_url="/admin/login/")
def cadastrar_material(request):
    if not request.user.is_staff:
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


@login_required(login_url="/admin/login/")
def editar_material(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied

    material = get_object_or_404(Material, pk=pk)

    if request.method == "POST":
        form = MaterialForm(request.POST, instance=material)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Material atualizado com sucesso!"
            )
            return redirect("lista_materiais")
    else:
        form = MaterialForm(instance=material)

    return render(
        request,
        "estoque/editar_material.html",
        {"form": form, "material": material}
    )


@login_required(login_url="/admin/login/")
def excluir_material(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied

    material = get_object_or_404(Material, pk=pk)

    if request.method == "POST":
        material.delete()
        messages.success(
            request,
            "Material excluído com sucesso!"
        )
        return redirect("lista_materiais")

    return render(
        request,
        "estoque/excluir_material.html",
        {"material": material}
    )
