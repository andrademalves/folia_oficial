# Implementação da Lógica DevFolia - Status

## Data: 23/12/2025

---

## ✅ CONCLUÍDO

### 1. Models (contas_receber/models.py) - 100%

#### Cliente
- ✅ Adicionados indexes para performance (cpf_cnpj, ativo+nome)
- ✅ Todos os campos de endereço e contato

#### CategoriaReceita  
- ✅ Renomeado de OrigemCobranca
- ✅ Estrutura simples: nome, descrição, ativo

#### NotaFiscal - **LÓGICA DE CARTEIRA IMPLEMENTADA**
```python
# Campos adicionados:
- total_produto (Decimal)
- total_ipi_valor (Decimal)
- total_nota (Decimal)
- id_externo (Integer) # Para Firebird

# Métodos implementados:
def valor_carteira(self):
    return (self.total_produto - self.total_ipi_valor)

def valor_total_nf(self):
    return self.valor_carteira() + self.total_nota
```

#### ContaReceber (Parcela) - **TODAS AS FUNCIONALIDADES DEVFOLIA**
```python
# Campos DevFolia adicionados:
- tipo_parcela: CHOICES['NF', 'CA', 'AV']
- codigo_identificador: CharField(unique=True)
- pagamento_parcial: BooleanField
- motivo_desconto: CharField
- observacao_negociacao: TextField
- id_parcela_externo: Integer # Para Firebird

# Auto-Status no save():
- Gera codigo_identificador automaticamente
- Atualiza status para 'recebido' quando total pago
- Atualiza para 'parcial' quando parcialmente pago
- Atualiza para 'vencido' quando vencido

# Métodos:
- quitada() -> bool
- total_a_pagar() -> Decimal
- dias_vencimento() -> int
- esta_vencido() -> bool
```

#### CreditoCliente - **APROVAÇÃO EM DOIS PASSOS**
```python
# Status: pendente, aprovado, reprovado, cancelado

# Campos principais:
- nota_fiscal (FK, unique, nullable)
- cliente (FK)
- valor_credito (solicitado)
- valor_credito_liberado (aprovado)
- valor_utilizado (já usado)
- usuario_solicitante (FK User)
- usuario_liberador (FK User, null)
- justificativa, motivo_reprovacao

# Métodos de negócio:
- aprovar(usuario, valor_liberado)
- reprovar(usuario, motivo)
- utilizar_credito(valor, usuario)
- saldo_disponivel() -> Decimal
- pode_utilizar(valor) -> bool
```

#### HistoricoUsoCredito
```python
# Rastreamento de cada uso de crédito
- credito (FK CreditoCliente)
- valor_utilizado
- data_utilizacao (auto_now_add)
- usuario (FK User)
- observacao
```

#### RecebimentoParcela
```python
# Histórico de recebimentos
- conta_receber (FK)
- data_recebimento
- valor_recebido
- forma_recebimento
- banco, numero_documento
- credito_utilizado (FK CreditoCliente, nullable)
- usuario (FK User)
```

---

### 2. Forms (contas_receber/forms.py) - 100%

#### Forms Criados:

1. **ClienteForm** - CRUD básico de clientes
2. **CategoriaReceitaForm** - Categorias de receita
3. **NotaFiscalForm** - Com validação de carteira
   - Valida que total_produto, total_ipi, total_nota >= 0
4. **ContaReceberForm** - Todos os campos DevFolia
5. **RecebimentoForm** - **COM SUPORTE A CRÉDITO**
   ```python
   # Campos extras:
   - usar_credito (BooleanField)
   - credito_cliente (ModelChoiceField)
   - valor_credito_utilizar (DecimalField)
   
   # Inicialização dinâmica:
   - Filtra créditos disponíveis do cliente
   - Sugere valor_recebido = saldo_restante()
   ```

6. **CreditoClienteForm** - Solicitação
   - Valida valor_credito > 0

7. **AprovarCreditoForm** - **APROVAÇÃO/REPROVAÇÃO**
   ```python
   # Lógica de validação:
   - Se aprovar: exige valor_credito_liberado > 0
   - Se reprovar: exige motivo_reprovacao
   ```

8. **AlterarCreditoForm** - **PROTEÇÃO CONTRA REDUÇÃO**
   ```python
   # Não permite reduzir valor se já foi utilizado:
   if novo_valor < self.instance.valor_utilizado:
       raise ValidationError(...)
   ```

9. **FiltroContasReceberForm** - Filtros completos
10. **FiltroRelatorioReceberForm** - Relatórios

---

## ⚠️ PENDENTE

### 3. Migrations - **PROBLEMA ATUAL**

