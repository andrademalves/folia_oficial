from django import forms
from .models import ConfiguracaoBancaria


class ConfiguracaoBancariaForm(forms.ModelForm):
    """Formulário para configuração bancária"""
    
    class Meta:
        model = ConfiguracaoBancaria
        fields = [
            'nome', 'ativo', 'conta_financeira',
            'codigo_banco', 'codigo_beneficiario',
            'agencia', 'agencia_dv', 'conta', 'conta_dv',
            'carteira', 'modalidade', 'convenio',
            'nosso_numero_inicio', 'nosso_numero_atual', 'nosso_numero_fim',
            'razao_social', 'cnpj', 'endereco', 'cidade', 'uf', 'cep',
            'percentual_juros_mes', 'percentual_multa', 'dias_para_multa',
            'dias_para_protesto', 'dias_para_baixa',
            'instrucao1', 'instrucao2', 'instrucao3', 'local_pagamento'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Caixa - Convênio Principal'}),
            'conta_financeira': forms.Select(attrs={'class': 'form-select'}),
            'codigo_banco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '104'}),
            'codigo_beneficiario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código fornecido pelo banco'}),
            'agencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1234'}),
            'agencia_dv': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 5', 'maxlength': '1'}),
            'conta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 123456'}),
            'conta_dv': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 7', 'maxlength': '1'}),
            'carteira': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1'}),
            'modalidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '14'}),
            'convenio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número do convênio'}),
            'nosso_numero_inicio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1'}),
            'nosso_numero_atual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1'}),
            'nosso_numero_fim': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '99999999999999999'}),
            'razao_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razão Social da Empresa'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Endereço completo'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'uf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SP', 'maxlength': '2'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'percentual_juros_mes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'percentual_multa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'dias_para_multa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1'}),
            'dias_para_protesto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'dias_para_baixa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'instrucao1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Não receber após o vencimento'}),
            'instrucao2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instrução 2 (opcional)'}),
            'instrucao3': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instrução 3 (opcional)'}),
            'local_pagamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PREFERENCIALMENTE NAS CASAS LOTÉRICAS ATÉ O VALOR LIMITE'}),
        }
    
    def clean_codigo_beneficiario(self):
        valor = self.cleaned_data.get('codigo_beneficiario')
        if valor and not str(valor).isdigit():
            raise forms.ValidationError('Código do Beneficiário deve conter apenas números.')
        return valor
    
    def clean_codigo_banco(self):
        valor = self.cleaned_data.get('codigo_banco')
        if valor and not str(valor).isdigit():
            raise forms.ValidationError('Código do Banco deve conter apenas números.')
        return valor
    
    def clean_agencia(self):
        valor = self.cleaned_data.get('agencia')
        if valor and not str(valor).isdigit():
            raise forms.ValidationError('Agência deve conter apenas números.')
        return valor
    
    def clean_conta(self):
        valor = self.cleaned_data.get('conta')
        if valor and not str(valor).isdigit():
            raise forms.ValidationError('Conta deve conter apenas números.')
        return valor
    
    def clean_carteira(self):
        valor = self.cleaned_data.get('carteira')
        if valor and not str(valor).isdigit():
            raise forms.ValidationError('Carteira deve conter apenas números.')
        return valor
    
    def clean_modalidade(self):
        valor = self.cleaned_data.get('modalidade')
        if valor and not str(valor).isdigit():
            raise forms.ValidationError('Modalidade deve conter apenas números.')
        return valor

