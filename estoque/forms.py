from django import forms
from .models import Material, Categoria, Equipamento, Movimentacao

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material

        fields = [
            "nome",
            "descricao",
            "categoria",
            "quantidade",
            "estoque_minimo",
            "unidade_medida",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "descricao": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "categoria": forms.Select(
                attrs={"class": "form-select"}
            ),
            "quantidade": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "estoque_minimo": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "unidade_medida": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "descricao"]

        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "descricao": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }
class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento

        fields = [
            "nome",
            "descricao",
            "categoria",
            "numero_patrimonio",
            "status",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "descricao": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "categoria": forms.Select(
                attrs={"class": "form-select"}
            ),
            "numero_patrimonio": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "status": forms.Select(
                attrs={"class": "form-select"}
            ),
        }
class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao

        fields = [
            "material",
            "tipo",
            "quantidade",
            "observacao",
        ]

        widgets = {
            "material": forms.Select(
                attrs={"class": "form-select"}
            ),
            "tipo": forms.Select(
                attrs={"class": "form-select"}
            ),
            "quantidade": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "observacao": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }

    def clean_quantidade(self):
        quantidade = self.cleaned_data["quantidade"]

        if quantidade <= 0:
            raise forms.ValidationError(
                "A quantidade deve ser maior que zero."
            )

        return quantidade

