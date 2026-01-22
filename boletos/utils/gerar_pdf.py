"""
Geração de PDF de Boleto Bancário - Padrão Caixa Econômica Federal
Usa ReportLab para gerar o layout visual do boleto conforme padrão oficial da Caixa
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime
from decimal import Decimal
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image
import os
from django.conf import settings


class GeradorBoletoPDF:
    """
    Classe para gerar PDF de boleto bancário no padrão Caixa Econômica Federal
    Layout conforme especificação FEBRABAN com branding Caixa
    """
    
    # Cores oficiais da Caixa
    COR_CAIXA_LARANJA = colors.HexColor('#FF6600')
    COR_CAIXA_AZUL = colors.HexColor('#003E7E')
    
    def __init__(self, boleto):
        self.boleto = boleto
        self.config = boleto.configuracao
        self.cliente = boleto.cliente
        self.width, self.height = A4
        
    def formatar_cpf_cnpj(self, documento):
        """Formata CPF/CNPJ"""
        doc = documento.replace('.', '').replace('/', '').replace('-', '').replace(' ', '')
        if len(doc) == 11:  # CPF
            return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
        else:  # CNPJ
            return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
    
    def formatar_valor(self, valor):
        """Formata valor monetário"""
        if valor is None or valor == '':
            return ""
        if isinstance(valor, str):
            valor = Decimal(valor)
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def formatar_data(self, data):
        """Formata data para DD/MM/YYYY"""
        if data is None:
            return ""
        if isinstance(data, str):
            data = datetime.strptime(data, '%Y-%m-%d').date()
        return data.strftime('%d/%m/%Y')
    
    def desenhar_logo_caixa(self, c, x, y, largura=25*mm, altura=7*mm):
        """Desenha o logo oficial da Caixa"""
        # Caminho para o logo
        logo_path = os.path.join(settings.BASE_DIR, 'boletos', 'static', 'boletos', 'img', 'logo_caixa.png')
        
        try:
            if os.path.exists(logo_path):
                # Abre a imagem com PIL e usa ImageReader
                from PIL import Image as PILImage
                pil_img = PILImage.open(logo_path)
                img_reader = ImageReader(pil_img)
                c.drawImage(img_reader, x, y, width=largura, height=altura, preserveAspectRatio=True)
                # Reseta cor
                c.setFillColor(colors.black)
                return
        except Exception as e:
            # Em caso de erro, usa fallback
            print(f"Erro ao carregar logo da Caixa: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback: retângulo laranja com texto branco
        c.setFillColor(self.COR_CAIXA_LARANJA)
        c.rect(x, y, largura, altura, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(x + largura/2, y + 1.5*mm, "CAIXA")
        
        # Reseta cor
        c.setFillColor(colors.black)
    
    def desenhar_campo(self, c, x, y, width, height, titulo, valor, font_size=9, bold_valor=False):
        """Desenha um campo padrão com título e valor"""
        # Borda
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.5)
        c.rect(x, y, width, height)
        
        # Título (pequeno, em cima)
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 6)
        c.drawString(x + 1*mm, y + height - 3*mm, titulo)
        
        # Valor (maior, embaixo)
        if bold_valor:
            c.setFont("Helvetica-Bold", font_size)
        else:
            c.setFont("Helvetica", font_size)
        
        # Quebra texto se for muito longo
        valor_str = str(valor) if valor else ""
        if len(valor_str) > 50:
            valor_str = valor_str[:50] + "..."
        
        c.drawString(x + 1*mm, y + height - 3*mm - 3.5*mm, valor_str)
    
    def gerar_codigo_barras_imagem(self):
        """Gera a imagem do código de barras no formato Code128"""
        try:
            codigo = self.boleto.codigo_barras
            
            # Gera o código de barras usando Code128
            buffer = BytesIO()
            Code128 = barcode.get_barcode_class('code128')
            code = Code128(codigo, writer=ImageWriter())
            
            # Configurações da imagem
            options = {
                'module_width': 0.4,
                'module_height': 12,
                'quiet_zone': 2,
                'font_size': 0,  # Não mostrar texto abaixo
                'text_distance': 1,
                'write_text': False
            }
            
            code.write(buffer, options=options)
            buffer.seek(0)
            
            return buffer
        except Exception as e:
            print(f"Erro ao gerar código de barras: {e}")
            return None
    
    def gerar_recibo_sacado(self, c, y_start):
        """
        Gera a parte superior do boleto (Recibo do Sacado) - versão compacta
        """
        y = y_start
        
        # Linha do topo com logo e dados básicos
        logo_x = 15*mm
        self.desenhar_logo_caixa(c, logo_x, y - 7*mm, largura=25*mm, altura=7*mm)
        
        # Código do banco
        c.setFont("Helvetica-Bold", 13)
        c.drawString(logo_x + 27*mm, y - 5.5*mm, "104-0")
        
        # Linha digitável
        c.setFont("Helvetica-Bold", 11)
        linha_formatada = self.boleto.linha_digitavel
        c.drawString(logo_x + 45*mm, y - 5.5*mm, linha_formatada)
        
        y -= 10*mm
        
        # Linha separadora grossa
        c.setLineWidth(2)
        c.line(15*mm, y, self.width - 15*mm, y)
        c.setLineWidth(0.5)
        
        y -= 7*mm
        
        # Campos principais em linha
        col_x = 15*mm
        
        # Campo: Beneficiário
        c.setFont("Helvetica", 7)
        c.drawString(col_x, y, "Beneficiário:")
        c.setFont("Helvetica-Bold", 9)
        beneficiario_text = self.config.razao_social[:40]
        c.drawString(col_x + 18*mm, y, beneficiario_text)
        
        # Campo: Agência/Código
        c.setFont("Helvetica", 7)
        c.drawString(col_x + 90*mm, y, "Agência/Código:")
        c.setFont("Helvetica-Bold", 9)
        agencia_cod = f"{self.config.agencia}/{self.config.codigo_beneficiario}"
        c.drawString(col_x + 112*mm, y, agencia_cod)
        
        # Campo: Vencimento
        c.setFont("Helvetica", 7)
        c.drawString(col_x + 145*mm, y, "Vencimento:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(col_x + 162*mm, y, self.formatar_data(self.boleto.data_vencimento))
        
        y -= 6*mm
        
        # Segunda linha
        c.setFont("Helvetica", 7)
        c.drawString(col_x, y, "Pagador:")
        c.setFont("Helvetica-Bold", 9)
        pagador_text = self.cliente.nome[:50]
        c.drawString(col_x + 15*mm, y, pagador_text)
        
        # Valor do documento
        c.setFont("Helvetica", 7)
        c.drawString(col_x + 145*mm, y, "Valor Documento:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(col_x + 168*mm, y, self.formatar_valor(self.boleto.valor_documento))
        
        y -= 6*mm
        
        # Terceira linha - Documento e Nosso Número
        c.setFont("Helvetica", 7)
        c.drawString(col_x, y, f"Nº Documento: ")
        c.setFont("Helvetica", 8)
        c.drawString(col_x + 20*mm, y, str(self.boleto.numero_documento))
        
        c.setFont("Helvetica", 7)
        c.drawString(col_x + 70*mm, y, f"Nosso Número: ")
        c.setFont("Helvetica", 8)
        c.drawString(col_x + 90*mm, y, str(self.boleto.nosso_numero))
        
        y -= 8*mm
        
        # Linha tracejada de corte
        c.setDash(2, 2)
        c.setStrokeColor(colors.grey)
        c.line(10*mm, y, self.width - 10*mm, y)
        c.setDash()
        c.setStrokeColor(colors.black)
        
        # Texto de corte
        c.setFont("Helvetica", 7)
        c.drawString(self.width/2 - 10*mm, y - 2*mm, "Corte na linha pontilhada")
        
        return y - 6*mm
    
    def gerar_ficha_compensacao(self, c, y_start):
        """
        Gera a ficha de compensação (parte principal do boleto) - Padrão Caixa
        """
        y = y_start
        margin_x = 15*mm
        
        # === CABEÇALHO COM LOGO E LINHA DIGITÁVEL ===
        logo_x = margin_x
        self.desenhar_logo_caixa(c, logo_x, y - 7*mm, largura=25*mm, altura=7*mm)
        
        # Código do banco com barra vertical
        c.setFont("Helvetica-Bold", 14)
        c.drawString(logo_x + 27*mm, y - 5.5*mm, "104-0")
        
        # Barra vertical separadora
        c.setLineWidth(2)
        c.line(logo_x + 42*mm, y - 7.5*mm, logo_x + 42*mm, y - 0.5*mm)
        c.setLineWidth(0.5)
        
        # Linha digitável (grande e destacada)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(logo_x + 45*mm, y - 5.5*mm, self.boleto.linha_digitavel)
        
        y -= 10*mm
        
        # Linha separadora grossa
        c.setLineWidth(2.5)
        c.line(margin_x, y, self.width - margin_x, y)
        c.setLineWidth(0.5)
        
        y -= 2*mm
        
        # === PRIMEIRA LINHA DE CAMPOS ===
        altura_campo = 10*mm
        y_campo = y - altura_campo
        
        # Local de Pagamento (75% da largura) | Vencimento (25%)
        largura_esquerda = 125*mm
        largura_direita = 55*mm
        
        self.desenhar_campo(c, margin_x, y_campo, largura_esquerda, altura_campo,
                          "Local de Pagamento", 
                          self.config.local_pagamento or "Pagável em qualquer banco até o vencimento", 8)
        
        self.desenhar_campo(c, margin_x + largura_esquerda, y_campo, largura_direita, altura_campo,
                          "Vencimento", 
                          self.formatar_data(self.boleto.data_vencimento), 10, bold_valor=True)
        
        # === SEGUNDA LINHA ===
        y_campo -= altura_campo
        
        # Beneficiário | Agência/Código
        beneficiario_texto = f"{self.config.razao_social}"
        cnpj_texto = f"CNPJ: {self.formatar_cpf_cnpj(self.config.cnpj)}"
        
        self.desenhar_campo(c, margin_x, y_campo, largura_esquerda, altura_campo,
                          "Beneficiário", 
                          f"{beneficiario_texto} - {cnpj_texto}", 7)
        
        agencia_codigo = f"{self.config.agencia}-{self.config.agencia_dv or ''} / {self.config.codigo_beneficiario}"
        self.desenhar_campo(c, margin_x + largura_esquerda, y_campo, largura_direita, altura_campo,
                          "Agência/Código Beneficiário", 
                          agencia_codigo, 9, bold_valor=True)
        
        # === TERCEIRA LINHA (4 campos) ===
        y_campo -= altura_campo
        
        l1 = 30*mm  # Data documento
        l2 = 35*mm  # Nº documento
        l3 = 30*mm  # Espécie doc
        l4 = 15*mm  # Aceite
        l5 = 15*mm  # Data processamento
        
        self.desenhar_campo(c, margin_x, y_campo, l1, altura_campo,
                          "Data do Documento", 
                          self.formatar_data(self.boleto.data_emissao), 8)
        
        self.desenhar_campo(c, margin_x + l1, y_campo, l2, altura_campo,
                          "Nº do Documento", 
                          str(self.boleto.numero_documento), 9)
        
        self.desenhar_campo(c, margin_x + l1 + l2, y_campo, l3, altura_campo,
                          "Espécie Doc.", 
                          "DM", 8)
        
        self.desenhar_campo(c, margin_x + l1 + l2 + l3, y_campo, l4, altura_campo,
                          "Aceite", 
                          "N", 8)
        
        self.desenhar_campo(c, margin_x + l1 + l2 + l3 + l4, y_campo, l5, altura_campo,
                          "Data Process.", 
                          self.formatar_data(datetime.now().date()), 7)
        
        # Nosso Número (direita)
        self.desenhar_campo(c, margin_x + largura_esquerda, y_campo, largura_direita, altura_campo,
                          "Nosso Número", 
                          str(self.boleto.nosso_numero), 9, bold_valor=True)
        
        # === QUARTA LINHA ===
        y_campo -= altura_campo
        
        l1 = 30*mm  # Uso do banco
        l2 = 20*mm  # Carteira
        l3 = 20*mm  # Espécie
        l4 = 30*mm  # Quantidade
        l5 = 25*mm  # Valor (x Quantidade)
        
        self.desenhar_campo(c, margin_x, y_campo, l1, altura_campo,
                          "Uso do Banco", 
                          "", 8)
        
        self.desenhar_campo(c, margin_x + l1, y_campo, l2, altura_campo,
                          "Carteira", 
                          str(self.config.carteira), 9)
        
        self.desenhar_campo(c, margin_x + l1 + l2, y_campo, l3, altura_campo,
                          "Espécie", 
                          "R$", 8)
        
        self.desenhar_campo(c, margin_x + l1 + l2 + l3, y_campo, l4, altura_campo,
                          "Quantidade", 
                          "", 8)
        
        self.desenhar_campo(c, margin_x + l1 + l2 + l3 + l4, y_campo, l5, altura_campo,
                          "Valor", 
                          "", 8)
        
        # (=) Valor do Documento (direita)
        self.desenhar_campo(c, margin_x + largura_esquerda, y_campo, largura_direita, altura_campo,
                          "(=) Valor do Documento", 
                          self.formatar_valor(self.boleto.valor_documento), 10, bold_valor=True)
        
        # === ÁREA DE INSTRUÇÕES (esquerda) E CAMPOS DE VALORES (direita) ===
        y_campo -= altura_campo
        altura_instrucoes = 40*mm
        
        # Caixa de instruções
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.5)
        c.rect(margin_x, y_campo - altura_instrucoes, largura_esquerda, altura_instrucoes)
        
        # Título
        c.setFont("Helvetica", 6)
        c.drawString(margin_x + 1*mm, y_campo - 3*mm, "Instruções (Texto de responsabilidade do beneficiário)")
        
        # Instruções
        c.setFont("Helvetica", 8)
        inst_y = y_campo - 7*mm
        instrucoes = []
        if self.config.instrucao1:
            instrucoes.append(self.config.instrucao1)
        if self.config.instrucao2:
            instrucoes.append(self.config.instrucao2)
        if self.config.instrucao3:
            instrucoes.append(self.config.instrucao3)
        
        # Se não houver instruções, adiciona instruções padrão
        if not instrucoes:
            instrucoes = [
                "- Não receber após o vencimento",
                "- Após vencimento cobrar multa de 2% e juros de mora",
                "- Em caso de dúvidas entre em contato com o beneficiário"
            ]
        
        for inst in instrucoes[:6]:  # Máximo 6 linhas
            c.drawString(margin_x + 2*mm, inst_y, inst[:80])
            inst_y -= 4*mm
        
        # Campos de valores à direita
        y_valor = y_campo
        altura_valor = 8*mm
        
        self.desenhar_campo(c, margin_x + largura_esquerda, y_valor, largura_direita, altura_valor,
                          "(-) Desconto/Abatimento", 
                          self.formatar_valor(self.boleto.valor_desconto) if self.boleto.valor_desconto and self.boleto.valor_desconto > 0 else "", 9)
        
        y_valor -= altura_valor
        self.desenhar_campo(c, margin_x + largura_esquerda, y_valor, largura_direita, altura_valor,
                          "(-) Outras Deduções", 
                          "", 9)
        
        y_valor -= altura_valor
        mora_texto = ""
        if self.config.percentual_juros_mes and self.config.percentual_juros_mes > 0:
            mora_texto = f"{self.config.percentual_juros_mes}% a.m."
        self.desenhar_campo(c, margin_x + largura_esquerda, y_valor, largura_direita, altura_valor,
                          "(+) Mora/Multa", 
                          mora_texto, 8)
        
        y_valor -= altura_valor
        self.desenhar_campo(c, margin_x + largura_esquerda, y_valor, largura_direita, altura_valor,
                          "(+) Outros Acréscimos", 
                          "", 9)
        
        y_valor -= altura_valor
        self.desenhar_campo(c, margin_x + largura_esquerda, y_valor, largura_direita, altura_valor,
                          "(=) Valor Cobrado", 
                          "", 9)
        
        # === DADOS DO SACADO/PAGADOR ===
        y_campo = y_campo - altura_instrucoes - altura_campo
        
        pagador_texto = f"{self.cliente.nome}"
        doc_texto = f"CPF/CNPJ: {self.formatar_cpf_cnpj(self.cliente.cpf_cnpj)}"
        
        # Primeira linha do sacado
        largura_total = largura_esquerda + largura_direita
        self.desenhar_campo(c, margin_x, y_campo, largura_total, altura_campo,
                          "Sacado", 
                          f"{pagador_texto} - {doc_texto}", 8)
        
        # Segunda linha do sacado (endereço)
        y_campo -= altura_campo
        endereco = self.cliente.endereco or ""
        cidade = self.cliente.cidade or ""
        estado = self.cliente.estado or ""
        endereco_completo = f"{endereco}, {cidade}-{estado}".strip(", -")
        
        c.rect(margin_x, y_campo, largura_total, altura_campo)
        c.setFont("Helvetica", 8)
        c.drawString(margin_x + 1*mm, y_campo + altura_campo - 6*mm, endereco_completo)
        
        # === SACADOR/AVALISTA ===
        y_campo -= altura_campo
        self.desenhar_campo(c, margin_x, y_campo, largura_total, altura_campo,
                          "Sacador/Avalista", 
                          "", 8)
        
        # === CÓDIGO DE BARRAS ===
        y_campo -= 15*mm
        
        # Tenta desenhar o código de barras como imagem
        try:
            barcode_buffer = self.gerar_codigo_barras_imagem()
            if barcode_buffer:
                # Abre a imagem
                img = Image.open(barcode_buffer)
                
                # Desenha no PDF
                c.drawImage(ImageReader(img), 
                          margin_x, y_campo, 
                          width=170*mm, height=12*mm,
                          preserveAspectRatio=True)
        except Exception as e:
            # Fallback: mostra o código como texto
            c.setFont("Courier", 9)
            c.drawString(margin_x, y_campo + 6*mm, f"Código de Barras: {self.boleto.codigo_barras}")
        
        # === AUTENTICAÇÃO MECÂNICA ===
        y_campo -= 3*mm
        c.setFont("Helvetica", 7)
        c.drawString(margin_x, y_campo, "Autenticação Mecânica - Ficha de Compensação")
        
        return y_campo
    
    def gerar(self, arquivo_saida=None):
        """
        Gera o PDF do boleto
        
        Args:
            arquivo_saida: Caminho do arquivo PDF ou None para retornar BytesIO
        
        Returns:
            BytesIO se arquivo_saida for None, caso contrário None
        """
        # Se não foi fornecido arquivo, usa BytesIO
        if arquivo_saida is None:
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
        else:
            c = canvas.Canvas(arquivo_saida, pagesize=A4)
        
        # Gera recibo do sacado (parte superior)
        y = self.height - 20*mm
        y = self.gerar_recibo_sacado(c, y)
        
        # Gera ficha de compensação
        self.gerar_ficha_compensacao(c, y)
        
        # Finaliza o PDF
        c.showPage()
        c.save()
        
        # Se usou buffer, retorna ele
        if arquivo_saida is None:
            buffer.seek(0)
            return buffer
        
        return None


def gerar_pdf_boleto(boleto, arquivo_saida=None):
    """
    Função auxiliar para gerar PDF do boleto
    
    Args:
        boleto: Objeto Boleto
        arquivo_saida: Caminho do arquivo ou None para BytesIO
    
    Returns:
        BytesIO se arquivo_saida for None
    """
    gerador = GeradorBoletoPDF(boleto)
    return gerador.gerar(arquivo_saida)
