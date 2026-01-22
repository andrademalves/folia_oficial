# Gestão TI — Status e Documentação (Dez 2025)

Este documento resume o que implementamos até agora e como usar.

## Visão Geral
- Apps principales: `usuarios`, `cadastros`, `financeiro`, `importacoes`.
- UI unificada com sidebar escura e fundo em gradiente (como nos outros módulos).
- Autenticação padrão Django + permissões via `usuarios.decorators.permissao_menu_required`.

## Importações (Futura → Gestão TI)
- Conexão Firebird usando `fdb` (driver Python).
- Modelo de log de importação: `ImportacaoLog` com progresso persistido (total, processados, criados, atualizados, erros, status, mensagens).
- Dados espelhados (simplificados): `CadastroFutura`, `NotaFiscalFutura`, `ContaParcelaFutura` com FK para o log.
- Fluxo assíncrono com progresso:
  - Endpoint para iniciar: `POST /importacoes/api/iniciar/` (cria log e dispara thread).
  - Endpoint de status: `GET /importacoes/api/status/<log_id>/` (retorna progresso JSON).
  - Frontend: modal Bootstrap com barra de progresso e texto "Importado X de Y", polling a cada ~1.5s.
- Páginas com modal e polling: `cadastro_geral`, `notas_fiscais`, `parcelas`.

### Rotas Importações
- Dashboard: `/importacoes/`
- Importar Cadastros: `/importacoes/cadastro-geral/`
- Importar Notas Fiscais: `/importacoes/notas-fiscais/`
- Importar Parcelas: `/importacoes/parcelas/`
- Logs: `/importacoes/logs/` e detalhe `/importacoes/logs/<id>/`
- APIs: `/importacoes/api/iniciar/` e `/importacoes/api/status/<id>/`

## Como Rodar (local)
1. Ativar venv e instalar dependências:

```powershell
cd "C:\HD_Antigo\01- Projetos Dev\1.3 Gestao"
.\venv\Scripts\Activate
python -m pip install -r requirements.txt
```

2. Migrar banco:

```powershell
python manage.py migrate
```

3. Executar servidor:

```powershell
python manage.py runserver
```

4. Acessar:
- Módulos: `/` (home dos módulos via `usuarios:home_modulos`)
- Importações: `/importacoes/`

## Configuração Firebird
- Arquivo: `importacoes/firebird_utils.py` (classe `FirebirdConnector`).
- Parâmetros (host, porta, caminho do banco, usuário, senha) estão centralizados ali.
- O driver `fdb` precisa estar instalado (já listado em `requirements.txt`).

## Detalhes Técnicos
- Backend atualiza o `ImportacaoLog` periodicamente durante a importação (total_registros, processados, mensagem e status).
- Frontend intercepta o submit e chama as APIs, exibindo modal de progresso.
- Templates atualizados para manter o padrão visual:
  - Importações: `dashboard.html` com sidebar escura e cards no padrão.
  - Páginas de importação com botão "Voltar ao Principal" (retorna a `/`).

## Comandos Úteis
- Checar sistema:

```powershell
python manage.py check
```

- Atribuir permissões iniciais:

```powershell
python manage.py atribuir_permissoes
```

## Próximos Passos Sugeridos
- Uniformizar o estilo dark também em `logs.html` e `detalhe_log.html`.
- Parametrizar as credenciais do Firebird via variáveis de ambiente.
- Acrescentar paginação e filtros nos logs.

---
Atualizado em: 21/12/2025
