from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Material(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="materiais"
    )

    quantidade = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)
    unidade_medida = models.CharField(max_length=30, default="unidade")

    @property
    def situacao_estoque(self):
        if self.quantidade == 0:
            return "esgotado"

        if self.quantidade <= self.estoque_minimo:
            return "baixo"

        return "normal"

    def __str__(self):
        return self.nome

@property
def situacao_estoque(self):
        if self.quantidade == 0:
            return "esgotado"

        if self.quantidade <= self.estoque_minimo:
            return "baixo"

        return "normal"

def __str__(self):
        return self.nome


class Equipamento(models.Model):
    STATUS_CHOICES = [
        ("disponivel", "Disponível"),
        ("emprestado", "Emprestado"),
        ("manutencao", "Em manutenção"),
    ]

    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="equipamentos"
    )
    numero_patrimonio = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="disponivel"
    )

    def __str__(self):
        return self.nome
    

class Movimentacao(models.Model):

    TIPO_CHOICES = [
        ("entrada", "Entrada"),
        ("saida", "Saída"),
    ]

    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="movimentacoes"
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES
    )

    quantidade = models.PositiveIntegerField()

    data = models.DateTimeField(auto_now_add=True)

    responsavel = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT
    )

    observacao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.material.nome}"
    

class Emprestimo(models.Model):

    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.PROTECT,
        related_name="emprestimos"
    )

    solicitante = models.CharField(max_length=150)

    data_emprestimo = models.DateTimeField(
        default=timezone.now
    )

    previsao_devolucao = models.DateField()

    data_devolucao = models.DateTimeField(
        null=True,
        blank=True
    )

    responsavel = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT
    )

    observacao = models.TextField(blank=True)

    @property
    def devolvido(self):
        return self.data_devolucao is not None

    def __str__(self):
        return f"{self.equipamento.nome} - {self.solicitante}"


