"""
Geração de Arquivo CNAB 240 para Caixa Econômica Federal
Baseado no Manual_de_Leiaute_de_Arquivo_Eletronico_CNAB_240.pdf da Caixa
e no Layout Padrão FEBRABAN CNAB 240
"""
from datetime import datetime, date
from decimal import Decimal


class GeradorCNAB240:
    """
    Classe para gerar arquivo de remessa CNAB 240 para Caixa Econômica Federal
    """
    
    def __init__(self, configuracao):
        self.configuracao = configuracao
        self.linhas = []
        self.sequencial_registro = 0
        self.sequencial_lote = 1
        self.total_registros_lote = 0
        self.total_valor_lote = Decimal('0.00')
        self.total_titulos = 0
    
    def formatar_campo(self, valor, tamanho, tipo='X', decimais=0, alinhamento='esquerda'):
        """
        Formata um campo conforme especificação CNAB
        
        Args:
            valor: Valor a ser formatado
            tamanho: Tamanho do campo
            tipo: Tipo do campo (X=alfanumérico, 9=numérico)
            decimais: Quantidade de decimais (para numéricos)
            alinhamento: 'esquerda' ou 'direita'
        """
        if valor is None:
            valor = ''
        
        valor_str = str(valor)
        
        if tipo == '9':  # Numérico
            # Remove caracteres não numéricos
            valor_str = ''.join(c for c in valor_str if c.isdigit() or c == '.')
            
            if '.' in valor_str:
                partes = valor_str.split('.')
                inteiro = partes[0] if partes[0] else '0'
                decimal = partes[1] if len(partes) > 1 else '0'
                decimal = decimal[:decimais].ljust(decimais, '0')
                valor_str = inteiro + decimal
            
            valor_str = valor_str.zfill(tamanho)
        else:  # Alfanumérico
            valor_str = valor_str[:tamanho]
            if alinhamento == 'esquerda':
                valor_str = valor_str.ljust(tamanho)
            else:
                valor_str = valor_str.rjust(tamanho)
        
        return valor_str[:tamanho]
    
    def gerar_header_arquivo(self):
        """
        Gera o Header do Arquivo (Registro 0) - 240 posições
        """
        self.sequencial_registro += 1
        config = self.configuracao
        
        # Controle
        codigo_banco = self.formatar_campo(config.codigo_banco, 3, '9')  # Pos 1-3
        lote = self.formatar_campo('0', 4, '9')  # Pos 4-7 (0000 = header arquivo)
        tipo_registro = self.formatar_campo('0', 1, '9')  # Pos 8
        
        # Uso Exclusivo FEBRABAN
        brancos1 = self.formatar_campo('', 9, 'X')  # Pos 9-17
        
        # Dados da Empresa
        tipo_inscricao = self.formatar_campo('2', 1, '9')  # Pos 18 (2=CNPJ)
        cnpj = self.formatar_campo(config.cnpj.replace('.', '').replace('/', '').replace('-', ''), 14, '9')  # Pos 19-32
        convenio = self.formatar_campo(config.convenio, 20, 'X')  # Pos 33-52
        agencia = self.formatar_campo(config.agencia, 5, '9')  # Pos 53-57
        dv_agencia = self.formatar_campo(config.agencia_dv or ' ', 1, 'X')  # Pos 58
        conta = self.formatar_campo(config.conta, 12, '9')  # Pos 59-70
        dv_conta = self.formatar_campo(config.conta_dv, 1, 'X')  # Pos 71
        dv_ag_conta = self.formatar_campo(' ', 1, 'X')  # Pos 72
        nome_empresa = self.formatar_campo(config.razao_social, 30, 'X')  # Pos 73-102
        
        # Dados do Banco
        nome_banco = self.formatar_campo('CAIXA ECONOMICA FEDERAL', 30, 'X')  # Pos 103-132
        
        # Uso Exclusivo FEBRABAN
        brancos2 = self.formatar_campo('', 8, 'X')  # Pos 133-140
        
        # Código CNAB
        codigo_cnab = self.formatar_campo('05', 2, '9')  # Pos 141-142 (05 = CNAB 240)
        
        # Controle do Arquivo
        codigo_remessa = self.formatar_campo('1', 1, '9')  # Pos 143 (1=Remessa)
        data_geracao = self.formatar_campo(datetime.now().strftime('%d%m%Y'), 8, '9')  # Pos 144-151
        hora_geracao = self.formatar_campo(datetime.now().strftime('%H%M%S'), 6, '9')  # Pos 152-157
        sequencial_arquivo = self.formatar_campo(config.sequencial_arquivo, 6, '9')  # Pos 158-163
        versao_layout = self.formatar_campo('103', 3, '9')  # Pos 164-166 (103 = versão Caixa)
        densidade = self.formatar_campo('0', 5, '9')  # Pos 167-171
        
        # Reservado Banco/Empresa
        brancos3 = self.formatar_campo('', 20, 'X')  # Pos 172-191
        brancos4 = self.formatar_campo('', 20, 'X')  # Pos 192-211
        
        # Uso Exclusivo FEBRABAN
        brancos5 = self.formatar_campo('', 29, 'X')  # Pos 212-240
        
        linha = (
            codigo_banco + lote + tipo_registro + brancos1 +
            tipo_inscricao + cnpj + convenio + agencia + dv_agencia +
            conta + dv_conta + dv_ag_conta + nome_empresa + nome_banco +
            brancos2 + codigo_cnab + codigo_remessa + data_geracao + hora_geracao +
            sequencial_arquivo + versao_layout + densidade +
            brancos3 + brancos4 + brancos5
        )
        
        self.linhas.append(linha)
        return linha
    
    def gerar_header_lote(self, operacao='R'):
        """
        Gera o Header do Lote (Registro 1) - 240 posições
        operacao: R=Remessa de entrada, D=Remessa de alteração, E=Remessa de exclusão
        """
        self.sequencial_registro += 1
        config = self.configuracao
        
        # Controle
        codigo_banco = self.formatar_campo(config.codigo_banco, 3, '9')  # Pos 1-3
        lote = self.formatar_campo(self.sequencial_lote, 4, '9')  # Pos 4-7
        tipo_registro = self.formatar_campo('1', 1, '9')  # Pos 8
        
        # Tipo de Operação e Serviço
        tipo_operacao = self.formatar_campo(operacao, 1, 'X')  # Pos 9
        tipo_servico = self.formatar_campo('01', 2, '9')  # Pos 10-11 (01=Cobrança)
        forma_lancamento = self.formatar_campo('00', 2, '9')  # Pos 12-13
        versao_layout_lote = self.formatar_campo('060', 3, '9')  # Pos 14-16
        
        # Uso Exclusivo FEBRABAN
        branco1 = self.formatar_campo('', 1, 'X')  # Pos 17
        
        # Dados da Empresa
        tipo_inscricao = self.formatar_campo('2', 1, '9')  # Pos 18
        cnpj = self.formatar_campo(config.cnpj.replace('.', '').replace('/', '').replace('-', ''), 15, '9')  # Pos 19-33
        convenio = self.formatar_campo(config.convenio, 20, 'X')  # Pos 34-53
        agencia = self.formatar_campo(config.agencia, 5, '9')  # Pos 54-58
        dv_agencia = self.formatar_campo(config.agencia_dv or ' ', 1, 'X')  # Pos 59
        conta = self.formatar_campo(config.conta, 12, '9')  # Pos 60-71
        dv_conta = self.formatar_campo(config.conta_dv, 1, 'X')  # Pos 72
        dv_ag_conta = self.formatar_campo(' ', 1, 'X')  # Pos 73
        nome_empresa = self.formatar_campo(config.razao_social, 30, 'X')  # Pos 74-103
        
        # Mensagens
        mensagem1 = self.formatar_campo('', 40, 'X')  # Pos 104-143
        mensagem2 = self.formatar_campo('', 40, 'X')  # Pos 144-183
        
        # Controle
        numero_remessa = self.formatar_campo(config.sequencial_arquivo, 8, '9')  # Pos 184-191
        data_gravacao = self.formatar_campo(datetime.now().strftime('%d%m%Y'), 8, '9')  # Pos 192-199
        data_credito = self.formatar_campo('0', 8, '9')  # Pos 200-207
        
        # Uso Exclusivo FEBRABAN
        brancos = self.formatar_campo('', 33, 'X')  # Pos 208-240
        
        linha = (
            codigo_banco + lote + tipo_registro + tipo_operacao +
            tipo_servico + forma_lancamento + versao_layout_lote + branco1 +
            tipo_inscricao + cnpj + convenio + agencia + dv_agencia +
            conta + dv_conta + dv_ag_conta + nome_empresa +
            mensagem1 + mensagem2 + numero_remessa + data_gravacao +
            data_credito + brancos
        )
        
        self.linhas.append(linha)
        self.total_registros_lote = 2  # Header lote + este registro
        return linha
    
    def gerar_segmento_p(self, boleto, sequencial_registro_lote):
        """
        Gera o Segmento P (Registro de Detalhe) - 240 posições
        Contém dados do título
        """
        self.sequencial_registro += 1
        config = self.configuracao
        
        # Controle
        codigo_banco = self.formatar_campo(config.codigo_banco, 3, '9')  # Pos 1-3
        lote = self.formatar_campo(self.sequencial_lote, 4, '9')  # Pos 4-7
        tipo_registro = self.formatar_campo('3', 1, '9')  # Pos 8
        
        # Sequencial e Segmento
        sequencial = self.formatar_campo(sequencial_registro_lote, 5, '9')  # Pos 9-13
        segmento = self.formatar_campo('P', 1, 'X')  # Pos 14
        branco1 = self.formatar_campo('', 1, 'X')  # Pos 15
        
        # Código de Movimento
        codigo_movimento = self.formatar_campo('01', 2, '9')  # Pos 16-17 (01=Entrada de títulos)
        
        # Dados da Conta
        agencia = self.formatar_campo(config.agencia, 5, '9')  # Pos 18-22
        dv_agencia = self.formatar_campo(config.agencia_dv or ' ', 1, 'X')  # Pos 23
        conta = self.formatar_campo(config.conta, 12, '9')  # Pos 24-35
        dv_conta = self.formatar_campo(config.conta_dv, 1, 'X')  # Pos 36
        dv_ag_conta = self.formatar_campo(' ', 1, 'X')  # Pos 37
        
        # Identificação do Título no Banco
        nosso_numero = self.formatar_campo(boleto.nosso_numero, 20, '9')  # Pos 38-57
        
        # Características do Título
        carteira = self.formatar_campo(config.carteira, 1, '9')  # Pos 58 (1=Cobrança Simples)
        forma_cadastro = self.formatar_campo('1', 1, '9')  # Pos 59 (1=Com cadastramento)
        tipo_documento = self.formatar_campo('2', 1, 'X')  # Pos 60 (2=Escritural)
        emissao_boleto = self.formatar_campo('2', 1, '9')  # Pos 61 (2=Beneficiário emite)
        distribuicao_boleto = self.formatar_campo('2', 1, 'X')  # Pos 62 (2=Beneficiário distribui)
        
        # Identificação do Título na Empresa
        numero_documento = self.formatar_campo(boleto.numero_documento, 15, 'X')  # Pos 63-77
        data_vencimento = self.formatar_campo(boleto.data_vencimento.strftime('%d%m%Y'), 8, '9')  # Pos 78-85
        valor_nominal = self.formatar_campo(int(boleto.valor_documento * 100), 15, '9')  # Pos 86-100
        
        # Dados da Cobrança
        ag_cobradora = self.formatar_campo('0', 5, '9')  # Pos 101-105
        dv_ag_cobradora = self.formatar_campo(' ', 1, 'X')  # Pos 106
        especie_titulo = self.formatar_campo('02', 2, '9')  # Pos 107-108 (02=Duplicata Mercantil)
        aceite = self.formatar_campo('N', 1, 'X')  # Pos 109
        data_emissao = self.formatar_campo(boleto.data_emissao.strftime('%d%m%Y'), 8, '9')  # Pos 110-117
        
        # Juros de Mora
        codigo_juros = self.formatar_campo('3', 1, '9')  # Pos 118 (3=Percentual ao mês)
        data_juros = self.formatar_campo(boleto.data_vencimento.strftime('%d%m%Y'), 8, '9')  # Pos 119-126
        juros_mora = self.formatar_campo(int(config.percentual_juros_mes * 100), 15, '9')  # Pos 127-141
        
        # Desconto 1
        codigo_desconto = self.formatar_campo('0', 1, '9')  # Pos 142 (0=Sem desconto)
        data_desconto = self.formatar_campo('0', 8, '9')  # Pos 143-150
        valor_desconto = self.formatar_campo('0', 15, '9')  # Pos 151-165
        
        # Valor IOF
        valor_iof = self.formatar_campo('0', 15, '9')  # Pos 166-180
        
        # Abatimento
        valor_abatimento = self.formatar_campo(int(boleto.valor_abatimento * 100), 15, '9')  # Pos 181-195
        
        # Identificação do Título na Empresa (continuação)
        identificacao_empresa = self.formatar_campo(boleto.numero_documento, 25, 'X')  # Pos 196-220
        
        # Código para Protesto
        codigo_protesto = self.formatar_campo('3', 1, '9')  # Pos 221 (3=Não protestar)
        prazo_protesto = self.formatar_campo(config.dias_para_protesto, 2, '9')  # Pos 222-223
        
        # Código para Baixa/Devolução
        codigo_baixa = self.formatar_campo('0', 1, '9')  # Pos 224 (0=Não baixar)
        prazo_baixa = self.formatar_campo('0', 3, '9')  # Pos 225-227
        
        # Código da Moeda
        codigo_moeda = self.formatar_campo('09', 2, '9')  # Pos 228-229 (09=Real)
        
        # Uso Exclusivo FEBRABAN
        numero_contrato = self.formatar_campo('0', 10, '9')  # Pos 230-239
        uso_livre = self.formatar_campo(' ', 1, 'X')  # Pos 240
        
        linha = (
            codigo_banco + lote + tipo_registro + sequencial + segmento + branco1 +
            codigo_movimento + agencia + dv_agencia + conta + dv_conta + dv_ag_conta +
            nosso_numero + carteira + forma_cadastro + tipo_documento +
            emissao_boleto + distribuicao_boleto + numero_documento +
            data_vencimento + valor_nominal + ag_cobradora + dv_ag_cobradora +
            especie_titulo + aceite + data_emissao + codigo_juros + data_juros +
            juros_mora + codigo_desconto + data_desconto + valor_desconto +
            valor_iof + valor_abatimento + identificacao_empresa +
            codigo_protesto + prazo_protesto + codigo_baixa + prazo_baixa +
            codigo_moeda + numero_contrato + uso_livre
        )
        
        self.linhas.append(linha)
        self.total_registros_lote += 1
        return linha
    
    def gerar_segmento_q(self, boleto, sequencial_registro_lote):
        """
        Gera o Segmento Q (Registro de Detalhe) - 240 posições
        Contém dados do sacado (pagador)
        """
        self.sequencial_registro += 1
        config = self.configuracao
        cliente = boleto.cliente
        
        # Controle
        codigo_banco = self.formatar_campo(config.codigo_banco, 3, '9')  # Pos 1-3
        lote = self.formatar_campo(self.sequencial_lote, 4, '9')  # Pos 4-7
        tipo_registro = self.formatar_campo('3', 1, '9')  # Pos 8
        
        # Sequencial e Segmento
        sequencial = self.formatar_campo(sequencial_registro_lote, 5, '9')  # Pos 9-13
        segmento = self.formatar_campo('Q', 1, 'X')  # Pos 14
        branco1 = self.formatar_campo('', 1, 'X')  # Pos 15
        
        # Código de Movimento
        codigo_movimento = self.formatar_campo('01', 2, '9')  # Pos 16-17
        
        # Dados do Sacado (Pagador)
        tipo_inscricao = self.formatar_campo('2' if len(cliente.cpf_cnpj) > 14 else '1', 1, '9')  # Pos 18
        numero_inscricao = self.formatar_campo(
            cliente.cpf_cnpj.replace('.', '').replace('/', '').replace('-', ''), 15, '9'
        )  # Pos 19-33
        nome_sacado = self.formatar_campo(cliente.nome, 40, 'X')  # Pos 34-73
        endereco = self.formatar_campo(cliente.endereco or '', 40, 'X')  # Pos 74-113
        bairro = self.formatar_campo('', 15, 'X')  # Pos 114-128 (campo não existe no model Cliente)
        cep = self.formatar_campo('', 5, '9')  # Pos 129-133 (campo não existe no model Cliente)
        cep_complemento = self.formatar_campo('000', 3, '9')  # Pos 134-136
        cidade = self.formatar_campo(cliente.cidade or '', 15, 'X')  # Pos 137-151
        uf = self.formatar_campo(cliente.estado or '', 2, 'X')  # Pos 152-153
        
        # Dados do Sacador/Avalista
        tipo_inscricao_avalista = self.formatar_campo('0', 1, '9')  # Pos 154 (0=Sem avalista)
        numero_inscricao_avalista = self.formatar_campo('0', 15, '9')  # Pos 155-169
        nome_avalista = self.formatar_campo('', 40, 'X')  # Pos 170-209
        
        # Código do Banco Correspondente
        codigo_banco_corresp = self.formatar_campo('0', 3, '9')  # Pos 210-212
        nosso_numero_banco_corresp = self.formatar_campo('', 20, 'X')  # Pos 213-232
        
        # Uso Exclusivo FEBRABAN
        brancos = self.formatar_campo('', 8, 'X')  # Pos 233-240
        
        linha = (
            codigo_banco + lote + tipo_registro + sequencial + segmento + branco1 +
            codigo_movimento + tipo_inscricao + numero_inscricao + nome_sacado +
            endereco + bairro + cep + cep_complemento + cidade + uf +
            tipo_inscricao_avalista + numero_inscricao_avalista + nome_avalista +
            codigo_banco_corresp + nosso_numero_banco_corresp + brancos
        )
        
        self.linhas.append(linha)
        self.total_registros_lote += 1
        return linha
    
    def gerar_segmento_r(self, boleto, sequencial_registro_lote):
        """
        Gera o Segmento R (Registro de Detalhe - Opcional) - 240 posições
        Contém dados adicionais (multa, descontos, etc.)
        """
        self.sequencial_registro += 1
        config = self.configuracao
        
        # Controle
        codigo_banco = self.formatar_campo(config.codigo_banco, 3, '9')  # Pos 1-3
        lote = self.formatar_campo(self.sequencial_lote, 4, '9')  # Pos 4-7
        tipo_registro = self.formatar_campo('3', 1, '9')  # Pos 8
        
        # Sequencial e Segmento
        sequencial = self.formatar_campo(sequencial_registro_lote, 5, '9')  # Pos 9-13
        segmento = self.formatar_campo('R', 1, 'X')  # Pos 14
        branco1 = self.formatar_campo('', 1, 'X')  # Pos 15
        
        # Código de Movimento
        codigo_movimento = self.formatar_campo('01', 2, '9')  # Pos 16-17
        
        # Desconto 2
        codigo_desconto2 = self.formatar_campo('0', 1, '9')  # Pos 18
        data_desconto2 = self.formatar_campo('0', 8, '9')  # Pos 19-26
        valor_desconto2 = self.formatar_campo('0', 15, '9')  # Pos 27-41
        
        # Desconto 3
        codigo_desconto3 = self.formatar_campo('0', 1, '9')  # Pos 42
        data_desconto3 = self.formatar_campo('0', 8, '9')  # Pos 43-50
        valor_desconto3 = self.formatar_campo('0', 15, '9')  # Pos 51-65
        
        # Multa
        codigo_multa = self.formatar_campo('2', 1, '9')  # Pos 66 (2=Percentual)
        data_multa = self.formatar_campo(boleto.data_vencimento.strftime('%d%m%Y'), 8, '9')  # Pos 67-74
        percentual_multa = self.formatar_campo(int(config.percentual_multa * 100), 15, '9')  # Pos 75-89
        
        # Informação ao Sacado
        informacao_sacado = self.formatar_campo('', 10, 'X')  # Pos 90-99
        
        # Informação 3
        mensagem3 = self.formatar_campo('', 40, 'X')  # Pos 100-139
        
        # Informação 4
        mensagem4 = self.formatar_campo('', 40, 'X')  # Pos 140-179
        
        # Uso Exclusivo FEBRABAN
        brancos = self.formatar_campo('', 61, 'X')  # Pos 180-240
        
        linha = (
            codigo_banco + lote + tipo_registro + sequencial + segmento + branco1 +
            codigo_movimento + codigo_desconto2 + data_desconto2 + valor_desconto2 +
            codigo_desconto3 + data_desconto3 + valor_desconto3 +
            codigo_multa + data_multa + percentual_multa +
            informacao_sacado + mensagem3 + mensagem4 + brancos
        )
        
        self.linhas.append(linha)
        self.total_registros_lote += 1
        return linha
    
    def gerar_trailer_lote(self):
        """
        Gera o Trailer do Lote (Registro 5) - 240 posições
        """
        self.sequencial_registro += 1
        config = self.configuracao
        
        # Controle
        codigo_banco = self.formatar_campo(config.codigo_banco, 3, '9')  # Pos 1-3
        lote = self.formatar_campo(self.sequencial_lote, 4, '9')  # Pos 4-7
        tipo_registro = self.formatar_campo('5', 1, '9')  # Pos 8
        
        # Uso Exclusivo FEBRABAN
        brancos1 = self.formatar_campo('', 9, 'X')  # Pos 9-17
        
        # Totais do Lote
        quantidade_registros = self.formatar_campo(self.total_registros_lote + 2, 6, '9')  # Pos 18-23 (+2 = header + trailer)
        quantidade_titulos = self.formatar_campo(self.total_titulos, 6, '9')  # Pos 24-29
        valor_total = self.formatar_campo(int(self.total_valor_lote * 100), 17, '9')  # Pos 30-46
        
        # Quantidade de Títulos em Cobrança (zeros para remessa)
        qtd_simples = self.formatar_campo('0', 6, '9')  # Pos 47-52
        valor_simples = self.formatar_campo('0', 17, '9')  # Pos 53-69
        qtd_vinculada = self.formatar_campo('0', 6, '9')  # Pos 70-75
        valor_vinculada = self.formatar_campo('0', 17, '9')  # Pos 76-92
        qtd_caucionada = self.formatar_campo('0', 6, '9')  # Pos 93-98
        valor_caucionada = self.formatar_campo('0', 17, '9')  # Pos 99-115
        qtd_descontada = self.formatar_campo('0', 6, '9')  # Pos 116-121
        valor_descontada = self.formatar_campo('0', 17, '9')  # Pos 122-138
        
        # Número do Aviso
        numero_aviso = self.formatar_campo('', 8, 'X')  # Pos 139-146
        
        # Uso Exclusivo FEBRABAN
        brancos2 = self.formatar_campo('', 94, 'X')  # Pos 147-240
        
        linha = (
            codigo_banco + lote + tipo_registro + brancos1 +
            quantidade_registros + quantidade_titulos + valor_total +
            qtd_simples + valor_simples + qtd_vinculada + valor_vinculada +
            qtd_caucionada + valor_caucionada + qtd_descontada + valor_descontada +
            numero_aviso + brancos2
        )
        
        self.linhas.append(linha)
        return linha
    
    def gerar_trailer_arquivo(self):
        """
        Gera o Trailer do Arquivo (Registro 9) - 240 posições
        """
        self.sequencial_registro += 1
        config = self.configuracao
        
        # Controle
        codigo_banco = self.formatar_campo(config.codigo_banco, 3, '9')  # Pos 1-3
        lote = self.formatar_campo('9999', 4, '9')  # Pos 4-7
        tipo_registro = self.formatar_campo('9', 1, '9')  # Pos 8
        
        # Uso Exclusivo FEBRABAN
        brancos1 = self.formatar_campo('', 9, 'X')  # Pos 9-17
        
        # Totais do Arquivo
        quantidade_lotes = self.formatar_campo(self.sequencial_lote, 6, '9')  # Pos 18-23
        quantidade_registros = self.formatar_campo(self.sequencial_registro + 1, 6, '9')  # Pos 24-29 (+1 = este trailer)
        qtd_contas_concil = self.formatar_campo('0', 6, '9')  # Pos 30-35
        
        # Uso Exclusivo FEBRABAN
        brancos2 = self.formatar_campo('', 205, 'X')  # Pos 36-240
        
        linha = (
            codigo_banco + lote + tipo_registro + brancos1 +
            quantidade_lotes + quantidade_registros + qtd_contas_concil + brancos2
        )
        
        self.linhas.append(linha)
        return linha
    
    def gerar_remessa(self, boletos):
        """
        Gera o arquivo de remessa completo
        
        Args:
            boletos: Lista de objetos Boleto
        
        Returns:
            String com o conteúdo do arquivo CNAB 240
        """
        self.linhas = []
        self.sequencial_registro = 0
        self.total_titulos = len(boletos)
        self.total_valor_lote = sum(b.valor_documento for b in boletos)
        
        # Header do Arquivo
        self.gerar_header_arquivo()
        
        # Header do Lote
        self.gerar_header_lote()
        
        # Detalhes (Segmentos P, Q, R para cada boleto)
        sequencial_lote = 1
        for boleto in boletos:
            self.gerar_segmento_p(boleto, sequencial_lote)
            sequencial_lote += 1
            
            self.gerar_segmento_q(boleto, sequencial_lote)
            sequencial_lote += 1
            
            self.gerar_segmento_r(boleto, sequencial_lote)
            sequencial_lote += 1
        
        # Trailer do Lote
        self.gerar_trailer_lote()
        
        # Trailer do Arquivo
        self.gerar_trailer_arquivo()
        
        # Retorna o arquivo completo (sem linha extra no final)
        return '\r\n'.join(self.linhas)
    
    def validar_arquivo(self, conteudo):
        """
        Valida se o arquivo CNAB gerado está correto
        """
        linhas = conteudo.split('\r\n')
        
        erros = []
        
        # Verifica se todas as linhas têm 240 posições
        for i, linha in enumerate(linhas, 1):
            if linha and len(linha) != 240:  # Ignora linhas vazias
                erros.append(f"Linha {i}: Tamanho incorreto ({len(linha)} posições, esperado 240)")
        
        # Verifica header do arquivo (primeira linha não vazia)
        primeira_linha = [l for l in linhas if l][0] if linhas else ''
        if primeira_linha and primeira_linha[7:8] != '0':
            erros.append("Header do arquivo inválido")
        
        # Verifica trailer do arquivo (última linha não vazia)
        ultima_linha = [l for l in linhas if l][-1] if linhas else ''
        if ultima_linha and ultima_linha[7:8] != '9':
            erros.append("Trailer do arquivo inválido")
        
        return len(erros) == 0, erros
