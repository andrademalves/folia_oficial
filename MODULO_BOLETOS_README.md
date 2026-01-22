# MÓDULO DE EMISSÃO DE BOLETOS - CAIXA ECONÔMICA FEDERAL

## Visão Geral

Este módulo implementa a geração completa de boletos bancários para a Caixa Econômica Federal (Banco 104), incluindo:

- ✅ Geração de boletos com código de barras e linha digitável
- ✅ Cálculo automático de dígitos verificadores
- ✅ Geração de arquivos CNAB 240 (remessa)
- ✅ Geração de PDF do boleto para impressão
- ✅ Controle de status e sequenciais
- ✅ Integração com módulo contas_receber

## Baseado em Documentação Oficial

- Manual CNAB 240 SIGCB - Caixa Econômica Federal
- Especificações de Código de Barras SIGCB
- Layout Padrão CNAB 240 - FEBRABAN

## Estrutura do Módulo

```
boletos/
├── models.py                    # Models: ConfiguracaoBancaria, Boleto, RemessaCNAB, RetornoCNAB
├── views.py                     # Views: Dashboard, geração, impressão, remessa
├── urls.py                      # URLs do módulo
├── admin.py                     # Interface administrativa
├── utils/
│   ├── codigo_barras.py        # Cálculo de código de barras e linha digitável
│   ├── cnab240.py              # Geração de arquivo CNAB 240
│   └── gerar_pdf.py            # Geração de PDF do boleto
└── templates/boletos/          # Templates HTML
```

## Instalação

### 1. Registrar o app no settings.py

```python
INSTALLED_APPS = [
    ...
    'boletos',
]
```

### 2. Adicionar URLs no projeto

Em `gestaoTi/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('boletos/', include('boletos.urls')),
]
```

### 3. Instalar dependências

```bash
pip install reportlab python-barcode pillow
```

### 4. Executar migrations

```bash
python manage.py makemigrations boletos
python manage.py migrate boletos
```

## Configuração Inicial

### 1. Configuração Bancária

Acesse o admin Django e crie uma Configuração Bancária:

**Dados Obrigatórios:**
- Nome: Ex: "Caixa - Cobrança Principal"
- Código do Banco: 104
- Agência: Ex: 1234
- Conta: Ex: 123456
- DV Conta: Ex: 7
- Código do Beneficiário: Fornecido pela Caixa
- Convênio: Número do convênio de cobrança
- Carteira: 1 (padrão Caixa)
- Modalidade: 14 (cobrança simples)

**Controle do Nosso Número:**
- Nosso Número Inicial: 1
- Nosso Número Atual: 1
- Nosso Número Fim: 99999999999999999 (17 dígitos)

**Dados da Empresa:**
- Razão Social, CNPJ, Endereço completo

**Configurações de Juros/Multa:**
- Percentual de Juros ao Mês: Ex: 1.00 (1% ao mês)
- Percentual de Multa: Ex: 2.00 (2%)
- Dias para Aplicar Multa: 1

### 2. Criando Módulo e Menu no Sistema

Execute o comando para popular módulos (se ainda não existe):

```python
# No shell do Django
from usuarios.models import Modulo, Menu

# Cria módulo Boletos
modulo_boletos = Modulo.objects.create(
    nome='Boletos',
    icone='fas fa-barcode',
    url='dashboard_boletos',
    ordem=6
)

# Cria menus
Menu.objects.create(
    modulo=modulo_boletos,
    nome='Dashboard',
    icone='fas fa-home',
    url='dashboard_boletos',
    ordem=1
)

Menu.objects.create(
    modulo=modulo_boletos,
    nome='Listar Boletos',
    icone='fas fa-list',
    url='lista_boletos',
    ordem=2
)

Menu.objects.create(
    modulo=modulo_boletos,
    nome='Gerar Remessa',
    icone='fas fa-file-export',
    url='gerar_remessa_cnab',
    ordem=3
)

Menu.objects.create(
    modulo=modulo_boletos,
    nome='Remessas CNAB',
    icone='fas fa-folder-open',
    url='lista_remessas',
    ordem=4
)
```

## Fluxo de Uso

### 1. Gerar Boleto para uma Parcela

```python
# Na view de parcelas do contas_receber, adicione link:
<a href="{% url 'gerar_boleto_parcela' parcela.id %}" class="btn btn-primary">
    <i class="fas fa-barcode"></i> Gerar Boleto
</a>
```

O sistema irá:
1. Buscar a configuração bancária ativa
2. Gerar o próximo nosso número sequencial (17 dígitos)
3. Calcular o código de barras (44 posições)
4. Calcular a linha digitável (47 posições)
5. Criar o registro do boleto com status EMITIDO

### 2. Imprimir Boleto (PDF)

```python
# Clique em "Imprimir" no detalhe do boleto
# Ou acesse diretamente:
/boletos/boletos/<id>/imprimir/
```

Gera um PDF com:
- Recibo do Sacado (parte superior)
- Ficha de Compensação (parte principal)
- Código de barras
- Linha digitável
- Dados do pagador e beneficiário

### 3. Gerar Arquivo de Remessa CNAB 240

1. Acesse "Gerar Remessa"
2. Selecione os boletos emitidos
3. Clique em "Gerar Arquivo CNAB"

