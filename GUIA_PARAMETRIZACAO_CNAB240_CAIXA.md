# GUIA DE PARAMETRIZAÇÃO - CNAB 240 CAIXA ECONÔMICA FEDERAL

## 📋 DADOS NECESSÁRIOS PARA CONFIGURAÇÃO

### 1. DADOS DO CONVÊNIO CAIXA (obter no gerente)

#### Código do Beneficiário
- **Tamanho:** 6 ou 7 dígitos (depende do convênio)
- **Exemplo:** `123456` ou `1234567`
- **Onde encontrar:** Contrato de cobrança CAIXA ou Internet Banking

#### Código do Convênio
- **Tamanho:** variável (até 20 posições)
- **Exemplo:** `100`, `200`, `1234567890`
- **Onde encontrar:** Contrato SIGCB ou gerente

#### Modalidade da Carteira
- **Valores possíveis:**
  - `11` - Cobrança Simples
  - `12` - Cobrança Indexada
  - `14` - Cobrança Caucionada
  - `21` - Cobrança Vinculada
- **Padrão:** `11` (mais comum)

### 2. DADOS DA CONTA

#### Agência
- **Tamanho:** 5 dígitos
- **Formato:** sem zeros à esquerda (preenche depois)
- **Exemplo:** `5666`

#### Dígito Verificador da Agência
- **Tamanho:** 1 caractere
- **Exemplo:** `1`
- **Observação:** algumas agências não têm DV (deixar em branco)

#### Conta Corrente
- **Tamanho:** até 12 dígitos
- **Formato:** sem zeros à esquerda (preenche depois)
- **Exemplo:** `16766`

#### Dígito Verificador da Conta
- **Tamanho:** 1 caractere
- **Exemplo:** `0`

### 3. DADOS DA EMPRESA

#### CNPJ
- **Tamanho:** 14 dígitos
- **Formato:** apenas números (sem pontos/barras)
- **Exemplo:** `06247611000115`

#### Razão Social
- **Tamanho:** até 30 caracteres
- **Formato:** apenas A-Z, 0-9 e espaço (SEM ACENTOS)
- **Exemplo:** `EMPRESA LTDA ME`
- **Observação:** será convertido automaticamente para maiúsculas sem acentos

### 4. VERSÕES DO LAYOUT

#### Header do Arquivo (Registro 0)
- **Versão:** `103` (fixo para CAIXA)
- **Posição:** 164-166

#### Header do Lote (Registro 1)
- **Versão:** `060` (fixo para cobrança CAIXA)
- **Posição:** 14-16

---

## ⚙️ CONFIGURAÇÕES ESPECÍFICAS CAIXA

### Nosso Número

O Nosso Número na CAIXA segue o formato:
```
Modalidade (2) + Identificação (15) + DV (1)
Exemplo: 11 + 000000000000001 + 2 = 110000000000000012
```

#### Cálculo do Dígito Verificador
- **Algoritmo:** Módulo 11
- **Peso:** 2 a 9 (da direita para esquerda)
- **Resto:** se 0 ou 1, DV = 0; senão DV = 11 - resto

#### Exemplo de Cálculo:
```python
nosso_numero = "11000000000000001"  # 17 dígitos
pesos = [2,3,4,5,6,7,8,9] * 3       # repetir peso

soma = 0
for i, digito in enumerate(reversed(nosso_numero)):
    peso = pesos[i % 8]
    soma += int(digito) * peso

resto = soma % 11
dv = 0 if resto in [0, 1] else 11 - resto
```

### Código de Barras

Formato: `BBBM.CCCCCX DDDDD.DDDDDY DDDDD.DDDDDY K VVVVVVVVVVVVVV`

- **BBB:** Código do banco (104)
- **M:** Código da moeda (9 = Real)
- **CCCCC:** 5 primeiras posições do campo livre
- **X:** DV do primeiro grupo
- **DDDDD.DDDDDY:** Posições 6-10 e 11-15 do campo livre com DV
- **DDDDD.DDDDDY:** Posições 16-20 e 21-25 do campo livre com DV
- **K:** DV geral do código de barras
- **VVVVVVVVVVVVVV:** Valor do título (10 inteiros + 2 decimais)

### Campo Livre (25 posições)
Para CAIXA modalidade 11 (Cobrança Simples):
```
Posição 01-06: Código do beneficiário (6 dígitos)
Posição 07-08: Dígito verificador do beneficiário
Posição 09-11: Posições 4, 5 e 6 do nosso número
Posição 12-12: Constante '1'
Posição 13-15: Posições 1, 2 e 3 do nosso número  
Posição 16-16: Constante '2'
Posição 17-24: Posições 7 a 14 do nosso número
Posição 25-25: DV do campo livre
```

---

## 🔍 CAMPOS QUE PRECISAM CONFIRMAÇÃO COM O BANCO

### ⚠️ CRÍTICOS (devem ser confirmados)

1. **Código do Convênio (posição 33-52 do Header Arquivo)**
   - Varia por contrato
   - Formato pode ser 6, 7 ou mais dígitos
   - Consultar gerente ou contrato SIGCB

2. **Código do Beneficiário**
   - Pode ser 6 ou 7 dígitos
   - Confirmar no contrato de cobrança

