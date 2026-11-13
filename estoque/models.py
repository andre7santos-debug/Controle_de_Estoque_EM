from django.db import models


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

