from django import forms
from django.db.models import Max
from .models import PlanoConta, ContaFinanceira, MetodoPagamento

class PlanoContaForm(forms.ModelForm):
    # Permite deixar 'id' vazio; se vazio, define próximo id disponível
    id = forms.IntegerField(required=False, min_value=1, label='ID')

    class Meta:
        model = PlanoConta
        fields = ['id', 'codigo', 'nome', 'ativo', 'pai']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pai': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajusta queryset para excluir a própria conta da lista de pais (evita loop)
        if self.instance.pk:
            self.fields['pai'].queryset = PlanoConta.objects.exclude(pk=self.instance.pk)
        # Placeholder para combo de pai
        self.fields['pai'].empty_label = "Nenhuma (Conta Raiz)"

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Se id não informado, gera próximo id
        if instance.pk is None:
            next_id = (PlanoConta.objects.aggregate(m=Max('id'))['m'] or 0) + 1
            instance.id = next_id
        if commit:
            instance.save()
        return instance

class ContaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = ContaFinanceira
        fields = ['nome', 'tipo', 'agencia', 'agencia_dv', 'conta', 'conta_dv', 'saldo_inicial', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'agencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1234'}),
            'agencia_dv': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 5', 'maxlength': '1', 'style': 'max-width: 60px; text-align: center;'}),
            'conta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 123456'}),
            'conta_dv': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 7', 'maxlength': '1', 'style': 'max-width: 60px; text-align: center;'}),
            'saldo_inicial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MetodoPagamentoForm(forms.ModelForm):
    class Meta:
        model = MetodoPagamento
        fields = ['nome', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MetodoPagamentoForm(forms.ModelForm):
    class Meta:
        model = MetodoPagamento
        fields = ['nome', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
