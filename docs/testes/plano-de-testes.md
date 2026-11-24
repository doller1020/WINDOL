# Plano de Testes de Software e Segurança

## 1. Objetivo e Escopo
O objetivo deste plano de testes é validar empiricamente a eficácia das intervenções de segurança, os controles de acesso RBAC, a proteção contra vulnerabilidades web clássicas (OWASP Top 10) e a aderência aos princípios da LGPD no Sistema Help Desk WINDOL.

## 2. Metodologia de Teste
- **Abordagem:** Testes de Caixa-Cinza (Grey-Box Testing) combinando análise funcional com inspeção direta do banco de dados e do estado interno de sessões.
- **Framework de Automação:** `pytest` (versão 9.x), executando no ambiente Python 3.14.
- **Isolamento de Ambiente:** Utilização de *fixtures* do pytest para criação de bancos SQLite temporários em memória/disco isolado (`tempfile.mkstemp()`), garantindo que **nenhum teste execute operações destrutivas ou altere a base de dados operacional real (`database.db`)**.

## 3. Matriz de Cobertura de Testes

| Categoria de Teste | Módulo de Teste | Quantidade de Casos de Teste | Foco de Avaliação |
| :--- | :--- | :---: | :--- |
| **Autenticação e Credenciais** | `tests/test_auth.py` | 8 | Login válido/inválido, PBKDF2 com salt, logout, troca de senha e regras de tamanho mínimo. |
| **Controle de Acesso (RBAC)** | `tests/test_permissions.py` | 8 | Bloqueio de anônimos, decoradores `@login_required` e `@perfil_required`, menor privilégio. |
| **Ciclo de Vida de Chamados** | `tests/test_chamados.py` | 8 | Abertura, listagem filtrada por solicitante, triagem técnica, escalonamento, finalização e proteção IDOR. |
| **Segurança e LGPD** | `tests/test_security.py` | 9 | Injeção de SQL, proteção CSRF, Security Headers, debug=False, erros 404/500, auditoria e minimização. |
| **Total de Testes Automatizados** | **4 módulos** | **33 casos de teste** | **100% dos fluxos críticos de segurança avaliados.** |

## 4. Critérios de Aceitação e Aprovação (Go/No-Go)
- **Critério de Sucesso:** 100% dos testes executados com status `PASSED`.
- **Tolerância a Falhas Críticas:** Zero tolerância (0 falhas em autenticação, RBAC ou injeção).
- **Relatório de Execução:** Registro automático de saída com timestamps e contadores.
