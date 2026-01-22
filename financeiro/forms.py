from django import forms
from django.core.exceptions import ValidationError
from cadastros.models import PlanoConta, ContaFinanceira, MetodoPagamento, Fornecedor
from importacoes.models import CadastroFutura
from .models import ContaPagar, ContaReceber, MovimentacaoFinanceira


class ContaPagarForm(forms.ModelForm):
    """Formulário para criar/editar contas a pagar com Select2"""
    
    # Campo customizado para incluir todos os cadastros do Futura
    fornecedor_futura = forms.ChoiceField(
        required=True,
        label='Beneficiário',
        widget=forms.Select(attrs={
            'class': 'form-control select2-single',
            'data-placeholder': 'Selecione o beneficiário do pagamento...',
            'required': 'required'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas contas PAI (que não possuem pai)
        self.fields['conta'].queryset = PlanoConta.objects.filter(
            pai__isnull=True,
            ativo=True
        ).order_by('codigo', 'nome')
        
        # Para subconta, sempre carregar todas as subcontas disponíveis
        # A validação será feita no clean() para verificar se pertence à conta pai
        self.fields['subconta'].queryset = PlanoConta.objects.filter(
            pai__isnull=False,
            ativo=True
        ).order_by('codigo', 'nome')
        
        # Popular TODOS os cadastros do Futura (não apenas fornecedores)
        cadastros_futura = CadastroFutura.objects.all().values_list(
            'id', 'razao_social', 'fantasia', 'cnpj_cpf', 
            'chk_cliente', 'chk_fornecedor', 'chk_funcionario'
        ).order_by('razao_social', 'fantasia')
        
        choices = [('', '-- Selecione um cadastro do Futura --')]
        for cad in cadastros_futura:
            nome = cad[1] or cad[2] or f'ID {cad[0]}'
            cnpj = f' - {cad[3]}' if cad[3] else ''
            
            # Adicionar badges de tipo
            tipos = []
            if cad[4] == 'S': tipos.append('Cliente')
            if cad[5] == 'S': tipos.append('Fornecedor')
            if cad[6] == 'S': tipos.append('Funcionário')
            tipo_str = f' ({", ".join(tipos)})' if tipos else ''
            
            choices.append((cad[0], f'{nome}{cnpj}{tipo_str}'))
        
        self.fields['fornecedor_futura'].choices = choices
        
        # Tornar subconta não obrigatória
        if 'subconta' in self.fields:
            self.fields['subconta'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        fornecedor_futura = cleaned_data.get('fornecedor_futura')
        conta = cleaned_data.get('conta')
        subconta = cleaned_data.get('subconta')
        
        # Validar subconta se foi selecionada
        if subconta and conta:
            if subconta.pai != conta:
                raise ValidationError({
                    'subconta': 'A subconta selecionada não pertence à conta principal escolhida.'
                })
        
        if not fornecedor_futura:
            raise ValidationError('Selecione o beneficiário do pagamento')
        
        try:
            cadastro_futura = CadastroFutura.objects.get(id=fornecedor_futura)
            
            # Buscar ou criar fornecedor no sistema
            nome = cadastro_futura.razao_social or cadastro_futura.fantasia or f'Cadastro {cadastro_futura.id}'
            
            # Primeiro tentar buscar por CNPJ se existir
            fornecedor_obj = None
            if cadastro_futura.cnpj_cpf:
                fornecedor_obj = Fornecedor.objects.filter(cnpj_cpf=cadastro_futura.cnpj_cpf).first()
            
            # Se não encontrou por CNPJ, tentar por nome
            if not fornecedor_obj:
                fornecedor_obj = Fornecedor.objects.filter(nome__iexact=nome).first()
            
            # Se ainda não encontrou, criar novo
            if not fornecedor_obj:
                fornecedor_obj = Fornecedor.objects.create(
                    nome=nome,
                    razao_social=cadastro_futura.razao_social,
                    cnpj_cpf=cadastro_futura.cnpj_cpf,
                    email=cadastro_futura.e_mail,
                    ativo=True
                )
            else:
                # Atualizar dados do fornecedor existente
                fornecedor_obj.nome = nome
                fornecedor_obj.razao_social = cadastro_futura.razao_social
                if cadastro_futura.cnpj_cpf and not fornecedor_obj.cnpj_cpf:
                    fornecedor_obj.cnpj_cpf = cadastro_futura.cnpj_cpf
                if cadastro_futura.e_mail and not fornecedor_obj.email:
                    fornecedor_obj.email = cadastro_futura.e_mail
                fornecedor_obj.save()
            
            cleaned_data['fornecedor'] = fornecedor_obj
            
        except CadastroFutura.DoesNotExist:
            raise ValidationError('Cadastro do Futura não encontrado')
        
        return cleaned_data
    
    class Meta:
        model = ContaPagar
        fields = [
            'conta', 'subconta', 'classificacao', 'descricao',
            'valor', 'vencimento', 'conta_financeira', 'metodo_pagamento'
        ]
        widgets = {
            # Select2 para campos de relacionamento
            'conta': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione a conta principal...',
                'required': 'required'
            }),
            'subconta': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione a subconta (opcional)...'
            }),
            'conta_financeira': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione a instituição financeira (opcional)...'
            }),
            'metodo_pagamento': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione o método de pagamento (opcional)...'
            }),
            
            # Select2 para fornecedor
            'fornecedor': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione o fornecedor...',
                'required': 'required'
            }),
            
            # Campos de texto
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição da conta (opcional)',
                'rows': 3
            }),
            
            # Campos de data
            'vencimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            
            # Campos numéricos
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            
            # Select para classificação
            'classificacao': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione a classificação...',
                'required': 'required'
            })
        }


