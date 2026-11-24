from django import forms
from django.utils import timezone
from .models import Material, Categoria, Equipamento, Movimentacao, Emprestimo, Manutencao
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm

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
class MaterialEdicaoForm(MaterialForm):
    class Meta(MaterialForm.Meta):
        fields = [
            "nome",
            "descricao",
            "categoria",
            "estoque_minimo",
            "unidade_medida",
        ]

class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo

        fields = [
            "equipamento",
            "solicitante",
            "data_emprestimo",
            "previsao_devolucao",
            "observacao",
        ]

        widgets = {
            "equipamento": forms.Select(
                attrs={"class": "form-select"}
            ),
            "solicitante": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "data_emprestimo": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),
            "previsao_devolucao": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "observacao": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        emprestimos_ativos = Emprestimo.objects.filter(
            data_devolucao__isnull=True
        ).values_list("equipamento_id", flat=True)

        self.fields["equipamento"].queryset = (
            Equipamento.objects.filter(
                status="disponivel"
            ).exclude(
                pk__in=emprestimos_ativos
            ).order_by("nome")
        )

    def clean_data_emprestimo(self):
        data = self.cleaned_data["data_emprestimo"]

        if data > timezone.now():
            raise forms.ValidationError(
                "A data do empréstimo não pode estar no futuro."
            )

        return data

    def clean(self):
        cleaned_data = super().clean()

        data_emprestimo = cleaned_data.get("data_emprestimo")
        previsao = cleaned_data.get("previsao_devolucao")

        if data_emprestimo and previsao:
            if previsao < timezone.localtime(data_emprestimo).date():
                self.add_error(
                    "previsao_devolucao",
                    "A previsão de devolução não pode ser anterior à data do empréstimo."
                )

        return cleaned_data
    

class ManutencaoForm(forms.ModelForm):

    class Meta:
        model = Manutencao

        fields = [
            "equipamento",
            "motivo",
            "data_inicio",
            "observacao",
        ]

        widgets = {
            "equipamento": forms.Select(
                attrs={"class": "form-select"}
            ),
            "motivo": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "data_inicio": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),
            "observacao": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }

        labels = {
            "equipamento": "Equipamento",
            "motivo": "Motivo da manutenção",
            "data_inicio": "Data de início",
            "observacao": "Observações",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        manutencoes_ativas = Manutencao.objects.filter(
            data_fim__isnull=True
        ).values_list("equipamento_id", flat=True)

        emprestimos_ativos = Emprestimo.objects.filter(
            data_devolucao__isnull=True
        ).values_list("equipamento_id", flat=True)

        self.fields["equipamento"].queryset = (
            Equipamento.objects.filter(
                status="disponivel"
            ).exclude(
                pk__in=manutencoes_ativas
            ).exclude(
                pk__in=emprestimos_ativos
            ).order_by("nome")
        )

    def clean_data_inicio(self):
        data_inicio = self.cleaned_data["data_inicio"]

        if data_inicio > timezone.now():
            raise forms.ValidationError(
                "A data de início não pode estar no futuro."
            )

        return data_inicio

class UsuarioCadastroForm(UserCreationForm):

    NIVEL_CHOICES = [
        ("comum", "Usuário comum"),
        ("administrador", "Administrador"),
    ]

    nivel_acesso = forms.ChoiceField(
        choices=NIVEL_CHOICES,
        label="Nível de acesso",
        widget=forms.Select(
            attrs={"class": "form-select"}
        )
    )

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "nivel_acesso",
        ]

        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "username": "Nome de usuário",
            "email": "E-mail",
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True

        self.fields["password1"].label = "Senha"
        self.fields["password2"].label = "Confirmar senha"

        for campo in self.fields.values():

            if isinstance(campo.widget, forms.Select):
                campo.widget.attrs["class"] = "form-select"
            else:
                campo.widget.attrs["class"] = "form-control"

    def clean_email(self):

        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Este e-mail já está cadastrado."
            )

        return email

    def save(self, commit=True):

        usuario = super().save(commit=False)

        usuario.is_staff = (
            self.cleaned_data["nivel_acesso"] == "administrador"
        )

        usuario.is_superuser = False
        usuario.is_active = True

        if commit:
            usuario.save()

        return usuario

class UsuarioEdicaoForm(forms.ModelForm):

    NIVEL_CHOICES = [
        ("comum", "Usuário comum"),
        ("administrador", "Administrador"),
    ]

    nivel_acesso = forms.ChoiceField(
        choices=NIVEL_CHOICES,
        label="Nível de acesso",
        widget=forms.Select(
            attrs={"class": "form-select"}
        )
    )

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "nivel_acesso",
        ]

        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "username": "Nome de usuário",
            "email": "E-mail",
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True

        self.fields["nivel_acesso"].initial = (
            "administrador"
            if self.instance.is_staff
            else "comum"
        )

        for campo in self.fields.values():

            if isinstance(campo.widget, forms.Select):
                campo.widget.attrs["class"] = "form-select"
            else:
                campo.widget.attrs["class"] = "form-control"

    def clean_email(self):

        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.pk).exists():

            raise forms.ValidationError(
                "Este e-mail já está cadastrado."
            )

        return email

    def save(self, commit=True):

        usuario = super().save(commit=False)

        usuario.is_staff = (
            self.cleaned_data["nivel_acesso"] == "administrador"
        )

        if commit:
            usuario.save()

        return usuario

class UsuarioSenhaForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["new_password1"].label = "Nova senha"
        self.fields["new_password2"].label = "Confirmar nova senha"

        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-control"