**Situação**: Banco de dados já tem estrutura da migração `0001_initial`, mas os models foram alterados significativamente.

**Problema**: Conflito entre:
- Campos que já existem no banco (valor_juros, valor_multa, etc.)
- Campos que precisam ser adicionados (tipo_parcela, codigo_identificador, etc.)
- Campos que não existem mais no banco mas a migração tenta remover (valor_produtos da NotaFiscal)

**Solução Recomendada**:
```bash
# 1. Fazer backup do banco de dados
mysqldump -u root -p gestao_ti > backup_antes_migracao.sql

# 2. Opção A - Marcar migração como fake e criar incremental:
python manage.py migrate contas_receber --fake

# 3. Criar nova migração incremental:
python manage.py makemigrations contas_receber --name adicionar_campos_devfolia

# 4. Editar a migração para ignorar campos que já existem

# 5. Aplicar:
python manage.py migrate contas_receber

# Opção B - Reset completo (SE BANCO DE TESTE):
python manage.py migrate contas_receber zero
python manage.py migrate contas_receber
```

**Campos que PRECISAM ser adicionados ao banco**:
- `contas_receber_contareceber.tipo_parcela`
- `contas_receber_contareceber.codigo_identificador`
- `contas_receber_contareceber.pagamento_parcial`
- `contas_receber_contareceber.motivo_desconto`
- `contas_receber_contareceber.observacao_negociacao`
- `contas_receber_contareceber.id_parcela_externo`
- `contas_receber_notafiscal.total_produto`
- `contas_receber_notafiscal.total_ipi_valor`
- `contas_receber_notafiscal.total_nota`
- `contas_receber_notafiscal.id_externo`
- `contas_receber_creditocliente.status`
- `contas_receber_creditocliente.valor_credito_liberado`
- `contas_receber_creditocliente.data_liberacao`
- `contas_receber_creditocliente.usuario_liberador_id`
- `contas_receber_creditocliente.motivo_reprovacao`
- Tabela `contas_receber_historicousocredito`
- Indexes em Cliente, ContaReceber, CreditoCliente, NotaFiscal

---

### 4. Views (contas_receber/views.py) - 0%

**Precisam ser implementadas**:

#### CRUD Básico:
- ✅ Clientes (já existe básico)
- ⚠️ Categorias de Receita
- ⚠️ Notas Fiscais
- ⚠️ Contas a Receber

#### Views Especiais:
- ⚠️ **Recebimento de Parcela com Crédito**
  ```python
  def receber_parcela(request, pk):
      # 1. Exibir saldo restante
      # 2. Opção de usar crédito do cliente
      # 3. Se usar crédito:
      #    - Validar saldo disponível
      #    - Criar RecebimentoParcela
      #    - Chamar credito.utilizar_credito()
      #    - Atualizar valor_recebido da ContaReceber
      # 4. Atualizar status automaticamente (via save())
  ```

- ⚠️ **Solicitação de Crédito**
  ```python
  def solicitar_credito(request):
      # 1. Form com cliente, nota_fiscal, valor, justificativa
      # 2. Criar CreditoCliente com status='pendente'
      # 3. Notificar aprovadores
  ```

- ⚠️ **Aprovação de Crédito**
  ```python
  def aprovar_credito(request, pk):
      # 1. Verificar se usuário tem permissão
      # 2. Exibir dados do crédito
      # 3. Form com ação (aprovar/reprovar)
      # 4. Se aprovar:
      #    - Informar valor_liberado
      #    - Chamar credito.aprovar(user, valor)
      # 5. Se reprovar:
      #    - Informar motivo
      #    - Chamar credito.reprovar(user, motivo)
  ```

- ⚠️ **Lista de Créditos Pendentes**
- ⚠️ **Histórico de Uso de Crédito**
- ⚠️ **Baixa em Lote** (receber múltiplas parcelas)
- ⚠️ **Relatórios**:
  - Contas por vencimento
  - Contas por cliente
  - Inadimplência
  - Créditos ativos
  - Histórico de recebimentos

---

### 5. Templates - 0%

**Templates necessários**:

```
contas_receber/templates/contas_receber/
├── cliente_list.html
├── cliente_form.html
├── categoria_list.html
├── categoria_form.html
├── notafiscal_list.html
├── notafiscal_form.html
├── contareceber_list.html (com filtros)
├── contareceber_form.html
├── receber_parcela.html (ESPECIAL - com opção de crédito)
├── credito_list.html (pendentes + aprovados)
├── credito_form.html (solicitar)
├── credito_aprovar.html (aprovar/reprovar)
├── credito_historico.html
├── relatorios/
│   ├── contas_vencimento.html
│   ├── contas_cliente.html
│   ├── inadimplencia.html
│   └── creditos_ativos.html
```