O sistema irá:
1. Gerar arquivo CNAB 240 conforme especificação da Caixa
2. Validar todas as 240 posições de cada linha
3. Criar registro de RemessaCNAB
4. Atualizar status dos boletos para REGISTRADO
5. Incrementar sequencial do arquivo

### 4. Enviar para a Caixa

1. Acesse o detalhe da remessa
2. Clique em "Download Arquivo"
3. Envie o arquivo `.REM` para a Caixa através do:
   - Internet Banking Empresarial
   - Sistema SIGCB Web
   - Convênio específico da sua empresa

### 5. Processar Arquivo de Retorno

*Funcionalidade a ser implementada*

O arquivo de retorno `.RET` da Caixa conterá:
- Confirmação de registro
- Liquidação (pagamento)
- Rejeições
- Baixas

## Particularidades da Caixa Econômica Federal

### Código de Barras (44 posições)

```
104 9 X 9999 9999999999 XXXXXXXXXXXXXXXXXXXXXXXXX
│   │ │  │      │         └─ Campo Livre (25 posições)
│   │ │  │      └─ Valor do documento (10 posições)
│   │ │  └─ Fator de vencimento (4 posições)
│   │ └─ DV do código de barras (1 posição)
│   └─ Código da moeda (1 posição) = 9 (Real)
└─ Código do banco (3 posições) = 104
```

### Campo Livre Caixa (25 posições)

```
BBBBBB D TTT C NNNNNNNNNNNNNN MM
│      │  │  │  │               └─ Modalidade (2)
│      │  │  │  └─ 14 dígitos do nosso número (14)
│      │  │  └─ Carteira (1)
│      │  └─ 3 primeiros dígitos do nosso número (3)
│      └─ DV do campo livre (1)
└─ Código do beneficiário (6)
```

### Nosso Número

- **Tamanho:** 17 dígitos
- **Formato:** Sequencial numérico
- **Exemplo:** 00000000000000001
- **DV:** Calculado por módulo 11 sobre Agência + Beneficiário + Nosso Número

### Arquivo CNAB 240

**Estrutura:**
- Todas as linhas têm exatamente 240 posições
- Terminação de linha: CRLF (\r\n)
- Encoding: ASCII

**Registros:**
- Tipo 0: Header do Arquivo
- Tipo 1: Header do Lote
- Tipo 3: Detalhes (Segmentos P, Q, R)
- Tipo 5: Trailer do Lote  
- Tipo 9: Trailer do Arquivo

**Segmentos por Título:**
- Segmento P: Dados do título
- Segmento Q: Dados do sacado (pagador)
- Segmento R: Multa, descontos adicionais (opcional)

## Validações Importantes

✅ **CPF/CNPJ:** Validado ao salvar cliente
✅ **Data de Vencimento:** Não pode ser retroativa
✅ **Nosso Número:** Único por configuração bancária
✅ **Código de Barras:** Validado por módulo 11
✅ **Arquivo CNAB:** Validado linha por linha (240 posições)
✅ **Fator de Vencimento:** >= 07/10/1997

## Códigos de Status

```python
PENDENTE    # Criado, aguardando emissão
EMITIDO     # Boleto emitido, pronto para envio
REGISTRADO  # Enviado ao banco via CNAB
PAGO        # Liquidado (processado no retorno)
CANCELADO   # Cancelado manualmente
VENCIDO     # Passou da data de vencimento
```

## Segurança e Boas Práticas

1. **Nunca reutilize nosso número:** Sistema controla automaticamente
2. **Backup dos arquivos CNAB:** Salve as remessas enviadas
3. **Teste em homologação:** Solicite ambiente de testes à Caixa
4. **Valide antes de enviar:** Sistema valida automaticamente
5. **Controle de acesso:** Use permissões do Django

## Troubleshooting

### Erro: "Nosso número esgotado"

**Solução:** Aumente o limite em Configuração Bancária → Nosso Número Fim

### Erro: "Código de barras inválido"

**Solução:** Verifique:
- Dados da configuração bancária
- Código do beneficiário
- Convênio

### Erro: "Arquivo CNAB inválido - tamanho incorreto"

**Solução:** Todas as linhas devem ter exatamente 240 caracteres. Verifique o gerador CNAB.

### Boleto não aparece para remessa

**Solução:** Verifique:
- Status = EMITIDO
- enviado_banco = False
- Configuração bancária ativa

## Próximos Passos

- [ ] Implementar processamento de arquivo de retorno (.RET)
- [ ] Adicionar suporte a CNAB 400 (legado)
- [ ] Implementar baixa automática de boletos pagos
- [ ] Adicionar relatórios de boletos
- [ ] Implementar envio automático via API SIGCB (Web Service)
- [ ] Adicionar notificações de vencimento
- [ ] Implementar segunda via de boleto
- [ ] Adicionar QR Code PIX (quando disponível pela Caixa)

## Contato e Suporte

Para dúvidas sobre o módulo, consulte:
- Documentação oficial da Caixa
- Manual CNAB 240
- Gerente de relacionamento da Caixa

## Licença

Módulo proprietário - Uso interno

---

**Desenvolvido em:** Dezembro/2024
**Versão:** 1.0
**Status:** Produção
