from django.db.models import F
from django.utils import timezone

from .models import Material, Movimentacao, Emprestimo, Manutencao


TIPOS_RELATORIO = {
    "estoque": "Estoque atual",
    "estoque_critico": "Estoque crítico",
    "movimentacoes": "Movimentações de estoque",
    "emprestimos": "Empréstimos e devoluções",
    "manutencoes": "Manutenções",
}


def formatar_data(data):
    if data is None:
        return "-"

    return data.strftime("%d/%m/%Y")


def formatar_data_hora(data):
    if data is None:
        return "-"

    return timezone.localtime(data).strftime("%d/%m/%Y %H:%M")


def filtrar_periodo(registros, campo, data_inicio, data_fim):
    if data_inicio:
        registros = registros.filter(
            **{f"{campo}__date__gte": data_inicio}
        )

    if data_fim:
        registros = registros.filter(
            **{f"{campo}__date__lte": data_fim}
        )

    return registros


def gerar_dados_relatorio(tipo, data_inicio=None, data_fim=None, situacao="todos"):

    if tipo in ["estoque", "estoque_critico"]:

        materiais = Material.objects.select_related(
            "categoria"
        ).order_by("nome")

        if tipo == "estoque_critico":
            materiais = materiais.filter(
                quantidade__lte=F("estoque_minimo")
            )

        cabecalhos = [
            "Material",
            "Categoria",
            "Quantidade",
            "Unidade",
            "Estoque mínimo",
            "Situação",
        ]

        linhas = [
            [
                material.nome,
                material.categoria.nome,
                material.quantidade,
                material.unidade_medida,
                material.estoque_minimo,
                {
                    "normal": "Normal",
                    "baixo": "Estoque baixo",
                    "esgotado": "Esgotado",
                }.get(material.situacao_estoque, "-"),
            ]
            for material in materiais
        ]

    elif tipo == "movimentacoes":

        movimentacoes = Movimentacao.objects.select_related(
            "material", "responsavel"
        ).order_by("-data")

        movimentacoes = filtrar_periodo(
            movimentacoes, "data", data_inicio, data_fim
        )

        if situacao in ["entrada", "saida"]:
            movimentacoes = movimentacoes.filter(tipo=situacao)

        cabecalhos = [
            "Material",
            "Tipo",
            "Quantidade",
            "Data",
            "Responsável",
            "Observação",
        ]

        linhas = [
            [
                movimentacao.material.nome,
                movimentacao.get_tipo_display(),
                movimentacao.quantidade,
                formatar_data_hora(movimentacao.data),
                movimentacao.responsavel.username,
                movimentacao.observacao or "-",
            ]
            for movimentacao in movimentacoes
        ]

    elif tipo == "emprestimos":

        emprestimos = Emprestimo.objects.select_related(
            "equipamento", "responsavel"
        ).order_by("-data_emprestimo")

        emprestimos = filtrar_periodo(
            emprestimos, "data_emprestimo", data_inicio, data_fim
        )

        if situacao == "ativos":
            emprestimos = emprestimos.filter(
                data_devolucao__isnull=True
            )

        elif situacao == "atrasados":
            emprestimos = emprestimos.filter(
                data_devolucao__isnull=True,
                previsao_devolucao__lt=timezone.localdate(),
            )

        elif situacao == "devolvidos":
            emprestimos = emprestimos.filter(
                data_devolucao__isnull=False
            )

        cabecalhos = [
            "Equipamento",
            "Solicitante",
            "Empréstimo",
            "Previsão de devolução",
            "Devolução",
            "Responsável",
            "Situação",
        ]

        linhas = [
            [
                emprestimo.equipamento.nome,
                emprestimo.solicitante,
                formatar_data_hora(emprestimo.data_emprestimo),
                formatar_data(emprestimo.previsao_devolucao),
                formatar_data_hora(emprestimo.data_devolucao),
                emprestimo.responsavel.username,
                {
                    "emprestado": "Emprestado",
                    "atrasado": "Atrasado",
                    "devolvido": "Devolvido",
                }.get(emprestimo.situacao, "-"),
            ]
            for emprestimo in emprestimos
        ]

    elif tipo == "manutencoes":

        manutencoes = Manutencao.objects.select_related(
            "equipamento", "responsavel"
        ).order_by("-data_inicio")

        manutencoes = filtrar_periodo(
            manutencoes, "data_inicio", data_inicio, data_fim
        )

        if situacao == "ativas":
            manutencoes = manutencoes.filter(
                data_fim__isnull=True
            )

        elif situacao == "finalizadas":
            manutencoes = manutencoes.filter(
                data_fim__isnull=False
            )

        cabecalhos = [
            "Equipamento",
            "Motivo",
            "Data de início",
            "Data de finalização",
            "Responsável",
            "Situação",
        ]

        linhas = [
            [
                manutencao.equipamento.nome,
                manutencao.motivo,
                formatar_data_hora(manutencao.data_inicio),
                formatar_data_hora(manutencao.data_fim),
                manutencao.responsavel.username,
                "Finalizada" if manutencao.finalizada else "Em andamento",
            ]
            for manutencao in manutencoes
        ]

    else:
        raise ValueError("Tipo de relatório inválido.")

    return {
        "titulo": TIPOS_RELATORIO[tipo],
        "cabecalhos": cabecalhos,
        "linhas": linhas,
        "total": len(linhas),
    }