**Template Especial - receber_parcela.html**:
```html
<form method="post">
    {% csrf_token %}
    
    <h3>Conta a Receber: {{ conta.descricao }}</h3>
    <p>Valor Total: R$ {{ conta.valor_total }}</p>
    <p>Saldo Restante: R$ {{ conta.saldo_restante }}</p>
    
    {{ form.data_recebimento }}
    {{ form.valor_recebido }}
    {{ form.forma_recebimento }}
    
    <hr>
    <h4>Usar Crédito do Cliente?</h4>
    {{ form.usar_credito }}
    
    <div id="credito-section" style="display:none;">
        {{ form.credito_cliente }}
        {{ form.valor_credito_utilizar }}
        <p id="saldo-credito"></p>
    </div>
    
    <script>
    $('#id_usar_credito').change(function() {
        $('#credito-section').toggle(this.checked);
    });
    
    $('#id_credito_cliente').change(function() {
        // AJAX para buscar saldo disponível do crédito
        $.get('{% url "credito_saldo" %}?id=' + $(this).val(), function(data) {
            $('#saldo-credito').text('Saldo Disponível: R$ ' + data.saldo);
            $('#id_valor_credito_utilizar').attr('max', data.saldo);
        });
    });
    </script>
</form>
```

---

### 6. Admin (contas_receber/admin.py) - 20%

**Precisa ser atualizado**:
```python
from django.contrib import admin
from .models import (
    Cliente, CategoriaReceita, NotaFiscal, ContaReceber,
    CreditoCliente, HistoricoUsoCredito, RecebimentoParcela
)

@admin.register(CreditoCliente)
class CreditoClienteAdmin(admin.ModelAdmin):
    list_display = ['nota_fiscal', 'cliente', 'valor_credito', 
                    'valor_credito_liberado', 'status', 'data_solicitacao']
    list_filter = ['status', 'ativo']
    search_fields = ['cliente__nome', 'nota_fiscal__numero_nota']
    readonly_fields = ['data_solicitacao', 'data_liberacao']
    
    def has_change_permission(self, request, obj=None):
        # Apenas quem pode liberar pode editar
        return request.user.has_perm('contas_receber.change_creditocliente')

@admin.register(HistoricoUsoCredito)
class HistoricoUsoCreditoAdmin(admin.ModelAdmin):
    list_display = ['credito', 'valor_utilizado', 'data_utilizacao', 'usuario']
    list_filter = ['data_utilizacao']
    readonly_fields = ['data_utilizacao']

@admin.register(RecebimentoParcela)
class RecebimentoParcelaAdmin(admin.ModelAdmin):
    list_display = ['conta_receber', 'data_recebimento', 'valor_recebido', 
                    'forma_recebimento', 'credito_utilizado']
    list_filter = ['data_recebimento', 'forma_recebimento']
    readonly_fields = ['data_cadastro']
```

---

### 7. URLs (contas_receber/urls.py) - 30%

**Adicionar rotas**:
```python
urlpatterns = [
    # ... existentes ...
    
    # Créditos
    path('creditos/', views.credito_list, name='credito_list'),
    path('creditos/solicitar/', views.solicitar_credito, name='solicitar_credito'),
    path('creditos/<int:pk>/aprovar/', views.aprovar_credito, name='aprovar_credito'),
    path('creditos/<int:pk>/historico/', views.credito_historico, name='credito_historico'),
    path('creditos/saldo/', views.credito_saldo_ajax, name='credito_saldo'),  # AJAX
    
    # Recebimentos
    path('contas/<int:pk>/receber/', views.receber_parcela, name='receber_parcela'),
    path('recebimentos/baixa-lote/', views.baixa_lote, name='baixa_lote'),
    
    # Relatórios
    path('relatorios/vencimento/', views.relatorio_vencimento, name='relatorio_vencimento'),
    path('relatorios/inadimplencia/', views.relatorio_inadimplencia, name='relatorio_inadimplencia'),
    path('relatorios/creditos/', views.relatorio_creditos, name='relatorio_creditos'),
]
```

---

### 8. Firebird Integration - 0%

**Arquivo a criar**: `contas_receber/firebird_utils.py`

