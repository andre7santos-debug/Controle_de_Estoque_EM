
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models.deletion import ProtectedError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from datetime import date
from .relatorios import TIPOS_RELATORIO, gerar_dados_relatorio

from .models import (
    Material,
    Categoria,
    Equipamento,
    Movimentacao,
    Emprestimo,
    Manutencao,
)

from .forms import (
    MaterialForm,
    CategoriaForm,
    EquipamentoForm,
    MovimentacaoForm,
    MaterialEdicaoForm,
    EmprestimoForm,
    ManutencaoForm,
    UsuarioCadastroForm,
    UsuarioEdicaoForm,
    UsuarioSenhaForm,
)

@login_required
def home(request):

    materiais_criticos = Material.objects.filter(
        quantidade__lte=F("estoque_minimo")
    )

    emprestimos_atrasados = Emprestimo.objects.filter(
        data_devolucao__isnull=True,
        previsao_devolucao__lt=timezone.localdate()
    ).select_related("equipamento")

    if not request.user.is_staff:
        emprestimos_atrasados = Emprestimo.objects.none()

    return render(
        request,
        "estoque/home.html",
        {
            "materiais_criticos": materiais_criticos,
            "total_alertas": materiais_criticos.count(),
            "emprestimos_atrasados": emprestimos_atrasados,
            "total_atrasados": emprestimos_atrasados.count(),
        }
    )


@login_required
def lista_materiais(request):

    materiais = Material.objects.select_related(
        "categoria"
    ).order_by("nome")

    return render(
        request,
        "estoque/lista_materiais.html",
        {"materiais": materiais}
    )


@login_required
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


@login_required
def editar_material(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied

    material = get_object_or_404(Material, pk=pk)

    if request.method == "POST":

        with transaction.atomic():

            material = get_object_or_404(
                Material.objects.select_for_update(),
                pk=pk
            )

            form = MaterialEdicaoForm(
                request.POST,
                instance=material
            )

            if form.is_valid():

                form.save()

                messages.success(
                    request,
                    "Material atualizado com sucesso!"
                )

                return redirect("lista_materiais")

    else:

        form = MaterialEdicaoForm(instance=material)

    return render(
        request,
        "estoque/editar_material.html",
        {
            "form": form,
            "material": material,
        }
    )


@login_required
def excluir_material(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied

    material = get_object_or_404(Material, pk=pk)

    if request.method == "POST":

        try:

            material.delete()

            messages.success(
                request,
                "Material excluído com sucesso!"
            )

        except ProtectedError:

            messages.error(
                request,
                "Não é possível excluir este material, "
                "pois ele possui movimentações registradas."
            )

        return redirect("lista_materiais")

    return render(
        request,
        "estoque/excluir_material.html",
        {"material": material}
    )


@login_required
def lista_categorias(request):

    categorias = Categoria.objects.all().order_by("nome")

    return render(
        request,
        "estoque/lista_categorias.html",
        {"categorias": categorias}
    )


@login_required
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
        {
            "form": form,
            "titulo": "Cadastrar categoria",
        }
    )


@login_required
def editar_categoria(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied

    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == "POST":

        form = CategoriaForm(
            request.POST,
            instance=categoria
        )

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
        {
            "form": form,
            "titulo": "Editar categoria",
            "categoria": categoria,
        }
    )


@login_required
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
                "Não é possível excluir esta categoria, "
                "pois existem materiais ou equipamentos vinculados."
            )

        return redirect("lista_categorias")

    return render(
        request,
        "estoque/excluir_categoria.html",
        {"categoria": categoria}
    )


@login_required
def lista_equipamentos(request):

    equipamentos = Equipamento.objects.select_related(
        "categoria"
    ).order_by("nome")

    return render(
        request,
        "estoque/lista_equipamentos.html",
        {"equipamentos": equipamentos}
    )


@login_required
def cadastrar_equipamento(request):

    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":

        form = EquipamentoForm(request.POST)

        if form.is_valid():

            equipamento = form.save(commit=False)
            equipamento.status = "disponivel"
            equipamento.save()

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
        {
            "form": form,
            "titulo": "Cadastrar equipamento",
        }
    )


@login_required
def editar_equipamento(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied

    equipamento = get_object_or_404(Equipamento, pk=pk)

    if request.method == "POST":

        with transaction.atomic():

            equipamento = get_object_or_404(
                Equipamento.objects.select_for_update(),
                pk=pk
            )

            status_atual = equipamento.status

            form = EquipamentoForm(
                request.POST,
                instance=equipamento
            )

            if form.is_valid():

                equipamento = form.save(commit=False)
                equipamento.status = status_atual
                equipamento.save()

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
        {
            "form": form,
            "titulo": "Editar equipamento",
            "equipamento": equipamento,
        }
    )