class DarBaixaForm(forms.ModelForm):
    """Formulário específico para dar baixa em contas a pagar"""
    
    class Meta:
        model = ContaPagar
        fields = [
            'data_pagamento', 'valor_pago', 'juros', 'desconto', 'pago'
        ]
        widgets = {
            'data_pagamento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'valor_pago': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'juros': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'desconto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'pago': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': 'checked'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        data_pagamento = cleaned_data.get('data_pagamento')
        valor_pago = cleaned_data.get('valor_pago')
        juros = cleaned_data.get('juros') or 0
        pago = cleaned_data.get('pago')
        
        # Validação: se pago, deve ter data_pagamento
        if pago and not data_pagamento:
            raise ValidationError(
                'Para marcar como pago, é necessário informar a data de pagamento.'
            )
        
        # Validação: valor_pago não pode ser maior que valor + juros
        if valor_pago:
            max_valor = self.instance.valor + juros
            if valor_pago > max_valor:
                raise ValidationError(
                    f'Valor pago (R$ {valor_pago:.2f}) não pode ser maior que o valor total com juros (R$ {max_valor:.2f}).'
                )
        
        # Validação: se pago, valor_pago deve ser informado
        if pago and not valor_pago:
            raise ValidationError(
                'Para marcar como pago, é necessário informar o valor pago.'
            )
        
        return cleaned_data


class ContaReceberForm(forms.ModelForm):
    """Formulário para criar/editar contas a receber com Select2"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas contas PAI (que não possuem pai)
        self.fields['conta'].queryset = PlanoConta.objects.filter(
            pai__isnull=True,
            ativo=True
        ).order_by('codigo', 'nome')
        
        # Se estiver editando e já tem uma conta selecionada, carregar as subcontas
        if self.instance.pk and self.instance.conta:
            self.fields['subconta'].queryset = PlanoConta.objects.filter(
                pai=self.instance.conta,
                ativo=True
            ).order_by('codigo', 'nome')
        else:
            # Caso contrário, deixar vazio até selecionar a conta pai
            self.fields['subconta'].queryset = PlanoConta.objects.none()
    
    class Meta:
        model = ContaReceber
        fields = [
            'conta', 'subconta', 'cliente', 'descricao',
            'vencimento', 'valor',
            'data_recebimento', 'valor_recebido', 'juros', 'desconto',
            'recebido', 'conta_financeira', 'metodo_pagamento', 'classificacao'
        ]
        widgets = {
            # Select2 para campos de relacionamento
            'conta': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione a conta principal...',
                'required': 'required'
            }),
            'subconta': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione a subconta (opcional)...'
            }),
            'conta_financeira': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione a conta financeira (opcional)...'
            }),
            'metodo_pagamento': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione o método de recebimento (opcional)...'
            }),
            
            # Campos de texto
            'cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do cliente',
                'required': 'required'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição da conta (opcional)',
                'rows': 3
            }),
            
            # Campos de data
            'vencimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'data_recebimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            
            # Campos numéricos
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'valor_recebido': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'juros': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'desconto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            
            # Checkbox
            'recebido': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            
            # Select para classificação
            'classificacao': forms.Select(attrs={
                'class': 'form-control select2-single',
                'data-placeholder': 'Selecione a classificação...',
                'required': 'required'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        vencimento = cleaned_data.get('vencimento')
        data_recebimento = cleaned_data.get('data_recebimento')
        valor = cleaned_data.get('valor')
        valor_recebido = cleaned_data.get('valor_recebido')
        juros = cleaned_data.get('juros')
        desconto = cleaned_data.get('desconto')
        recebido = cleaned_data.get('recebido')
        
        # Validação: data_recebimento não pode ser antes de vencimento
        if data_recebimento and vencimento and data_recebimento < vencimento:
            raise ValidationError(
                'A data de recebimento não pode ser anterior à data de vencimento.'
            )
        
        # Validação: se recebido, deve ter data_recebimento
        if recebido and not data_recebimento:
            raise ValidationError(
                'Para marcar como recebido, é necessário informar a data de recebimento.'
            )
        
        # Validação: valor_recebido não pode ser maior que valor + juros
        if valor_recebido:
            max_valor = (valor or 0) + (juros or 0)
            if valor_recebido > max_valor:
                raise ValidationError(
                    f'Valor recebido (R$ {valor_recebido}) não pode ser maior que o valor total com juros (R$ {max_valor}).'
                )
        
        # Validação: se recebido, valor_recebido deve ser informado
        if recebido and not valor_recebido:
            raise ValidationError(
                'Para marcar como recebido, é necessário informar o valor recebido.'
            )
        
        return cleaned_data


class FiltroContaPagarForm(forms.Form):
    """Formulário para filtrar contas a pagar"""
    
    STATUS_CHOICES = [
        ('', '--- Todos os Status ---'),
        ('pago', 'Pago'),
        ('pendente', 'Pendente'),
        ('atrasado', 'Atrasado'),
    ]
    
    status = forms.ChoiceField(
        required=False,
        initial='',
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control select2-single',
            'id': 'id_status',
            'data-placeholder': 'Todos os Status'
        })
    )
    
    classificacao = forms.ChoiceField(
        required=False,
        initial='',
        choices=[('', '--- Todas as Classificações ---')] + ContaPagar.CLASSIFICACAO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control select2-single',
            'id': 'id_classificacao',
            'data-placeholder': 'Todas as Classificações'
        })
    )
    
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.filter(ativo=True).order_by('nome'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2-single',
            'id': 'id_fornecedor',
            'data-placeholder': 'Todos os Fornecedores'
        }),
        empty_label='--- Todos os Fornecedores ---'
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'filtro_data_inicio'
        }),
        label='Vencimento a partir de'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'filtro_data_fim'
        }),
        label='Vencimento até'
    )


class FiltroContaReceberForm(forms.Form):
    """Formulário para filtrar contas a receber"""
    
    STATUS_CHOICES = [
        ('', '--- Todos os Status ---'),
        ('recebido', 'Recebido'),
        ('pendente', 'Pendente'),
        ('atrasado', 'Atrasado'),
    ]
    
    classificacao = forms.ChoiceField(
        required=False,
        initial='',
        choices=[('', '--- Todas as Classificações ---')] + ContaReceber.CLASSIFICACAO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'filtro_classificacao'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        initial='',
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'filtro_status'
        })
    )
    
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'filtro_data_inicio'
        }),
        label='Vencimento a partir de'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'filtro_data_fim'
        }),
        label='Vencimento até'
    )


class FiltroRelatorioForm(forms.Form):
    """Formulário para filtros de relatórios financeiros"""
    
    TIPO_RELATORIO_CHOICES = [
        ('', '--- Selecione o Tipo de Relatório ---'),
        ('contas_periodo', 'Contas a Pagar por Período'),
        ('pagas_pendentes', 'Contas Pagas vs Pendentes'),
        ('em_atraso', 'Contas em Atraso'),
        ('a_vencer', 'Contas a Vencer'),
        ('por_fornecedor', 'Contas por Fornecedor'),
        ('por_plano_contas', 'Contas por Plano de Contas'),
        ('por_metodo_pagamento', 'Contas por Método de Pagamento'),
        ('por_instituicao', 'Contas por Instituição Financeira'),
        ('fluxo_caixa', 'Fluxo de Caixa'),
    ]
    
    TIPO_DATA_CHOICES = [
        ('vencimento', 'Data de Vencimento'),
        ('pagamento', 'Data de Pagamento'),
        ('criacao', 'Data de Criação'),
    ]
    
    STATUS_CHOICES = [
        ('', 'Todos'),
        ('pago', 'Pago'),
        ('pendente', 'Pendente'),
        ('atrasado', 'Atrasado'),
    ]
    
    tipo_relatorio = forms.ChoiceField(
        required=True,
        choices=TIPO_RELATORIO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_tipo_relatorio'
        }),
        label='Tipo de Relatório'
    )
    
    tipo_data = forms.ChoiceField(
        required=False,
        choices=TIPO_DATA_CHOICES,
        initial='vencimento',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_tipo_data'
        }),
        label='Considerar'
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_data_inicio'
        }),
        label='Data Inicial'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_data_fim'
        }),
        label='Data Final'
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_status'
        }),
        label='Status'
    )
    
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.filter(ativo=True).order_by('nome'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2-single',
            'id': 'id_fornecedor',
            'data-placeholder': 'Todos os Fornecedores'
        }),
        empty_label='Todos os Fornecedores',
        label='Fornecedor'
    )
    
    conta_financeira = forms.ModelChoiceField(
        queryset=ContaFinanceira.objects.filter(ativo=True).order_by('nome'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2-single',
            'id': 'id_conta_financeira',
            'data-placeholder': 'Todas as Instituições'
        }),
        empty_label='Todas as Instituições',
        label='Instituição Financeira'
    )
    
    plano_conta = forms.ModelChoiceField(
        queryset=PlanoConta.objects.filter(ativo=True, pai__isnull=True).order_by('codigo'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2-single',
            'id': 'id_plano_conta',
            'data-placeholder': 'Todas as Contas'
        }),
        empty_label='Todas as Contas',
        label='Plano de Contas'
    )
    
    metodo_pagamento = forms.ModelChoiceField(
        queryset=MetodoPagamento.objects.filter(ativo=True).order_by('nome'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2-single',
            'id': 'id_metodo_pagamento',
            'data-placeholder': 'Todos os Métodos'
        }),
        empty_label='Todos os Métodos',
        label='Método de Pagamento'
    )
    
    classificacao = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas')] + ContaPagar.CLASSIFICACAO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_classificacao'
        }),
        label='Classificação'
    )
    
    dias_vencer = forms.IntegerField(
        required=False,
        initial=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'id_dias_vencer',
            'min': '1',
            'placeholder': '30'
        }),
        label='Dias a Vencer'
    )

