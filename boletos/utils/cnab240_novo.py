"""
GERADOR E VALIDADOR CNAB 240 - CAIXA ECONÔMICA FEDERAL
Layout: CNAB 240 - SIGCB (Sistema de Gestão de Cobrança Bancária)
Versão: 103 (Header Arquivo) / 060 (Header Lote)

REGRAS CRÍTICAS:
- Cada linha tem EXATAMENTE 240 posições
- Campos numéricos (9): alinhados à direita, zeros à esquerda
- Campos alfanuméricos (X): alinhados à esquerda, espaços à direita
- Sem TAB, sem acentos, sem caracteres especiais
- Encoding: ASCII puro
"""

from datetime import datetime
from decimal import Decimal


class ValidadorCNAB240:
    """Validador rigoroso de campos CNAB 240"""
    
    @staticmethod
    def validar_linha(linha, numero_linha):
        """Valida se a linha tem exatamente 240 posições"""
        erros = []
        
        if len(linha) != 240:
            erros.append(f"Linha {numero_linha}: Tamanho incorreto ({len(linha)} chars, esperado 240)")
        
        # Verificar caracteres proibidos
        if '\t' in linha:
            erros.append(f"Linha {numero_linha}: Contém TAB (proibido)")
        
        if '\n' in linha or '\r' in linha:
            erros.append(f"Linha {numero_linha}: Contém quebra de linha (proibido)")
        
        # Verificar ASCII puro
        try:
            linha.encode('ascii')
        except UnicodeEncodeError:
            erros.append(f"Linha {numero_linha}: Contém caracteres não-ASCII (proibido)")
        
        return erros
    
    @staticmethod
    def validar_numerico(valor, tamanho):
        """Valida se valor numérico está correto"""
        if len(valor) != tamanho:
            return False
        if not valor.isdigit():
            return False
        return True
    
    @staticmethod
    def validar_data(data_str):
        """Valida formato de data DDMMAAAA"""
        if len(data_str) != 8:
            return False
        try:
            dia = int(data_str[0:2])
            mes = int(data_str[2:4])
            ano = int(data_str[4:8])
            if dia < 1 or dia > 31:
                return False
            if mes < 1 or mes > 12:
                return False
            if ano < 1900 or ano > 2100:
                return False
            return True
        except:
            return False


