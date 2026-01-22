#!/usr/bin/env python
"""
Script para adicionar campos faltantes nas tabelas do módulo contas_receber
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.db import connection

def executar_sql():
    """Executa os comandos SQL para adicionar campos"""
    
    with connection.cursor() as cursor:
        print("Adicionando campos na tabela contas_receber_contareceber...")
        
        # ContaReceber - pagamento_parcial
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_contareceber 
                ADD COLUMN pagamento_parcial TINYINT(1) NOT NULL DEFAULT 0
            """)
            print("✓ Campo pagamento_parcial adicionado")
        except Exception as e:
            print(f"  Campo pagamento_parcial já existe ou erro: {e}")
        
        # ContaReceber - tipo_parcela
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_contareceber 
                ADD COLUMN tipo_parcela VARCHAR(2) NOT NULL DEFAULT 'NF'
            """)
            print("✓ Campo tipo_parcela adicionado")
        except Exception as e:
            print(f"  Campo tipo_parcela já existe ou erro: {e}")
        
        # ContaReceber - codigo_identificador
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_contareceber 
                ADD COLUMN codigo_identificador VARCHAR(100) NULL UNIQUE
            """)
            print("✓ Campo codigo_identificador adicionado")
        except Exception as e:
            print(f"  Campo codigo_identificador já existe ou erro: {e}")
        
        # ContaReceber - motivo_desconto
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_contareceber 
                ADD COLUMN motivo_desconto VARCHAR(255) NULL
            """)
            print("✓ Campo motivo_desconto adicionado")
        except Exception as e:
            print(f"  Campo motivo_desconto já existe ou erro: {e}")
        
        # ContaReceber - observacao_negociacao
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_contareceber 
                ADD COLUMN observacao_negociacao TEXT NULL
            """)
            print("✓ Campo observacao_negociacao adicionado")
        except Exception as e:
            print(f"  Campo observacao_negociacao já existe ou erro: {e}")
        
        # ContaReceber - id_parcela_externo
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_contareceber 
                ADD COLUMN id_parcela_externo INT NULL
            """)
            print("✓ Campo id_parcela_externo adicionado")
        except Exception as e:
            print(f"  Campo id_parcela_externo já existe ou erro: {e}")
        
        print("\nAdicionando campos na tabela contas_receber_notafiscal...")
        
        # NotaFiscal - total_produto
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_notafiscal 
                ADD COLUMN total_produto DECIMAL(12,2) NOT NULL DEFAULT 0
            """)
            print("✓ Campo total_produto adicionado")
        except Exception as e:
            print(f"  Campo total_produto já existe ou erro: {e}")
        
        # NotaFiscal - total_ipi_valor
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_notafiscal 
                ADD COLUMN total_ipi_valor DECIMAL(12,2) NOT NULL DEFAULT 0
            """)
            print("✓ Campo total_ipi_valor adicionado")
        except Exception as e:
            print(f"  Campo total_ipi_valor já existe ou erro: {e}")
        
        # NotaFiscal - total_nota
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_notafiscal 
                ADD COLUMN total_nota DECIMAL(12,2) NOT NULL DEFAULT 0
            """)
            print("✓ Campo total_nota adicionado")
        except Exception as e:
            print(f"  Campo total_nota já existe ou erro: {e}")
        
        # NotaFiscal - id_externo
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_notafiscal 
                ADD COLUMN id_externo INT NULL
            """)
            print("✓ Campo id_externo adicionado")
        except Exception as e:
            print(f"  Campo id_externo já existe ou erro: {e}")
        
        print("\nAdicionando campos na tabela contas_receber_creditocliente...")
        
        # CreditoCliente - status
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_creditocliente 
                ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pendente'
            """)
            print("✓ Campo status adicionado")
        except Exception as e:
            print(f"  Campo status já existe ou erro: {e}")
        
        # CreditoCliente - valor_credito_liberado
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_creditocliente 
                ADD COLUMN valor_credito_liberado DECIMAL(12,2) NULL
            """)
            print("✓ Campo valor_credito_liberado adicionado")
        except Exception as e:
            print(f"  Campo valor_credito_liberado já existe ou erro: {e}")
        
        # CreditoCliente - data_liberacao
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_creditocliente 
                ADD COLUMN data_liberacao DATETIME(6) NULL
            """)
            print("✓ Campo data_liberacao adicionado")
        except Exception as e:
            print(f"  Campo data_liberacao já existe ou erro: {e}")
        
        # CreditoCliente - usuario_liberador_id
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_creditocliente 
                ADD COLUMN usuario_liberador_id BIGINT NULL
            """)
            print("✓ Campo usuario_liberador_id adicionado")
        except Exception as e:
            print(f"  Campo usuario_liberador_id já existe ou erro: {e}")
        
        # CreditoCliente - motivo_reprovacao
        try:
            cursor.execute("""
                ALTER TABLE contas_receber_creditocliente 
                ADD COLUMN motivo_reprovacao TEXT NULL
            """)
            print("✓ Campo motivo_reprovacao adicionado")
        except Exception as e:
            print(f"  Campo motivo_reprovacao já existe ou erro: {e}")
        
        print("\n✅ Processo concluído!")

if __name__ == '__main__':
    executar_sql()