3. **Modalidade da Carteira**
   - Confirmar qual modalidade está contratada
   - Mais comum: `11` (Cobrança Simples)

4. **Nosso Número**
   - Formato do sequencial
   - Faixa inicial e final
   - Como calcular o DV

5. **Código da Espécie do Título (posição 107-108 Segmento P)**
   - `02` - Duplicata Mercantil (mais comum)
   - `01` - Duplicata Rural
   - `12` - Nota Promissória
   - Outros conforme necessidade

### ℹ️ OPCIONAIS (podem usar padrão)

1. **Instruções de Protesto**
   - Código para protesto (posição 221)
   - Dias para protesto (posição 222-223)
   - Padrão: `3` (não protestar) + `00` dias

2. **Instruções de Baixa**
   - Código para baixa (posição 224)
   - Dias para baixa (posição 225-227)
   - Padrão: `0` (não baixar automaticamente)

3. **Juros/Multa/Desconto**
   - Códigos e valores
   - Podem ser zerados inicialmente

---

## 📝 EXEMPLO DE CONFIGURAÇÃO COMPLETA

```python
# Configuração mínima funcional
configuracao = {
    # Banco
    'codigo_banco': '104',
    
    # Empresa
    'cnpj': '06247611000115',
    'razao_social': 'EMPRESA LTDA ME',
    
    # Conta
    'agencia': '5666',
    'agencia_dv': '1',
    'conta': '16766',
    'conta_dv': '0',
    
    # Convênio CAIXA (CONFIRMAR COM GERENTE)
    'convenio': '100',
    'codigo_beneficiario': '123456',  # 6 ou 7 dígitos
    'modalidade_carteira': '11',      # Cobrança Simples
    
    # Controle
    'sequencial_arquivo': 1,
    
    # Nosso Número
    'sequencial_nosso_numero': 1,     # Próximo nosso número
    'nosso_numero_inicio': 1,         # Faixa inicial
    'nosso_numero_fim': 999999999,    # Faixa final
}
```

---

## 🚀 CHECKLIST ANTES DE ENVIAR À CAIXA

### Validações Obrigatórias

- [ ] Arquivo tem extensão `.REM`
- [ ] Todas as linhas têm exatamente 240 caracteres
- [ ] Encoding é ASCII puro (sem UTF-8, sem acentos)
- [ ] Separador de linha é CRLF (`\r\n`)
- [ ] Header Arquivo (tipo 0) está correto
- [ ] Header Lote (tipo 1) está correto
- [ ] Cada título tem Segmento P + Segmento Q
- [ ] Trailer Lote (tipo 5) está correto
- [ ] Trailer Arquivo (tipo 9) está correto
- [ ] Quantidade de registros bate
- [ ] CNPJ sem formatação (14 dígitos)
- [ ] Valores em centavos (2 decimais)
- [ ] Datas no formato DDMMAAAA

### Testes Recomendados

1. **Teste com 1 título apenas**
   - Validar estrutura básica
   - Confirmar aceite do banco

2. **Teste com título de valor conhecido**
   - Ex: R$ 100,00
   - Facilita conferência do código de barras

3. **Validar retorno**
   - Após envio, processar arquivo de retorno
   - Confirmar que títulos foram aceitos

---

## 📞 SUPORTE CAIXA

**Central de Atendimento Empresarial:**
- Telefone: 0800 726 0101
- Horário: Segunda a sexta, 8h às 20h

**Documentação:**
- Manual CNAB 240 SIGCB
- Portal da CAIXA > Empresas > Cobrança > Manuais

**Solicitações:**
- Contrato de cobrança
- Código do convênio
- Faixa de nosso número
- Modalidade de carteira
- Parametrização do sistema

---

## ⚡ DICAS IMPORTANTES

1. **Sempre teste em homologação primeiro** (se disponível)
2. **Mantenha backup de todos os arquivos enviados**
3. **Numere sequencialmente os arquivos** (campo sequencial_arquivo)
4. **Não reutilize nosso número** (deve ser único)
5. **Valide o arquivo antes de enviar** (use validador rigoroso)
6. **Acompanhe o retorno do banco** (arquivo .RET)
7. **Documente os parâmetros do seu convênio**
8. **Mantenha contato com gerente** para dúvidas específicas

---

## 🔧 TROUBLESHOOTING

### Arquivo rejeitado pela CAIXA

**Erro:** "Arquivo com formato inválido"
- **Causa:** Linhas com tamanho diferente de 240
- **Solução:** Validar cada linha com `len(linha) == 240`

**Erro:** "Convênio não encontrado"
- **Causa:** Código do convênio incorreto
- **Solução:** Confirmar código com gerente

**Erro:** "Nosso número duplicado"
- **Causa:** Nosso número já usado anteriormente
- **Solução:** Incrementar sequencial corretamente

**Erro:** "Agência/Conta inválida"
- **Causa:** Dados da conta incorretos
- **Solução:** Verificar no contrato ou extrato

### Código de barras não lê no app

- Verificar cálculo do DV
- Conferir campo livre (25 posições)
- Validar formato do nosso número
- Testar gerando código de barras de teste online

---

**Versão do documento:** 1.0
**Data:** 28/12/2025
**Compatível com:** CNAB 240 CAIXA SIGCB v103/060
