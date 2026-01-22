from django import forms
from .models import Cliente, NotaFiscal, OrigemCobranca, Parcela, CreditoCobranca
from cadastros.models import ContaFinanceira


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'cidade', 'estado', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class NotaFiscalForm(forms.ModelForm):
    class Meta:
        model = NotaFiscal
        fields = [
            'numero_nota', 'serie', 'cliente', 'data_emissao', 'data_vencimento',
            'valor_produtos', 'valor_ipi', 'valor_desconto', 'valor_acrescimo',
            'valor_total', 'observacoes', 'ativo'
        ]
        widgets = {
            'numero_nota': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'data_emissao': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_produtos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_ipi': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_acrescimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OrigemCobrancaForm(forms.ModelForm):
    class Meta:
        model = OrigemCobranca
        fields = ['nome', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ParcelaForm(forms.ModelForm):
    class Meta:
        model = Parcela
        fields = [
            'nota_fiscal', 'cliente', 'origem', 'tipo_parcela', 'numero_parcela',
            'valor', 'valor_pago', 'desconto_concedido', 'juros', 'multa', 'acrescimos',
            'data_vencimento', 'data_pagamento', 'status_pagamento',
            'motivo_desconto', 'observacao'
        ]
        widgets = {
            'nota_fiscal': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'origem': forms.Select(attrs={'class': 'form-select'}),
            'tipo_parcela': forms.Select(attrs={'class': 'form-select'}),
            'numero_parcela': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_pago': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desconto_concedido': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'juros': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'multa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'acrescimos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_pagamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'motivo_desconto': forms.TextInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RegistrarParcelasForm(forms.Form):
    """Form para vincular instituições financeiras às parcelas e gerar carteira"""
    numero_nota = forms.CharField(
        max_length=20,
        label='Número da NF',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    conta_financeira_parcelas = forms.ModelChoiceField(
        queryset=ContaFinanceira.objects.filter(ativo=True),
        label='Instituição Financeira para Parcelas',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tem_carteira = forms.BooleanField(
        required=False,
        initial=False,
        label='Há Carteira?',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    conta_financeira_carteira = forms.ModelChoiceField(
        queryset=ContaFinanceira.objects.filter(ativo=True),
        label='Instituição Financeira para Carteira',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class CreditoCobrancaForm(forms.ModelForm):
    class Meta:
        model = CreditoCobranca
        fields = ['nota_fiscal', 'cliente', 'valor_credito', 'justificativa']
        widgets = {
            'nota_fiscal': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'valor_credito': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'justificativa': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class BaixaParcelaForm(forms.Form):
    """Form para dar baixa em uma ou mais parcelas"""
    data_pagamento = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    valor_pago = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    desconto = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    juros = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    multa = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    motivo_desconto = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    observacao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
