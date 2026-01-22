from django import forms
from datetime import datetime, timedelta
from .models import ImportacaoLog, ConfiguracaoFirebird


class ImportacaoForm(forms.Form):
    """Form para configurar importação"""
    
    TIPO_CHOICES = [
        ('cadastro', 'Cadastros'),
        ('nota_fiscal', 'Notas Fiscais'),
        ('conta_parcela', 'Parcelas de Contas'),
    ]
    
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Tipo de Importação'
    )
    
    data_inicial = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'value': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        }),
        label='Data Inicial',
        initial=(datetime.now() - timedelta(days=30))
    )
    
    data_final = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'value': datetime.now().strftime('%Y-%m-%d'),
        }),
        label='Data Final',
        initial=datetime.now()
    )
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicial = cleaned_data.get('data_inicial')
        data_final = cleaned_data.get('data_final')
        
        if data_inicial and data_final:
            if data_inicial > data_final:
                raise forms.ValidationError('A data inicial deve ser anterior à data final.')
        
        return cleaned_data


class FiltroImportacaoForm(forms.Form):
    """Form para filtrar logs de importação"""
    
    TIPO_CHOICES = [
        ('', 'Todos os tipos'),
        ('cadastro', 'Cadastros'),
        ('nota_fiscal', 'Notas Fiscais'),
        ('conta_parcela', 'Parcelas de Contas'),
    ]
    
    STATUS_CHOICES = [
        ('', 'Todos os status'),
        ('pendente', 'Pendente'),
        ('em_progresso', 'Em Progresso'),
        ('concluida', 'Concluída'),
        ('erro', 'Erro'),
    ]
    
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Tipo'
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Status'
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Data de Início (De)'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Data de Início (Até)'
    )


class ConfiguracaoFirebirdForm(forms.ModelForm):
    """Form para editar configurações de conexão ao Firebird"""
    
    class Meta:
        model = ConfiguracaoFirebird
        fields = ['host', 'port', 'database', 'user', 'password']
        widgets = {
            'host': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '45.178.23.26',
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '3050'
            }),
            'database': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'c:/FuturaDados/DADOS.FDB'
            }),
            'user': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SYS_CONSULTA'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'senha',
                'autocomplete': 'off'
            }),
        }
        labels = {
            'host': 'IP/Host do Servidor Firebird',
            'port': 'Porta',
            'database': 'Caminho do Banco',
            'user': 'Usuário',
            'password': 'Senha',
        }
