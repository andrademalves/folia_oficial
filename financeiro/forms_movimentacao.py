from django import forms
from django.core.exceptions import ValidationError
from cadastros.models import PlanoConta, ContaFinanceira
from .models import MovimentacaoFinanceira


class MovimentacaoFinanceiraForm(forms.ModelForm):
    """Formulário para lançamento manual de movimentações"""
    
    class Meta:
        model = MovimentacaoFinanceira
        fields = [
            'conta_financeira', 'data', 'tipo', 'valor', 'descricao',
            'categoria', 'conta_destino', 'observacoes'
        ]
        widgets = {
            'conta_financeira': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione a conta...',
                'required': 'required'
            }),
            'data': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': 'required'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição da movimentação...',
                'rows': 3,
                'required': 'required'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione uma categoria (opcional)...'
            }),
            'conta_destino': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Para transferências, selecione a conta destino...'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observações adicionais (opcional)...',
                'rows': 2
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas contas ativas
        self.fields['conta_financeira'].queryset = ContaFinanceira.objects.filter(ativo=True)
        self.fields['conta_destino'].queryset = ContaFinanceira.objects.filter(ativo=True)
        self.fields['categoria'].queryset = PlanoConta.objects.filter(ativo=True).order_by('codigo', 'nome')
        
        # Se for edição, desabilitar alguns campos
        if self.instance.pk and self.instance.origem != 'MANUAL':
            self.fields['conta_financeira'].disabled = True
            self.fields['tipo'].disabled = True
            self.fields['valor'].disabled = True
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        conta_destino = cleaned_data.get('conta_destino')
        conta_financeira = cleaned_data.get('conta_financeira')
        
        # Se for transferência, validar conta destino
        if conta_destino:
            if not tipo:
                raise ValidationError('Para transferências, selecione o tipo de movimentação.')
            if conta_destino == conta_financeira:
                raise ValidationError('A conta de destino não pode ser a mesma que a conta de origem.')
        
        return cleaned_data


class FiltroMovimentacaoForm(forms.Form):
    """Formulário para filtrar movimentações financeiras"""
    
    conta_financeira = forms.ModelChoiceField(
        queryset=ContaFinanceira.objects.filter(ativo=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2-single',
            'data-placeholder': 'Todas as contas...',
            'id': 'filtro_conta'
        }),
        label='Conta Financeira'
    )
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos')] + list(MovimentacaoFinanceira.TIPO_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'filtro_tipo'
        }),
        label='Tipo'
    )
    
    origem = forms.ChoiceField(
        choices=[('', 'Todas')] + list(MovimentacaoFinanceira.ORIGEM_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'filtro_origem'
        }),
        label='Origem'
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'filtro_data_inicio'
        }),
        label='Data início'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'filtro_data_fim'
        }),
        label='Data fim'
    )
