"""
Geração de Código de Barras e Linha Digitável para Caixa Econômica Federal
Baseado nas especificações do manual ESP_COD_BARRAS_SIGCB_COBRANCA_CAIXA.pdf
"""
from datetime import datetime, date
from decimal import Decimal


def modulo10(numero):
    """
    Cálculo do dígito verificador pelo módulo 10
    Usado para verificar campos da linha digitável
    """
    try:
        numero = str(numero)  # Garante que é string
        sequencia = [2, 1] * (len(numero) // 2 + 1)
        soma = 0
        
        for i, digito in enumerate(reversed(numero)):
            if not digito.isdigit():
                raise ValueError(f"Caractere inválido '{digito}' na posição {len(numero)-i-1} do número '{numero}'")
            resultado = int(digito) * sequencia[i]
            if resultado > 9:
                resultado = sum(int(d) for d in str(resultado))
            soma += resultado
        
        resto = soma % 10
        return 0 if resto == 0 else 10 - resto
    except Exception as e:
        raise ValueError(f"Erro no modulo10 com número '{numero}': {str(e)}")


def modulo11(numero, base=9):
    """
    Cálculo do dígito verificador pelo módulo 11
    Usado para verificar o código de barras completo
    """
    try:
        numero = str(numero)  # Garante que é string
        sequencia = list(range(2, base + 1))
        soma = 0
        
        for i, digito in enumerate(reversed(numero)):
            if not digito.isdigit():
                raise ValueError(f"Caractere inválido '{digito}' na posição {len(numero)-i-1} do número '{numero}'")
            soma += int(digito) * sequencia[i % len(sequencia)]
        
        resto = soma % 11
        
        if resto in [0, 1, 10]:
            return 1
        else:
            return 11 - resto
    except Exception as e:
        raise ValueError(f"Erro no modulo11 com número '{numero}': {str(e)}")


def calcular_fator_vencimento(data_vencimento):
    """
    Calcula o fator de vencimento baseado na data
    Fator = número de dias entre 07/10/1997 e a data de vencimento
    """
    try:
        # Converte datetime para date se necessário
        if hasattr(data_vencimento, 'date'):
            data_vencimento = data_vencimento.date()
        elif isinstance(data_vencimento, str):
            # Tenta diferentes formatos de data
            for formato in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    data_vencimento = datetime.strptime(data_vencimento, formato).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Formato de data inválido: '{data_vencimento}'. Use YYYY-MM-DD, DD/MM/YYYY ou DD-MM-YYYY")
        
        data_base = date(1997, 10, 7)
        delta = data_vencimento - data_base
        fator = delta.days
        
        # Validação: fator deve ser positivo
        if fator < 0:
            raise ValueError('Data de vencimento não pode ser anterior a 07/10/1997')
        
        # IMPORTANTE: O fator de vencimento deve ter exatamente 4 dígitos
        # Quando passa de 9999, usa módulo 10000 para manter 4 dígitos
        # Referência: FEBRABAN - após 21/02/2025 o fator passa de 9999
        if fator > 9999:
            fator = fator % 10000
        
        return str(fator).zfill(4)
    except Exception as e:
        raise ValueError(f"Erro ao calcular fator de vencimento com data '{data_vencimento}' (tipo: {type(data_vencimento).__name__}): {str(e)}")


def formatar_valor(valor):
    """
    Formata o valor para 10 dígitos sem vírgula
    Ex: 1234.56 -> 0000123456
    """
    try:
        if isinstance(valor, str):
            # Remove caracteres não numéricos exceto ponto e vírgula
            valor = valor.replace(',', '.')
            valor = Decimal(valor)
        elif not isinstance(valor, Decimal):
            valor = Decimal(str(valor))
        
        valor_centavos = int(valor * 100)
        return str(valor_centavos).zfill(10)
    except Exception as e:
        raise ValueError(f"Erro ao formatar valor '{valor}': {str(e)}")


def gerar_nosso_numero(configuracao):
    """
    Gera o nosso número sequencial de 17 dígitos para a Caixa
    """
    proximo = configuracao.proximo_nosso_numero()
    return str(proximo).zfill(17)


def calcular_dv_nosso_numero_caixa(nosso_numero, agencia, beneficiario):
    """
    Calcula o dígito verificador do nosso número específico da Caixa
    Composição: Agência (4) + Beneficiário (6) + Nosso Número (17)
    """
    campo = str(agencia).zfill(4) + str(beneficiario).zfill(6) + str(nosso_numero).zfill(17)
    return str(modulo11(campo))


def gerar_codigo_barras(boleto):
    """
    Gera o código de barras de 44 posições para boleto da Caixa
    
    Estrutura do código de barras (44 posições):
    - Posição 01-03: Código do banco (104 = Caixa)
    - Posição 04: Código da moeda (9 = Real)
    - Posição 05: DV do código de barras (calculado por módulo 11)
    - Posição 06-09: Fator de vencimento
    - Posição 10-19: Valor do documento (10 posições sem vírgula)
    - Posição 20-44: Campo livre (25 posições - específico da Caixa)
    
    Campo Livre da Caixa (25 posições):
    - Posição 20-25: Código do Beneficiário (6 posições)
    - Posição 26: DV do campo livre
    - Posição 27-29: Três primeiras posições do nosso número
    - Posição 30: Código da carteira (1)
    - Posição 31-47: 14 posições restantes do nosso número
    - Posição 48-49: Modalidade de cobrança
    """
    config = boleto.configuracao
    
    # Validações
    if not config.codigo_beneficiario or not str(config.codigo_beneficiario).isdigit():
        raise ValueError(f"Código do Beneficiário inválido: '{config.codigo_beneficiario}'. Deve conter apenas números.")
    
    if not config.codigo_banco or not str(config.codigo_banco).isdigit():
        raise ValueError(f"Código do Banco inválido: '{config.codigo_banco}'. Deve conter apenas números.")
    
    if not config.agencia or not str(config.agencia).isdigit():
        raise ValueError(f"Agência inválida: '{config.agencia}'. Deve conter apenas números.")
    
    if not config.carteira or not str(config.carteira).isdigit():
        raise ValueError(f"Carteira inválida: '{config.carteira}'. Deve conter apenas números.")
    
    if not config.modalidade or not str(config.modalidade).isdigit():
        raise ValueError(f"Modalidade inválida: '{config.modalidade}'. Deve conter apenas números.")
    
    # Posições 01-04: Banco e Moeda
    codigo_banco = str(config.codigo_banco).zfill(3)  # 104
    codigo_moeda = '9'  # Real
    
    # Posições 06-09: Fator de vencimento
    fator_vencimento = calcular_fator_vencimento(boleto.data_vencimento)
    
    # Posições 10-19: Valor
    valor = formatar_valor(boleto.valor_documento)
    
    # Campo Livre (25 posições)
    # IMPORTANTE: Beneficiário deve ter exatamente 6 posições
    # Se tiver mais, pega os 6 últimos; se tiver menos, completa com zeros à esquerda
    beneficiario = str(config.codigo_beneficiario).zfill(6)[-6:]  # Garante 6 posições
    nosso_numero = str(boleto.nosso_numero).zfill(17)
    
    # Monta campo livre conforme especificação CAIXA SIGCB
    # Estrutura do Campo Livre (25 posições):
    # Pos 01-06: Código do Beneficiário (6)
    # Pos 07-07: DV do campo livre (1)
    # Pos 08-10: Três primeiras posições do nosso número (3)
    # Pos 11-11: Código da carteira (1)
    # Pos 12-23: 12 posições restantes do nosso número (12)
    # Pos 24-25: Modalidade de cobrança (2)
    
    campo_livre = beneficiario  # 6 posições
    
    # DV do campo livre (posição 7)
    dv_campo_livre = calcular_dv_nosso_numero_caixa(
        nosso_numero, 
        config.agencia, 
        beneficiario
    )
    campo_livre += dv_campo_livre  # 1 posição (total: 7)
    
    # Três primeiras posições do nosso número
    campo_livre += nosso_numero[:3]  # 3 posições (total: 10)
    
    # Código da carteira (1 dígito apenas)
    campo_livre += str(config.carteira)[-1:]  # 1 posição (total: 11)
    
    # 12 posições restantes do nosso número (posições 4 a 15)
    campo_livre += nosso_numero[3:15]  # 12 posições (total: 23)
    
    # Modalidade de cobrança (2 posições no final)
    campo_livre += str(config.modalidade).zfill(2)  # 2 posições (total: 25)
    
    # Campo livre deve ter exatamente 25 posições
    if len(campo_livre) != 25:
        raise ValueError(f"Campo livre deve ter 25 posições, mas tem {len(campo_livre)}: '{campo_livre}'")
    
    # Monta código sem DV (43 posições)
    codigo_sem_dv = (
        codigo_banco +       # 3
        codigo_moeda +       # 1
        fator_vencimento +   # 4
        valor +              # 10
        campo_livre          # 25
    )
    
    # Calcula DV do código de barras (posição 5)
    dv = modulo11(codigo_sem_dv)
    
    # Monta código completo inserindo DV na posição 5
    codigo_barras = (
        codigo_banco +       # Posições 1-3
        codigo_moeda +       # Posição 4
        str(dv) +           # Posição 5
        fator_vencimento +   # Posições 6-9
        valor +              # Posições 10-19
        campo_livre          # Posições 20-44
    )
    
    return codigo_barras


def gerar_linha_digitavel(codigo_barras):
    """
    Gera a linha digitável de 47 posições a partir do código de barras
    
    A linha digitável é dividida em 5 campos:
    Campo 1: Banco(3) + Moeda(1) + Primeiras 5 do campo livre + DV (10 posições)
    Campo 2: Posições 6-15 do campo livre + DV (11 posições)
    Campo 3: Posições 16-25 do campo livre + DV (11 posições)
    Campo 4: DV do código de barras (1 posição)
    Campo 5: Fator vencimento(4) + Valor(10) (14 posições)
    """
    
    # Extrai partes do código de barras
    banco = codigo_barras[0:3]
    moeda = codigo_barras[3:4]
    dv_geral = codigo_barras[4:5]
    fator = codigo_barras[5:9]
    valor = codigo_barras[9:19]
    campo_livre = codigo_barras[19:44]
    
    # Campo 1: Banco + Moeda + Primeiras 5 do campo livre
    campo1 = banco + moeda + campo_livre[0:5]
    dv1 = modulo10(campo1)
    campo1_formatado = f"{campo1[0:5]}.{campo1[5:]}{dv1}"
    
    # Campo 2: Posições 6-15 do campo livre
    campo2 = campo_livre[5:15]
    dv2 = modulo10(campo2)
    campo2_formatado = f"{campo2[0:5]}.{campo2[5:]}{dv2}"
    
    # Campo 3: Posições 16-25 do campo livre
    campo3 = campo_livre[15:25]
    dv3 = modulo10(campo3)
    campo3_formatado = f"{campo3[0:5]}.{campo3[5:]}{dv3}"
    
    # Campo 4: DV do código de barras
    campo4 = dv_geral
    
    # Campo 5: Fator + Valor
    campo5 = fator + valor
    
    # Monta linha digitável
    linha_digitavel = (
        campo1_formatado + ' ' +
        campo2_formatado + ' ' +
        campo3_formatado + ' ' +
        campo4 + ' ' +
        campo5
    )
    
    return linha_digitavel


def validar_codigo_barras(codigo_barras):
    """
    Valida se um código de barras está correto
    """
    if len(codigo_barras) != 44:
        return False, "Código de barras deve ter 44 posições"
    
    # Extrai DV
    dv_informado = codigo_barras[4]
    
    # Monta código sem DV
    codigo_sem_dv = codigo_barras[0:4] + codigo_barras[5:]
    
    # Calcula DV esperado
    dv_calculado = str(modulo11(codigo_sem_dv))
    
    if dv_informado != dv_calculado:
        return False, f"DV inválido. Informado: {dv_informado}, Calculado: {dv_calculado}"
    
    return True, "Código de barras válido"


def formatar_codigo_barras_visual(codigo_barras):
    """
    Formata código de barras para exibição visual com espaços
    """
    return ' '.join([
        codigo_barras[0:4],
        codigo_barras[4:5],
        codigo_barras[5:9],
        codigo_barras[9:19],
        codigo_barras[19:24],
        codigo_barras[24:29],
        codigo_barras[29:34],
        codigo_barras[34:39],
        codigo_barras[39:44]
    ])