@login_required
def excluir_equipamento(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied

    equipamento = get_object_or_404(Equipamento, pk=pk)

    if request.method == "POST":

        try:

            equipamento.delete()

            messages.success(
                request,
                "Equipamento excluído com sucesso!"
            )

        except ProtectedError:

            messages.error(
                request,
                "Não é possível excluir este equipamento, "
                "pois ele possui empréstimos registrados."
            )

        return redirect("lista_equipamentos")

    return render(
        request,
        "estoque/excluir_equipamento.html",
        {"equipamento": equipamento}
    )


@login_required
def registrar_movimentacao(request):

    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":

        form = MovimentacaoForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                material = get_object_or_404(
                    Material.objects.select_for_update(),
                    pk=form.cleaned_data["material"].pk
                )

                tipo = form.cleaned_data["tipo"]
                quantidade = form.cleaned_data["quantidade"]

                if tipo == "saida" and quantidade > material.quantidade:

                    form.add_error(
                        "quantidade",
                        "Quantidade insuficiente em estoque."
                    )

                else:

                    if tipo == "entrada":
                        variacao = quantidade
                    else:
                        variacao = -quantidade

                    Material.objects.filter(
                        pk=material.pk
                    ).update(
                        quantidade=F("quantidade") + variacao
                    )

                    movimentacao = form.save(commit=False)
                    movimentacao.material = material
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


@login_required
def lista_movimentacoes(request):

    if not request.user.is_staff:
        raise PermissionDenied

    movimentacoes = Movimentacao.objects.select_related(
        "material",
        "responsavel"
    ).order_by("-data")

    return render(
        request,
        "estoque/lista_movimentacoes.html",
        {"movimentacoes": movimentacoes}
    )


@login_required
def registrar_emprestimo(request):

    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":

        form = EmprestimoForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                equipamento = get_object_or_404(
                    Equipamento.objects.select_for_update(),
                    pk=form.cleaned_data["equipamento"].pk
                )

                emprestimo_ativo = Emprestimo.objects.filter(
                    equipamento=equipamento,
                    data_devolucao__isnull=True
                ).exists()

                if equipamento.status != "disponivel" or emprestimo_ativo:

                    form.add_error(
                        "equipamento",
                        "Este equipamento não está disponível."
                    )

                else:

                    emprestimo = form.save(commit=False)
                    emprestimo.responsavel = request.user
                    emprestimo.equipamento = equipamento
                    emprestimo.save()

                    equipamento.status = "emprestado"
                    equipamento.save(update_fields=["status"])

                    messages.success(
                        request,
                        "Empréstimo registrado com sucesso!"
                    )

                    return redirect("lista_equipamentos")

    else:

        form = EmprestimoForm()

    return render(
        request,
        "estoque/registrar_emprestimo.html",
        {"form": form}
    )


@login_required
def lista_emprestimos(request):

    if not request.user.is_staff:
        raise PermissionDenied

    filtro = request.GET.get("situacao", "todos")

    emprestimos = Emprestimo.objects.select_related(
        "equipamento",
        "responsavel"
    ).order_by("-data_emprestimo")

    if filtro == "ativos":

        emprestimos = emprestimos.filter(
            data_devolucao__isnull=True
        )

    elif filtro == "atrasados":

        emprestimos = emprestimos.filter(
            data_devolucao__isnull=True,
            previsao_devolucao__lt=timezone.localdate()
        )

    elif filtro == "devolvidos":

        emprestimos = emprestimos.filter(
            data_devolucao__isnull=False
        )

    return render(
        request,
        "estoque/lista_emprestimos.html",
        {
            "emprestimos": emprestimos,
            "filtro": filtro,
        }
    )


@login_required
def registrar_devolucao(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied

    emprestimo = get_object_or_404(Emprestimo, pk=pk)

    if request.method == "POST":

        with transaction.atomic():

            equipamento = get_object_or_404(
                Equipamento.objects.select_for_update(),
                pk=emprestimo.equipamento_id
            )

            emprestimo = get_object_or_404(
                Emprestimo.objects.select_for_update(),
                pk=pk
            )

            if emprestimo.data_devolucao is not None:

                messages.error(
                    request,
                    "Este equipamento já foi devolvido."
                )

                return redirect("lista_emprestimos")

            emprestimo.data_devolucao = timezone.now()
            emprestimo.save(update_fields=["data_devolucao"])

            equipamento.status = "disponivel"
            equipamento.save(update_fields=["status"])

            messages.success(
                request,
                "Devolução registrada com sucesso!"
            )

        return redirect("lista_emprestimos")

    return render(
        request,
        "estoque/registrar_devolucao.html",
        {"emprestimo": emprestimo}
    )

@login_required
def registrar_manutencao(request):

    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":

        form = ManutencaoForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                equipamento = get_object_or_404(
                    Equipamento.objects.select_for_update(),
                    pk=form.cleaned_data["equipamento"].pk
                )

                manutencao_ativa = Manutencao.objects.filter(
                    equipamento=equipamento,
                    data_fim__isnull=True
                ).exists()

                emprestimo_ativo = Emprestimo.objects.filter(
                    equipamento=equipamento,
                    data_devolucao__isnull=True
                ).exists()

                if (
                    equipamento.status != "disponivel"
                    or manutencao_ativa
                    or emprestimo_ativo
                ):

                    form.add_error(
                        "equipamento",
                        "Este equipamento não está disponível."
                    )

                else:

                    manutencao = form.save(commit=False)
                    manutencao.equipamento = equipamento
                    manutencao.responsavel = request.user
                    manutencao.save()

                    equipamento.status = "manutencao"
                    equipamento.save(update_fields=["status"])

                    messages.success(
                        request,
                        "Manutenção registrada com sucesso!"
                    )

                    return redirect("lista_equipamentos")

    else:

        form = ManutencaoForm()

    return render(
        request,
        "estoque/registrar_manutencao.html",
        {"form": form}
    )

@login_required
def lista_manutencoes(request):

    if not request.user.is_staff:
        raise PermissionDenied

    filtro = request.GET.get("situacao", "todos")

    manutencoes = Manutencao.objects.select_related(
        "equipamento",
        "responsavel"
    ).order_by("-data_inicio")

    if filtro == "ativas":

        manutencoes = manutencoes.filter(
            data_fim__isnull=True
        )

    elif filtro == "finalizadas":

        manutencoes = manutencoes.filter(
            data_fim__isnull=False
        )

    else:

        filtro = "todos"

    return render(
        request,
        "estoque/lista_manutencoes.html",
        {
            "manutencoes": manutencoes,
            "filtro": filtro,
        }
    )


@login_required
def finalizar_manutencao(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied

    manutencao = get_object_or_404(Manutencao, pk=pk)

    if request.method == "POST":

        with transaction.atomic():

            equipamento = get_object_or_404(
                Equipamento.objects.select_for_update(),
                pk=manutencao.equipamento_id
            )

            manutencao = get_object_or_404(
                Manutencao.objects.select_for_update(),
                pk=pk
            )

            if manutencao.data_fim is not None:

                messages.error(
                    request,
                    "Esta manutenção já foi finalizada."
                )

                return redirect("lista_manutencoes")

            if equipamento.status != "manutencao" or Emprestimo.objects.filter(
                equipamento=equipamento,
                data_devolucao__isnull=True
            ).exists():

                messages.error(
                    request,
                    "O equipamento possui uma situação incompatível."
                )

                return redirect("lista_manutencoes")

            manutencao.data_fim = timezone.now()
            manutencao.save(update_fields=["data_fim"])

            equipamento.status = "disponivel"
            equipamento.save(update_fields=["status"])

            messages.success(
                request,
                "Manutenção finalizada com sucesso!"
            )

        return redirect("lista_manutencoes")

    return render(
        request,
        "estoque/finalizar_manutencao.html",
        {"manutencao": manutencao}
    )

def login_usuario(request):

    if request.user.is_authenticated:
        return redirect("home")

    proxima_pagina = request.POST.get(
        "next",
        request.GET.get("next", "")
    )

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:

            login(request, usuario)

            if url_has_allowed_host_and_scheme(
                url=proxima_pagina,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(proxima_pagina)

            return redirect("home")

        messages.error(
            request,
            "Usuário ou senha incorretos."
        )

    return render(
        request,
        "estoque/login.html",
        {"next": proxima_pagina}
    )


@login_required(login_url="login")
def logout_usuario(request):

    if request.method == "POST":

        logout(request)

        messages.success(
            request,
            "Você saiu do sistema com sucesso."
        )

        return redirect("login")

    return redirect("home")
@login_required
def lista_usuarios(request):

    if not request.user.is_staff:
        raise PermissionDenied

    usuarios = User.objects.all().order_by("username")

    return render(
        request,
        "estoque/lista_usuarios.html",
        {"usuarios": usuarios}
    )


@login_required
def cadastrar_usuario(request):

    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":

        form = UsuarioCadastroForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Usuário cadastrado com sucesso."
            )

            return redirect("lista_usuarios")

    else:

        form = UsuarioCadastroForm()

    return render(
        request,
        "estoque/cadastrar_usuario.html",
        {"form": form}
    )

@login_required
def editar_usuario(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied

    usuario = get_object_or_404(User, pk=pk)

    if usuario.is_superuser:

        messages.error(
            request,
            "A conta do superusuário não pode ser editada por esta página."
        )

        return redirect("lista_usuarios")

    if request.method == "POST":

        form = UsuarioEdicaoForm(
            request.POST,
            instance=usuario
        )

        if form.is_valid():

            if (
                usuario.pk == request.user.pk
                and form.cleaned_data["nivel_acesso"] == "comum"
            ):

                form.add_error(
                    "nivel_acesso",
                    "Você não pode remover sua própria permissão administrativa."
                )

            else:

                form.save()

                messages.success(
                    request,
                    "Usuário atualizado com sucesso."
                )

                return redirect("lista_usuarios")

    else:

        form = UsuarioEdicaoForm(instance=usuario)

    return render(
        request,
        "estoque/editar_usuario.html",
        {
            "form": form,
            "usuario": usuario
        }
    )

@login_required
def alterar_senha_usuario(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied

    usuario = get_object_or_404(User, pk=pk)

    if usuario.is_superuser:

        messages.error(
            request,
            "A senha do superusuário não pode ser alterada por esta página."
        )

        return redirect("lista_usuarios")

    if request.method == "POST":

        form = UsuarioSenhaForm(usuario, request.POST)

        if form.is_valid():

            form.save()

            if usuario.pk == request.user.pk:
                update_session_auth_hash(request, usuario)

            messages.success(
                request,
                "Senha alterada com sucesso."
            )

            return redirect("lista_usuarios")

    else:

        form = UsuarioSenhaForm(usuario)

    return render(
        request,
        "estoque/alterar_senha_usuario.html",
        {
            "form": form,
            "usuario": usuario
        }
    )

@login_required
def alterar_situacao_usuario(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied

    usuario = get_object_or_404(User, pk=pk)

    if usuario.is_superuser:

        messages.error(
            request,
            "A conta do superusuário é protegida."
        )

        return redirect("lista_usuarios")

    if usuario.pk == request.user.pk:

        messages.error(
            request,
            "Você não pode desativar sua própria conta."
        )

        return redirect("lista_usuarios")

    if request.method == "POST":

        usuario.is_active = not usuario.is_active

        usuario.save(update_fields=["is_active"])

        if usuario.is_active:

            messages.success(
                request,
                "Usuário ativado com sucesso."
            )

        else:

            messages.success(
                request,
                "Usuário desativado com sucesso."
            )

        return redirect("lista_usuarios")

    return render(
        request,
        "estoque/alterar_situacao_usuario.html",
        {"usuario": usuario}
    )
@login_required
def relatorios(request):
    if not request.user.is_staff:
        raise PermissionDenied

    tipo = request.GET.get("tipo", "estoque")
    data_inicio = request.GET.get("data_inicio", "")
    data_fim = request.GET.get("data_fim", "")
    situacao = request.GET.get("situacao", "todos")

    dados = None
    erro = None

    situacoes_permitidas = {
        "estoque": ["todos"],
        "estoque_critico": ["todos"],
        "movimentacoes": ["todos", "entrada", "saida"],
        "emprestimos": ["todos", "ativos", "atrasados", "devolvidos"],
        "manutencoes": ["todos", "ativas", "finalizadas"],
    }

    if tipo not in TIPOS_RELATORIO:
        tipo = "estoque"

    if situacao not in situacoes_permitidas[tipo]:
        situacao = "todos"

    if tipo in ["estoque", "estoque_critico"]:
        data_inicio = ""
        data_fim = ""

    try:
        inicio = date.fromisoformat(data_inicio) if data_inicio else None
        fim = date.fromisoformat(data_fim) if data_fim else None

        if inicio and fim and inicio > fim:
            erro = "A data inicial não pode ser maior que a data final."
        else:
            dados = gerar_dados_relatorio(
                tipo,
                inicio,
                fim,
                situacao
            )

    except ValueError:
        erro = "Informe datas válidas."

    return render(
        request,
        "estoque/relatorios.html",
        {
            "tipos_relatorio": TIPOS_RELATORIO,
            "tipo": tipo,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "situacao": situacao,
            "dados": dados,
            "erro": erro,
        }
    )