from django.db.models import F
from django.utils import timezone
import csv
from django.http import HttpResponse
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

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
def proteger_celula_csv(valor):
    if isinstance(valor, str):
        if valor.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + valor

    return valor


def exportar_csv(dados, tipo):
    resposta = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )

    resposta["Content-Disposition"] = (
        f'attachment; filename="relatorio_{tipo}.csv"'
    )

    resposta.write("\ufeff")

    escritor = csv.writer(resposta, delimiter=";")

    escritor.writerow(dados["cabecalhos"])

    for linha in dados["linhas"]:
        escritor.writerow([
            proteger_celula_csv(valor)
            for valor in linha
        ])

    return resposta
def numerar_pagina(canvas, documento):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)

    canvas.drawString(
        30,
        20,
        "Sistema de Controle de Estoque - Espaço Maker"
    )

    canvas.drawRightString(
        landscape(A4)[0] - 30,
        20,
        f"Página {documento.page}"
    )

    canvas.restoreState()


def exportar_pdf(dados, tipo, usuario, inicio=None, fim=None, situacao="todos"):
    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=40,
        title=dados["titulo"],
        author="Espaço Maker - IFSULDEMINAS"
    )

    estilos = getSampleStyleSheet()

    estilo_institucional = ParagraphStyle(
        "Institucional",
        parent=estilos["Normal"],
        fontSize=13,
        leading=17,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#146c43")
    )

    estilo_titulo = ParagraphStyle(
        "TituloRelatorio",
        parent=estilos["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER
    )

    estilo_celula = ParagraphStyle(
        "Celula",
        parent=estilos["Normal"],
        fontSize=9,
        leading=12,
        splitLongWords=True
    )

    estilo_cabecalho = ParagraphStyle(
        "CabecalhoTabela",
        parent=estilo_celula,
        fontName="Helvetica-Bold",
        textColor=colors.white
    )

    elementos = []

    elementos.append(
        Paragraph(
            "<b>IFSULDEMINAS - Campus Muzambinho</b>",
            estilo_institucional
        )
    )

    elementos.append(
        Paragraph(
            "Espaço Maker - Sistema de Controle de Estoque",
            estilo_institucional
        )
    )

    elementos.append(Spacer(1, 15))

    elementos.append(
        Paragraph(
            escape(dados["titulo"]),
            estilo_titulo
        )
    )

    elementos.append(Spacer(1, 10))

    data_emissao = timezone.localtime(
        timezone.now()
    ).strftime("%d/%m/%Y às %H:%M")

    responsavel = usuario.get_full_name() or usuario.username

    elementos.append(
        Paragraph(
            f"<b>Data de emissão:</b> {data_emissao}",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"<b>Emitido por:</b> {escape(responsavel)}",
            estilos["Normal"]
        )
    )

    if tipo not in ["estoque", "estoque_critico"]:

        periodo_inicio = formatar_data(inicio) if inicio else "Sem limite"
        periodo_fim = formatar_data(fim) if fim else "Sem limite"

        elementos.append(
            Paragraph(
                f"<b>Período:</b> {periodo_inicio} até {periodo_fim}",
                estilos["Normal"]
            )
        )

        nomes_situacao = {
            "todos": "Todos",
            "entrada": "Entradas",
            "saida": "Saídas",
            "ativos": "Ativos",
            "atrasados": "Atrasados",
            "devolvidos": "Devolvidos",
            "ativas": "Em andamento",
            "finalizadas": "Finalizadas"
        }

        elementos.append(
            Paragraph(
                f"<b>Situação:</b> {nomes_situacao.get(situacao, 'Todos')}",
                estilos["Normal"]
            )
        )

    elementos.append(
        Paragraph(
            f"<b>Total de registros:</b> {dados['total']}",
            estilos["Normal"]
        )
    )

    elementos.append(Spacer(1, 15))

    if dados["linhas"]:

        linhas_tabela = [
            [
                Paragraph(
                    escape(str(valor)),
                    estilo_cabecalho
                )
                for valor in dados["cabecalhos"]
            ]
        ]

        for linha in dados["linhas"]:
            linhas_tabela.append([
                Paragraph(
                    escape(str(valor)).replace("\n", "<br/>"),
                    estilo_celula
                )
                for valor in linha
            ])

        largura_coluna = documento.width / len(dados["cabecalhos"])

        tabela = Table(
            linhas_tabela,
            colWidths=[
                largura_coluna
            ] * len(dados["cabecalhos"]),
            repeatRows=1,
            splitInRow=1
        )

        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#212529")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#f2f2f2")
            ]),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6)
        ]))

        elementos.append(tabela)

    else:

        elementos.append(
            Paragraph(
                "Nenhum registro encontrado.",
                estilos["Normal"]
            )
        )

    documento.build(
        elementos,
        onFirstPage=numerar_pagina,
        onLaterPages=numerar_pagina
    )

    buffer.seek(0)

    resposta = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf"
    )

    resposta["Content-Disposition"] = (
        f'attachment; filename="relatorio_{tipo}.pdf"'
    )

    buffer.close()

    return resposta