class CamposCNAB240:
    """Formatador de campos CNAB 240"""
    
    @staticmethod
    def formatar_numerico(valor, tamanho):
        """
        Formata campo numérico (picture 9)
        Alinhado à direita, zeros à esquerda
        """
        if valor is None:
            valor = 0
        
        # Converter para string sem formatação
        if isinstance(valor, (int, float, Decimal)):
            valor_str = str(int(valor))
        else:
            # Remove caracteres não numéricos
            valor_str = ''.join(c for c in str(valor) if c.isdigit())
        
        # Preencher com zeros à esquerda
        return valor_str.zfill(tamanho)[:tamanho]
    
    @staticmethod
    def formatar_alfanumerico(valor, tamanho):
        """
        Formata campo alfanumérico (picture X)
        Alinhado à esquerda, espaços à direita
        Remove acentos e caracteres especiais
        """
        if valor is None:
            valor = ''
        
        # Converter para string
        valor_str = str(valor)
        
        # Remover acentos e caracteres especiais
        valor_str = CamposCNAB240.remover_acentos(valor_str)
        
        # Converter para maiúsculas
        valor_str = valor_str.upper()
        
        # Manter apenas A-Z, 0-9 e espaço
        valor_str = ''.join(c for c in valor_str if c.isalnum() or c == ' ')
        
        # Preencher com espaços à direita
        return valor_str.ljust(tamanho)[:tamanho]
    
    @staticmethod
    def remover_acentos(texto):
        """Remove acentos e caracteres especiais"""
        mapa = {
            'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A',
            'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
            'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
            'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
            'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
            'Ç': 'C', 'Ñ': 'N',
            'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
            'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
            'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
            'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        
        resultado = ''
        for c in texto:
            resultado += mapa.get(c, c)
        
        return resultado
    
    @staticmethod
    def formatar_valor(valor, tamanho, decimais=2):
        """
        Formata valor monetário
        Ex: 1272.35 -> 000000000127235 (15 posições, 2 decimais)
        """
        if valor is None:
            valor = 0
        
        # Converter para centavos
        if isinstance(valor, (int, float, Decimal)):
            valor_centavos = int(valor * (10 ** decimais))
        else:
            valor_centavos = int(float(valor) * (10 ** decimais))
        
        return CamposCNAB240.formatar_numerico(valor_centavos, tamanho)
    
    @staticmethod
    def formatar_data(data, formato='DDMMAAAA'):
        """
        Formata data para DDMMAAAA
        """
        if isinstance(data, str):
            # Assumir que já está no formato correto
            return data.replace('/', '').replace('-', '').zfill(8)
        
        if hasattr(data, 'strftime'):
            return data.strftime('%d%m%Y')
        
        return '00000000'


class GeradorCNAB240Caixa:
    """
    Gerador de arquivo CNAB 240 para CAIXA ECONÔMICA FEDERAL
    Layout SIGCB - Sistema de Gestão de Cobrança Bancária
    """
    
    def __init__(self, configuracao):
        """
        Configuração deve conter:
        - codigo_banco: '104'
        - cnpj: CNPJ do beneficiário (sem formatação)
        - convenio: Código do convênio (6 ou 7 dígitos)
        - codigo_beneficiario: Código do beneficiário
        - agencia: Número da agência
        - agencia_dv: Dígito verificador da agência
        - conta: Número da conta
        - conta_dv: Dígito verificador da conta
        - razao_social: Razão social do beneficiário
        - sequencial_arquivo: Número sequencial do arquivo
        """
        self.config = configuracao
        self.linhas = []
        self.sequencial_registro = 0
        self.sequencial_lote = 1
        self.total_registros_lote = 0
        self.validador = ValidadorCNAB240()
        self.campos = CamposCNAB240()
    
    def gerar_remessa(self, boletos):
        """Gera arquivo completo de remessa"""
        self.linhas = []
        self.sequencial_registro = 0
        
        # 1. Header do Arquivo (Registro 0)
        self.gerar_header_arquivo()
        
        # 2. Header do Lote (Registro 1)
        self.gerar_header_lote()
        
        # 3. Detalhes - Segmentos P, Q (e R se necessário) para cada boleto
        sequencial_detalhe = 1
        for boleto in boletos:
            # Segmento P (obrigatório)
            self.gerar_segmento_p(boleto, sequencial_detalhe)
            sequencial_detalhe += 1
            
            # Segmento Q (obrigatório)
            self.gerar_segmento_q(boleto, sequencial_detalhe)
            sequencial_detalhe += 1
            
            # Segmento R (opcional - multa/desconto)
            if self.tem_segmento_r(boleto):
                self.gerar_segmento_r(boleto, sequencial_detalhe)
                sequencial_detalhe += 1
        
        # 4. Trailer do Lote (Registro 5)
        self.gerar_trailer_lote()
        
        # 5. Trailer do Arquivo (Registro 9)
        self.gerar_trailer_arquivo()
        
        # Validar arquivo completo
        erros = self.validar_arquivo()
        if erros:
            raise ValueError(f"Arquivo CNAB inválido:\n" + "\n".join(erros))
        
        # Retornar conteúdo
        return '\r\n'.join(self.linhas)
    
    def gerar_header_arquivo(self):
        """
        REGISTRO 0 - HEADER DO ARQUIVO
        Posição 001-240
        """
        linha = ''
        
        # Posição 001-003: Código do Banco (9/3)
        linha += self.campos.formatar_numerico(self.config.codigo_banco, 3)
        
        # Posição 004-007: Lote de Serviço (9/4) - '0000' para header
        linha += self.campos.formatar_numerico(0, 4)
        
        # Posição 008-008: Tipo de Registro (9/1) - '0' para header arquivo
        linha += '0'
        
        # Posição 009-017: Uso Exclusivo FEBRABAN (X/9)
        linha += self.campos.formatar_alfanumerico('', 9)
        
        # Posição 018-018: Tipo de Inscrição da Empresa (9/1) - '2' para CNPJ
        linha += '2'
        
        # Posição 019-032: Número de Inscrição da Empresa (9/14)
        linha += self.campos.formatar_numerico(self.config.cnpj, 14)
        
        # Posição 033-052: Código do Convênio no Banco (X/20)
        linha += self.campos.formatar_alfanumerico(self.config.convenio, 20)
        
        # Posição 053-057: Agência Mantenedora da Conta (9/5)
        linha += self.campos.formatar_numerico(self.config.agencia, 5)
        
        # Posição 058-058: Dígito Verificador da Agência (X/1)
        linha += self.campos.formatar_alfanumerico(self.config.agencia_dv or '', 1)
        
        # Posição 059-070: Número da Conta Corrente (9/12)
        linha += self.campos.formatar_numerico(self.config.conta, 12)
        
        # Posição 071-071: Dígito Verificador da Conta (X/1)
        linha += self.campos.formatar_alfanumerico(self.config.conta_dv, 1)
        
        # Posição 072-072: Dígito Verificador da Ag/Conta (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 073-102: Nome da Empresa (X/30)
        linha += self.campos.formatar_alfanumerico(self.config.razao_social, 30)
        
        # Posição 103-132: Nome do Banco (X/30)
        linha += self.campos.formatar_alfanumerico('CAIXA ECONOMICA FEDERAL', 30)
        
        # Posição 133-142: Uso Exclusivo FEBRABAN (X/10)
        linha += self.campos.formatar_alfanumerico('', 10)
        
        # Posição 143-143: Código de Remessa/Retorno (9/1) - '1' para remessa
        linha += '1'
        
        # Posição 144-151: Data de Geração do Arquivo (9/8) - DDMMAAAA
        linha += datetime.now().strftime('%d%m%Y')
        
        # Posição 152-157: Hora de Geração do Arquivo (9/6) - HHMMSS
        linha += datetime.now().strftime('%H%M%S')
        
        # Posição 158-163: Número Sequencial do Arquivo (9/6)
        linha += self.campos.formatar_numerico(self.config.sequencial_arquivo, 6)
        
        # Posição 164-166: Versão do Layout do Arquivo (9/3) - '103' para CAIXA
        linha += '103'
        
        # Posição 167-171: Densidade de Gravação do Arquivo (9/5)
        linha += self.campos.formatar_numerico(0, 5)
        
        # Posição 172-191: Para Uso Reservado do Banco (X/20)
        linha += self.campos.formatar_alfanumerico('', 20)
        
        # Posição 192-211: Para Uso Reservado da Empresa (X/20)
        linha += self.campos.formatar_alfanumerico('', 20)
        
        # Posição 212-240: Uso Exclusivo FEBRABAN (X/29)
        linha += self.campos.formatar_alfanumerico('', 29)
        
        self.linhas.append(linha)
        self.sequencial_registro += 1
    
    def tem_segmento_r(self, boleto):
        """Verifica se boleto necessita Segmento R"""
        # Segmento R é necessário se houver multa, desconto ou abatimento
        return (
            hasattr(boleto, 'valor_multa') and boleto.valor_multa > 0 or
            hasattr(boleto, 'valor_desconto') and boleto.valor_desconto > 0 or
            hasattr(boleto, 'valor_abatimento') and boleto.valor_abatimento > 0
        )
    
    def validar_arquivo(self):
        """Valida todo o arquivo"""
        erros = []
        
        for i, linha in enumerate(self.linhas, 1):
            erros_linha = self.validador.validar_linha(linha, i)
            erros.extend(erros_linha)
        
        # Verificar estrutura
        if len(self.linhas) < 4:
            erros.append("Arquivo deve ter no mínimo 4 registros (Header Arquivo, Header Lote, Trailer Lote, Trailer Arquivo)")
        
        # Verificar header arquivo
        if self.linhas[0][7:8] != '0':
            erros.append("Primeiro registro deve ser Header do Arquivo (tipo '0')")
        
        # Verificar trailer arquivo
        if self.linhas[-1][7:8] != '9':
            erros.append("Último registro deve ser Trailer do Arquivo (tipo '9')")
        
        return erros


    def gerar_header_lote(self):
        """
        REGISTRO 1 - HEADER DO LOTE
        Posição 001-240
        """
        linha = ''
        
        # Posição 001-003: Código do Banco (9/3)
        linha += self.campos.formatar_numerico(self.config.codigo_banco, 3)
        
        # Posição 004-007: Lote de Serviço (9/4)
        linha += self.campos.formatar_numerico(self.sequencial_lote, 4)
        
        # Posição 008-008: Tipo de Registro (9/1) - '1' para header lote
        linha += '1'
        
        # Posição 009-009: Tipo de Operação (X/1) - 'R' para remessa
        linha += 'R'
        
        # Posição 010-011: Tipo de Serviço (9/2) - '01' para cobrança
        linha += '01'
        
        # Posição 012-013: Forma de Lançamento (9/2) - '00'
        linha += '00'
        
        # Posição 014-016: Versão do Layout do Lote (9/3) - '060' para CAIXA cobrança
        linha += '060'
        
        # Posição 017-017: Uso Exclusivo FEBRABAN (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 018-018: Tipo de Inscrição da Empresa (9/1) - '2' para CNPJ
        linha += '2'
        
        # Posição 019-033: Número de Inscrição da Empresa (9/15)
        linha += self.campos.formatar_numerico(self.config.cnpj, 15)
        
        # Posição 034-053: Código do Convênio no Banco (X/20)
        linha += self.campos.formatar_alfanumerico(self.config.convenio, 20)
        
        # Posição 054-058: Agência Mantenedora da Conta (9/5)
        linha += self.campos.formatar_numerico(self.config.agencia, 5)
        
        # Posição 059-059: Dígito Verificador da Agência (X/1)
        linha += self.campos.formatar_alfanumerico(self.config.agencia_dv or '', 1)
        
        # Posição 060-071: Número da Conta Corrente (9/12)
        linha += self.campos.formatar_numerico(self.config.conta, 12)
        
        # Posição 072-072: Dígito Verificador da Conta (X/1)
        linha += self.campos.formatar_alfanumerico(self.config.conta_dv, 1)
        
        # Posição 073-073: Dígito Verificador da Ag/Conta (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 074-103: Nome da Empresa (X/30)
        linha += self.campos.formatar_alfanumerico(self.config.razao_social, 30)
        
        # Posição 104-143: Mensagem 1 (X/40)
        linha += self.campos.formatar_alfanumerico('', 40)
        
        # Posição 144-183: Mensagem 2 (X/40)
        linha += self.campos.formatar_alfanumerico('', 40)
        
        # Posição 184-191: Número Remessa/Retorno (9/8)
        linha += self.campos.formatar_numerico(self.config.sequencial_arquivo, 8)
        
        # Posição 192-199: Data de Gravação (9/8) - DDMMAAAA
        linha += datetime.now().strftime('%d%m%Y')
        
        # Posição 200-207: Data do Crédito (9/8) - zeros
        linha += self.campos.formatar_numerico(0, 8)
        
        # Posição 208-240: Uso Exclusivo FEBRABAN (X/33)
        linha += self.campos.formatar_alfanumerico('', 33)
        
        self.linhas.append(linha)
        self.sequencial_registro += 1
        self.total_registros_lote = 0
    
    def gerar_segmento_p(self, boleto, sequencial):
        """
        SEGMENTO P - Informações do Título
        Registro tipo 3
        """
        linha = ''
        
        # Posição 001-003: Código do Banco (9/3)
        linha += self.campos.formatar_numerico(self.config.codigo_banco, 3)
        
        # Posição 004-007: Lote de Serviço (9/4)
        linha += self.campos.formatar_numerico(self.sequencial_lote, 4)
        
        # Posição 008-008: Tipo de Registro (9/1) - '3' para detalhe
        linha += '3'
        
        # Posição 009-013: Nº Sequencial do Registro no Lote (9/5)
        linha += self.campos.formatar_numerico(sequencial, 5)
        
        # Posição 014-014: Código do Segmento (X/1) - 'P'
        linha += 'P'
        
        # Posição 015-015: Uso Exclusivo FEBRABAN (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 016-017: Código de Movimento (9/2) - '01' entrada de título
        linha += '01'
        
        # Posição 018-022: Agência Mantenedora da Conta (9/5)
        linha += self.campos.formatar_numerico(self.config.agencia, 5)
        
        # Posição 023-023: Dígito Verificador da Agência (X/1)
        linha += self.campos.formatar_alfanumerico(self.config.agencia_dv or '', 1)
        
        # Posição 024-035: Número da Conta Corrente (9/12)
        linha += self.campos.formatar_numerico(self.config.conta, 12)
        
        # Posição 036-036: Dígito Verificador da Conta (X/1)
        linha += self.campos.formatar_alfanumerico(self.config.conta_dv, 1)
        
        # Posição 037-037: Dígito Verificador da Ag/Conta (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 038-057: Nosso Número - Identificação do Título no Banco (X/20)
        # Formato CAIXA: modalidade(2) + nosso_numero(15) + dv(1)
        nosso_numero_completo = self.campos.formatar_numerico(boleto.nosso_numero, 17)
        linha += self.campos.formatar_alfanumerico(nosso_numero_completo, 20)
        
        # Posição 058-058: Código da Carteira (9/1) - '1' cobrança simples
        linha += '1'
        
        # Posição 059-059: Forma de Cadastr. do Título no Banco (9/1) - '1' com registro
        linha += '1'
        
        # Posição 060-060: Tipo de Documento (X/1) - '2' escritural
        linha += '2'
        
        # Posição 061-061: Identificação da Emissão do Boleto (9/1) - '1' banco emite
        linha += '1'
        
        # Posição 062-062: Identificação da Distribuição (X/1) - '0' banco distribui
        linha += '0'
        
        # Posição 063-077: Número do Documento de Cobrança (X/15)
        linha += self.campos.formatar_alfanumerico(boleto.numero_documento, 15)
        
        # Posição 078-085: Data de Vencimento do Título (9/8) - DDMMAAAA
        linha += self.campos.formatar_data(boleto.data_vencimento)
        
        # Posição 086-100: Valor Nominal do Título (9/15) - 2 decimais
        linha += self.campos.formatar_valor(boleto.valor_documento, 15, 2)
        
        # Posição 101-105: Agência Encarregada da Cobrança (9/5)
        linha += self.campos.formatar_numerico(0, 5)
        
        # Posição 106-106: Dígito Verificador da Agência (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 107-108: Espécie do Título (9/2) - '02' Duplicata Mercantil
        linha += '02'
        
        # Posição 109-109: Identific. de Título Aceito/Não Aceito (X/1) - 'N'
        linha += 'N'
        
        # Posição 110-117: Data da Emissão do Título (9/8) - DDMMAAAA
        linha += self.campos.formatar_data(boleto.data_emissao)
        
        # Posição 118-118: Código do Juros de Mora (9/1) - '1' valor por dia
        codigo_juros = '1' if hasattr(boleto, 'valor_juros_dia') and boleto.valor_juros_dia > 0 else '3'
        linha += codigo_juros
        
        # Posição 119-126: Data do Juros de Mora (9/8) - DDMMAAAA
        data_juros = self.campos.formatar_data(boleto.data_vencimento) if codigo_juros == '1' else '00000000'
        linha += data_juros
        
        # Posição 127-141: Juros de Mora por Dia/Taxa (9/15) - 2 decimais
        valor_juros = boleto.valor_juros_dia if hasattr(boleto, 'valor_juros_dia') else 0
        linha += self.campos.formatar_valor(valor_juros, 15, 2)
        
        # Posição 142-142: Código do Desconto 1 (9/1) - '0' sem desconto
        linha += '0'
        
        # Posição 143-150: Data do Desconto 1 (9/8)
        linha += self.campos.formatar_numerico(0, 8)
        
        # Posição 151-165: Valor/Percentual a ser Concedido (9/15)
        linha += self.campos.formatar_numerico(0, 15)
        
        # Posição 166-180: Valor do IOF a ser Recolhido (9/15)
        linha += self.campos.formatar_numerico(0, 15)
        
        # Posição 181-195: Valor do Abatimento (9/15)
        valor_abatimento = boleto.valor_abatimento if hasattr(boleto, 'valor_abatimento') else 0
        linha += self.campos.formatar_valor(valor_abatimento, 15, 2)
        
        # Posição 196-220: Identificação do Título na Empresa (X/25)
        linha += self.campos.formatar_alfanumerico(boleto.numero_documento, 25)
        
        # Posição 221-221: Código para Protesto (9/1) - '3' não protestar
        linha += '3'
        
        # Posição 222-223: Número de Dias para Protesto (9/2)
        linha += self.campos.formatar_numerico(0, 2)
        
        # Posição 224-224: Código para Baixa/Devolução (9/1) - '0' não baixar
        linha += '0'
        
        # Posição 225-227: Número de Dias para Baixa/Devolução (X/3)
        linha += self.campos.formatar_alfanumerico('', 3)
        
        # Posição 228-229: Código da Moeda (9/2) - '09' Real
        linha += '09'
        
        # Posição 230-239: Nº do Contrato da Operação de Crédito (9/10)
        linha += self.campos.formatar_numerico(0, 10)
        
        # Posição 240-240: Uso Exclusivo FEBRABAN (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        self.linhas.append(linha)
        self.sequencial_registro += 1
        self.total_registros_lote += 1
    
    def gerar_segmento_q(self, boleto, sequencial):
        """
        SEGMENTO Q - Informações do Sacado (Pagador)
        Registro tipo 3
        """
        linha = ''
        cliente = boleto.cliente
        
        # Posição 001-003: Código do Banco (9/3)
        linha += self.campos.formatar_numerico(self.config.codigo_banco, 3)
        
        # Posição 004-007: Lote de Serviço (9/4)
        linha += self.campos.formatar_numerico(self.sequencial_lote, 4)
        
        # Posição 008-008: Tipo de Registro (9/1) - '3' para detalhe
        linha += '3'
        
        # Posição 009-013: Nº Sequencial do Registro no Lote (9/5)
        linha += self.campos.formatar_numerico(sequencial, 5)
        
        # Posição 014-014: Código do Segmento (X/1) - 'Q'
        linha += 'Q'
        
        # Posição 015-015: Uso Exclusivo FEBRABAN (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 016-017: Código de Movimento (9/2) - '01' entrada de título
        linha += '01'
        
        # Posição 018-018: Tipo de Inscrição (9/1) - '1' CPF, '2' CNPJ
        tipo_inscricao = '2' if len(cliente.cpf_cnpj.replace('.', '').replace('/', '').replace('-', '')) > 11 else '1'
        linha += tipo_inscricao
        
        # Posição 019-033: Número de Inscrição (9/15)
        linha += self.campos.formatar_numerico(cliente.cpf_cnpj, 15)
        
        # Posição 034-073: Nome (X/40)
        linha += self.campos.formatar_alfanumerico(cliente.nome, 40)
        
        # Posição 074-113: Endereço (X/40)
        linha += self.campos.formatar_alfanumerico(cliente.endereco or '', 40)
        
        # Posição 114-128: Bairro (X/15)
        linha += self.campos.formatar_alfanumerico('', 15)
        
        # Posição 129-133: CEP (9/5) - sem dígito verificador
        linha += self.campos.formatar_numerico(0, 5)
        
        # Posição 134-136: Sufixo do CEP (9/3)
        linha += self.campos.formatar_numerico(0, 3)
        
        # Posição 137-151: Cidade (X/15)
        linha += self.campos.formatar_alfanumerico(cliente.cidade or '', 15)
        
        # Posição 152-153: Unidade da Federação (X/2)
        linha += self.campos.formatar_alfanumerico(cliente.estado or '', 2)
        
        # Posição 154-154: Tipo de Inscrição Sacador/Avalista (9/1) - '0' sem avalista
        linha += '0'
        
        # Posição 155-169: Número de Inscrição Sacador/Avalista (9/15)
        linha += self.campos.formatar_numerico(0, 15)
        
        # Posição 170-209: Nome do Sacador/Avalista (X/40)
        linha += self.campos.formatar_alfanumerico('', 40)
        
        # Posição 210-212: Código Banco Correspondente (9/3)
        linha += self.campos.formatar_numerico(0, 3)
        
        # Posição 213-232: Nosso Nº no Banco Correspondente (X/20)
        linha += self.campos.formatar_alfanumerico('', 20)
        
        # Posição 233-240: Uso Exclusivo FEBRABAN (X/8)
        linha += self.campos.formatar_alfanumerico('', 8)
        
        self.linhas.append(linha)
        self.sequencial_registro += 1
        self.total_registros_lote += 1
    
    def gerar_segmento_r(self, boleto, sequencial):
        """
        SEGMENTO R - Informações Adicionais (Multa, Desconto, etc)
        Registro tipo 3 - OPCIONAL
        """
        linha = ''
        
        # Posição 001-003: Código do Banco (9/3)
        linha += self.campos.formatar_numerico(self.config.codigo_banco, 3)
        
        # Posição 004-007: Lote de Serviço (9/4)
        linha += self.campos.formatar_numerico(self.sequencial_lote, 4)
        
        # Posição 008-008: Tipo de Registro (9/1) - '3' para detalhe
        linha += '3'
        
        # Posição 009-013: Nº Sequencial do Registro no Lote (9/5)
        linha += self.campos.formatar_numerico(sequencial, 5)
        
        # Posição 014-014: Código do Segmento (X/1) - 'R'
        linha += 'R'
        
        # Posição 015-015: Uso Exclusivo FEBRABAN (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 016-017: Código de Movimento (9/2) - '01' entrada de título
        linha += '01'
        
        # Posição 018-018: Código do Desconto 2 (9/1) - '0' sem desconto
        linha += '0'
        
        # Posição 019-026: Data do Desconto 2 (9/8)
        linha += self.campos.formatar_numerico(0, 8)
        
        # Posição 027-041: Valor/Percentual Desconto 2 (9/15)
        linha += self.campos.formatar_numerico(0, 15)
        
        # Posição 042-042: Código do Desconto 3 (9/1)
        linha += '0'
        
        # Posição 043-050: Data do Desconto 3 (9/8)
        linha += self.campos.formatar_numerico(0, 8)
        
        # Posição 051-065: Valor/Percentual Desconto 3 (9/15)
        linha += self.campos.formatar_numerico(0, 15)
        
        # Posição 066-066: Código da Multa (9/1) - '1' valor fixo, '2' percentual
        codigo_multa = '0'
        if hasattr(boleto, 'valor_multa') and boleto.valor_multa > 0:
            codigo_multa = '1'  # valor fixo
        linha += codigo_multa
        
        # Posição 067-074: Data da Multa (9/8) - DDMMAAAA
        if codigo_multa != '0':
            linha += self.campos.formatar_data(boleto.data_vencimento)
        else:
            linha += self.campos.formatar_numerico(0, 8)
        
        # Posição 075-089: Valor/Percentual da Multa (9/15)
        valor_multa = boleto.valor_multa if hasattr(boleto, 'valor_multa') else 0
        linha += self.campos.formatar_valor(valor_multa, 15, 2)
        
        # Posição 090-099: Informação ao Pagador (X/10)
        linha += self.campos.formatar_alfanumerico('', 10)
        
        # Posição 100-139: Informação 3 (X/40)
        linha += self.campos.formatar_alfanumerico('', 40)
        
        # Posição 140-179: Informação 4 (X/40)
        linha += self.campos.formatar_alfanumerico('', 40)
        
        # Posição 180-199: Uso Exclusivo FEBRABAN (X/20)
        linha += self.campos.formatar_alfanumerico('', 20)
        
        # Posição 200-207: Cód. Ocor. do Pagador (9/8)
        linha += self.campos.formatar_numerico(0, 8)
        
        # Posição 208-210: Cód. do Banco na Conta Débito (9/3)
        linha += self.campos.formatar_numerico(0, 3)
        
        # Posição 211-215: Cód. da Agência do Débito (9/5)
        linha += self.campos.formatar_numerico(0, 5)
        
        # Posição 216-216: Dígito Verificador da Agência (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 217-228: Conta Corrente para Débito (9/12)
        linha += self.campos.formatar_numerico(0, 12)
        
        # Posição 229-229: Dígito Verificador da Conta (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 230-230: Dígito Verificador Ag/Conta (X/1)
        linha += self.campos.formatar_alfanumerico('', 1)
        
        # Posição 231-231: Aviso para Débito Automático (9/1) - '0' não debitar
        linha += '0'
        
        # Posição 232-240: Uso Exclusivo FEBRABAN (X/9)
        linha += self.campos.formatar_alfanumerico('', 9)
        
        self.linhas.append(linha)
        self.sequencial_registro += 1
        self.total_registros_lote += 1
    
    def gerar_trailer_lote(self):
        """
        REGISTRO 5 - TRAILER DO LOTE
        """
        linha = ''
        
        # Posição 001-003: Código do Banco (9/3)
        linha += self.campos.formatar_numerico(self.config.codigo_banco, 3)
        
        # Posição 004-007: Lote de Serviço (9/4)
        linha += self.campos.formatar_numerico(self.sequencial_lote, 4)
        
        # Posição 008-008: Tipo de Registro (9/1) - '5' para trailer lote
        linha += '5'
        
        # Posição 009-017: Uso Exclusivo FEBRABAN (X/9)
        linha += self.campos.formatar_alfanumerico('', 9)
        
        # Posição 018-023: Quantidade de Registros no Lote (9/6)
        # Header lote + detalhes + trailer lote
        qtd_registros = self.total_registros_lote + 2
        linha += self.campos.formatar_numerico(qtd_registros, 6)
        
        # Posição 024-029: Quantidade de Títulos em Cobrança (9/6)
        qtd_titulos = self.total_registros_lote // 2  # P e Q por título (ou P, Q, R)
        linha += self.campos.formatar_numerico(qtd_titulos, 6)
        
        # Posição 030-046: Valor Total dos Títulos em Carteiras (9/17) - 2 decimais
        linha += self.campos.formatar_numerico(0, 17)
        
        # Posição 047-052: Qtde de Títulos em Cobrança Simples (9/6)
        linha += self.campos.formatar_numerico(qtd_titulos, 6)
        
        # Posição 053-069: Valor Total Títulos Carteira Simples (9/17)
        linha += self.campos.formatar_numerico(0, 17)
        
        # Posição 070-075: Qtde Títulos Cobrança Vinculada (9/6)
        linha += self.campos.formatar_numerico(0, 6)
        
        # Posição 076-092: Valor Total Títulos Carteira Vinculada (9/17)
        linha += self.campos.formatar_numerico(0, 17)
        
        # Posição 093-098: Qtde Títulos Cobrança Caucionada (9/6)
        linha += self.campos.formatar_numerico(0, 6)
        
        # Posição 099-115: Valor Total Títulos Carteira Caucionada (9/17)
        linha += self.campos.formatar_numerico(0, 17)
        
        # Posição 116-123: Qtde Títulos Cobrança Descontada (9/8)
        linha += self.campos.formatar_numerico(0, 8)
        
        # Posição 124-140: Valor Total Títulos Carteira Descontada (9/17)
        linha += self.campos.formatar_numerico(0, 17)
        
        # Posição 141-148: Número do Aviso de Lançamento (X/8)
        linha += self.campos.formatar_alfanumerico('', 8)
        
        # Posição 149-240: Uso Exclusivo FEBRABAN (X/92)
        linha += self.campos.formatar_alfanumerico('', 92)
        
        self.linhas.append(linha)
        self.sequencial_registro += 1
    
    def gerar_trailer_arquivo(self):
        """
        REGISTRO 9 - TRAILER DO ARQUIVO
        """
        linha = ''
        
        # Posição 001-003: Código do Banco (9/3)
        linha += self.campos.formatar_numerico(self.config.codigo_banco, 3)
        
        # Posição 004-007: Lote de Serviço (9/4) - '9999' para trailer arquivo
        linha += '9999'
        
        # Posição 008-008: Tipo de Registro (9/1) - '9' para trailer arquivo
        linha += '9'
        
        # Posição 009-017: Uso Exclusivo FEBRABAN (X/9)
        linha += self.campos.formatar_alfanumerico('', 9)
        
        # Posição 018-023: Quantidade de Lotes do Arquivo (9/6)
        linha += self.campos.formatar_numerico(1, 6)
        
        # Posição 024-029: Quantidade de Registros do Arquivo (9/6)
        # Header arquivo + header lote + detalhes + trailer lote + trailer arquivo
        qtd_registros_arquivo = len(self.linhas) + 1  # +1 para este trailer
        linha += self.campos.formatar_numerico(qtd_registros_arquivo, 6)
        
        # Posição 030-035: Qtde de Contas Conciliação (9/6)
        linha += self.campos.formatar_numerico(0, 6)
        
        # Posição 036-240: Uso Exclusivo FEBRABAN (X/205)
        linha += self.campos.formatar_alfanumerico('', 205)
        
        self.linhas.append(linha)