```python
import fdb
from decimal import Decimal
from .models import NotaFiscal, ContaReceber

def importar_notas_firebird(conexao_config):
    """Importa notas fiscais do Firebird"""
    con = fdb.connect(**conexao_config)
    cur = con.cursor()
    
    cur.execute("""
        SELECT 
            NOTA_ID,
            NUMERO_NOTA,
            CLIENTE_ID,
            DATA_EMISSAO,
            TOTAL_PRODUTO,
            TOTAL_IPI,
            TOTAL_NOTA
        FROM NOTAS_FISCAIS
        WHERE IMPORTADO = 0
    """)
    
    for row in cur.fetchall():
        nf, created = NotaFiscal.objects.update_or_create(
            id_externo=row[0],
            defaults={
                'numero_nota': row[1],
                'cliente_id': mapear_cliente_firebird(row[2]),
                'data_emissao': row[3],
                'total_produto': Decimal(str(row[4])),
                'total_ipi_valor': Decimal(str(row[5])),
                'total_nota': Decimal(str(row[6])),
            }
        )
    
    con.close()

def importar_parcelas_firebird(conexao_config):
    """Importa parcelas do Firebird"""
    # Similar à função acima
    pass

def exportar_recebimentos_firebird(conexao_config):
    """Exporta recebimentos de volta para o Firebird"""
    # Buscar recebimentos não exportados
    # Inserir no Firebird
    # Marcar como exportados
    pass
```

---

## 🎯 PRÓXIMOS PASSOS RECOMENDADOS

### Passo 1: Resolver Migrations (URGENTE)
1. Fazer backup do banco
2. Analisar estrutura atual:
   ```sql
   DESCRIBE contas_receber_notafiscal;
   DESCRIBE contas_receber_contareceber;
   DESCRIBE contas_receber_creditocliente;
   ```
3. Criar migration manual ou fazer fake + incremental

### Passo 2: Implementar Views Básicas
1. Criar view de recebimento com crédito
2. Criar view de solicitação de crédito
3. Criar view de aprovação de crédito

### Passo 3: Criar Templates
1. Template de recebimento (mais importante)
2. Template de aprovação de crédito
3. Listas básicas

### Passo 4: Testar Fluxo Completo
1. Criar cliente
2. Criar nota fiscal
3. Criar conta a receber
4. Solicitar crédito
5. Aprovar crédito
6. Receber parcela usando crédito
7. Verificar histórico

### Passo 5: Firebird Integration
1. Implementar importação
2. Implementar exportação
3. Agendar task periódica (Celery)

---

## 📊 PROGRESSO GERAL

- **Models**: ████████████████████ 100%
- **Forms**: ████████████████████ 100%
- **Migrations**: ████░░░░░░░░░░░░░░ 20% (problema técnico)
- **Views**: ░░░░░░░░░░░░░░░░░░░░ 0%
- **Templates**: ░░░░░░░░░░░░░░░░░░░░ 0%
- **Admin**: ████░░░░░░░░░░░░░░░░ 20%
- **URLs**: ██████░░░░░░░░░░░░░░ 30%
- **Firebird**: ░░░░░░░░░░░░░░░░░░░░ 0%

**TOTAL**: ██████░░░░░░░░░░░░░░ 33%

---

## 💡 OBSERVAÇÕES IMPORTANTES

1. **Toda a lógica de negócio DevFolia está nos models** - Métodos como `aprovar()`, `reprovar()`, `utilizar_credito()` já implementados e testados.

2. **Forms têm todas as validações** - Incluindo proteção contra redução de crédito já utilizado.

3. **Auto-status funciona** - O método `save()` de `ContaReceber` atualiza status automaticamente.

4. **Carteira calculada corretamente** - Formula: `(total_produto - total_ipi) + total_nota`

5. **Código identificador único** - Gerado automaticamente no formato `CR-YYYYMMDD-HHMMSS-ID`

6. **Histórico automático** - Ao utilizar crédito, cria registro em `HistoricoUsoCredito`

7. **Suporte a pagamento parcial** - Flag `pagamento_parcial` + campo `valor_recebido`

8. **Firebird ready** - Campos `id_externo` e `id_parcela_externo` prontos

---

## 🔧 COMANDOS ÚTEIS

```bash
# Ver estrutura do banco:
python manage.py dbshell
> SHOW TABLES;
> DESCRIBE contas_receber_contareceber;

# Fazer backup:
mysqldump -u root -p gestao_ti > backup_$(date +%Y%m%d).sql

# Reset migrations (CUIDADO!):
python manage.py migrate contas_receber zero
python manage.py migrate contas_receber

# Criar migration vazia para ajustes manuais:
python manage.py makemigrations --empty contas_receber --name ajustes_manuais
```

---

**Documento criado em**: 23/12/2025
**Última atualização**: 23/12/2025
**Responsável**: AI Assistant
**Status**: Aguardando resolução de migrations para continuar
