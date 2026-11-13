
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models.deletion import ProtectedError
from django.db import transaction
from django.db.models import F

from .models import Material, Categoria, Equipamento, Movimentacao
from .forms import MaterialForm, CategoriaForm, EquipamentoForm, MovimentacaoForm

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


@login_required(login_url="/admin/login/")
def lista_categorias(request):
    categorias = Categoria.objects.all().order_by("nome")

    return render(
        request,
        "estoque/lista_categorias.html",
        {"categorias": categorias}
    )


@login_required(login_url="/admin/login/")
def cadastrar_categoria(request):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        form = CategoriaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Categoria cadastrada com sucesso!"
            )
            return redirect("lista_categorias")
    else:
        form = CategoriaForm()

    return render(
        request,
        "estoque/form_categoria.html",
        {"form": form, "titulo": "Cadastrar categoria"}
    )


@login_required(login_url="/admin/login/")
def editar_categoria(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied

    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Categoria atualizada com sucesso!"
            )
            return redirect("lista_categorias")
    else:
        form = CategoriaForm(instance=categoria)

    return render(
        request,
        "estoque/form_categoria.html",
        {"form": form, "titulo": "Editar categoria"}
    )


@login_required(login_url="/admin/login/")
def excluir_categoria(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied

    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == "POST":
        try:
            categoria.delete()
            messages.success(
                request,
                "Categoria excluída com sucesso!"
            )
        except ProtectedError:
            messages.error(
                request,
                "Não é possível excluir esta categoria, pois "
                "ela possui materiais ou equipamentos vinculados."
            )

        return redirect("lista_categorias")

    return render(
        request,
        "estoque/excluir_categoria.html",
        {"categoria": categoria}
    )

def lista_equipamentos(request):
    equipamentos = Equipamento.objects.select_related(
        "categoria"
    ).order_by("nome")

    return render(
        request,
        "estoque/lista_equipamentos.html",
        {"equipamentos": equipamentos}
    )


@login_required(login_url="/admin/login/")
def cadastrar_equipamento(request):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        form = EquipamentoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Equipamento cadastrado com sucesso!"
            )
            return redirect("lista_equipamentos")
    else:
        form = EquipamentoForm()

    return render(
        request,
        "estoque/form_equipamento.html",
        {"form": form, "titulo": "Cadastrar equipamento"}
    )


@login_required(login_url="/admin/login/")
def editar_equipamento(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied

    equipamento = get_object_or_404(Equipamento, pk=pk)

    if request.method == "POST":
        form = EquipamentoForm(request.POST, instance=equipamento)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Equipamento atualizado com sucesso!"
            )
            return redirect("lista_equipamentos")
    else:
        form = EquipamentoForm(instance=equipamento)

    return render(
        request,
        "estoque/form_equipamento.html",
        {"form": form, "titulo": "Editar equipamento"}
    )


@login_required(login_url="/admin/login/")
def excluir_equipamento(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied

    equipamento = get_object_or_404(Equipamento, pk=pk)

    if request.method == "POST":
        equipamento.delete()
        messages.success(
            request,
            "Equipamento excluído com sucesso!"
        )
        return redirect("lista_equipamentos")

    return render(
        request,
        "estoque/excluir_equipamento.html",
        {"equipamento": equipamento}
    )

@login_required(login_url="/admin/login/")
def registrar_movimentacao(request):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        form = MovimentacaoForm(request.POST)

        if form.is_valid():
            dados = form.cleaned_data

            with transaction.atomic():
                material = Material.objects.select_for_update().get(
                    pk=dados["material"].pk
                )

                quantidade = dados["quantidade"]
                tipo = dados["tipo"]

                if tipo == "saida" and quantidade > material.quantidade:
                    form.add_error(
                        "quantidade",
                        "Estoque insuficiente para realizar esta saída."
                    )
                else:
                    variacao = (
                        quantidade if tipo == "entrada"
                        else -quantidade
                    )

                    Material.objects.filter(pk=material.pk).update(
                        quantidade=F("quantidade") + variacao
                    )

                    movimentacao = form.save(commit=False)
                    movimentacao.responsavel = request.user
                    movimentacao.save()

                    messages.success(
                        request,
                        "Movimentação registrada com sucesso!"
                    )

                    return redirect("lista_materiais")
    else:
        form = MovimentacaoForm()

    return render(
        request,
        "estoque/registrar_movimentacao.html",
        {"form": form}
    )
