# Relatório Consolidado de Execução dos Testes Automatizados

## 1. Sumário Executivo da Bateria de Testes
- **Data e Hora da Execução:** 23/11/2026 - 23:39:43 BRT
- **Ambiente:** Python 3.14.3 / Windows 11 / pytest 9.2.0 / SQLite 3
- **Total de Casos Executados:** 33 testes
- **Total de Testes Aprovados (PASSED):** 33 testes (100.0%)
- **Total de Falhas (FAILED):** 0 testes (0.0%)
- **Tempo Total de Execução:** 57.15 segundos (tempo decorrente do custo computacional proposital do hashing PBKDF2 com 1.000.000 iterações)

## 2. Tabela Detalhada de Resultados por Caso de Teste

| Identificador | Caso de Teste | Módulo | Resultado Obtido | Status |
| :---: | :--- | :--- | :--- | :---: |
| **CT-AUT-01** | `test_login_valido_usuario` | `test_auth.py` | HTTP 302 para `/meus_chamados`, sessão válida | **APROVADO** |
| **CT-AUT-02** | `test_login_valido_admin` | `test_auth.py` | HTTP 302 para `/admin`, sessão `tipo='admin'` | **APROVADO** |
| **CT-AUT-03** | `test_login_invalido_senha_incorreta` | `test_auth.py` | Flash exibido, sem inicialização de sessão | **APROVADO** |
| **CT-AUT-04** | `test_login_invalido_usuario_inexistente` | `test_auth.py` | Mensagem genérica, mitigando enumeração | **APROVADO** |
| **CT-AUT-05** | `test_armazenamento_seguro_senhas` | `test_auth.py` | 100% dos registros iniciam com `pbkdf2:sha256:` | **APROVADO** |
| **CT-AUT-06** | `test_logout_encerra_sessao` | `test_auth.py` | Sessão limpa, redirecionado para `/` | **APROVADO** |
| **CT-AUT-07** | `test_alterar_senha_sucesso` | `test_auth.py` | Hash atualizado no banco, nova senha válida | **APROVADO** |
| **CT-AUT-08** | `test_alterar_senha_rejeita_curta` | `test_auth.py` | Senhas < 6 caracteres rejeitadas com flash | **APROVADO** |
| **CT-CHAM-01** | `test_abertura_chamado_sucesso` | `test_chamados.py` | Chamado gravado com status='aberto' e nível='N1' | **APROVADO** |
| **CT-CHAM-02** | `test_abertura_chamado_rejeita_campos_vazios` | `test_chamados.py` | Rejeição imediata sem persistir no banco | **APROVADO** |
| **CT-CHAM-03** | `test_meus_chamados_filtra_por_usuario` | `test_chamados.py` | Exibe exclusivamente chamados do solicitante ativo | **APROVADO** |
| **CT-CHAM-04** | `test_tecnico_assume_chamado` | `test_chamados.py` | Status='em andamento', `bloqueado_por=tecnico` | **APROVADO** |
| **CT-CHAM-05** | `test_tecnico_escalona_chamado_n1_para_n2` | `test_chamados.py` | Nível escalonado para 'N2', lock liberado | **APROVADO** |
| **CT-CHAM-06** | `test_tecnico_finaliza_chamado` | `test_chamados.py` | Status='finalizado', parecer técnico registrado | **APROVADO** |
| **CT-CHAM-07** | `test_exclusao_chamado_titular_sucesso` | `test_chamados.py` | Autor exclui chamado próprio com sucesso | **APROVADO** |
| **CT-CHAM-08** | `test_exclusao_chamado_nao_titular_bloqueado` | `test_chamados.py` | Bloqueio de exclusão de chamado de terceiro (IDOR) | **APROVADO** |
| **CT-PERM-01** | `test_rota_admin_bloqueia_anonimo` | `test_permissions.py` | Anônimo redirecionado para `/login` | **APROVADO** |
| **CT-PERM-02** | `test_rota_admin_bloqueia_usuario_comum` | `test_permissions.py` | Usuário comum impedido de acessar `/admin` | **APROVADO** |
| **CT-PERM-03** | `test_rota_admin_permite_administrador` | `test_permissions.py` | Administrador acessa `/admin` normalmente | **APROVADO** |
| **CT-PERM-04** | `test_rota_chamados_bloqueia_usuario_comum` | `test_permissions.py` | Usuário comum bloqueado na fila técnica | **APROVADO** |
| **CT-PERM-05** | `test_rota_chamados_permite_tecnico_n1` | `test_permissions.py` | Técnico N1 acessa a fila operacional | **APROVADO** |
| **CT-PERM-06** | `test_rota_gerente_permite_gerente_e_admin` | `test_permissions.py` | Técnico bloqueado; gerente e admin autorizados | **APROVADO** |
| **CT-PERM-07** | `test_rota_auditoria_permite_admin_e_gerente` | `test_permissions.py` | Painel de auditoria restrito a admin e gerente | **APROVADO** |
| **CT-PERM-08** | `test_rota_colaboradores_permite_apenas_admin` | `test_permissions.py` | Catálogo de colaboradores restrito a admin | **APROVADO** |
| **CT-SEC-01** | `test_sql_injection_login_bloqueado` | `test_security.py` | Payload `' OR '1'='1` rejeitado com segurança | **APROVADO** |
| **CT-SEC-02** | `test_sql_injection_filtro_chamados_neutralizado` | `test_security.py` | Injeção em query param neutralizada por whitelist | **APROVADO** |
| **CT-SEC-03** | `test_csrf_bloqueia_requisicao_sem_token` | `test_security.py` | POST sem token CSRF rejeitado com HTTP 403 | **APROVADO** |
| **CT-SEC-04** | `test_csrf_permite_requisicao_com_token_valido` | `test_security.py` | POST com token legítimo aprovado | **APROVADO** |
| **CT-SEC-05** | `test_security_headers_presentes` | `test_security.py` | Headers de proteção HTTP presentes nas respostas | **APROVADO** |
| **CT-SEC-06** | `test_debug_mode_desativado` | `test_security.py` | Servidor configurado com `debug=False` | **APROVADO** |
| **CT-SEC-07** | `test_fail_secure_erro_404_sem_stacktrace` | `test_security.py` | Erro amigável sem exposição de stack trace | **APROVADO** |
| **CT-SEC-08** | `test_registro_auditoria_eventos_criticos` | `test_security.py` | Eventos persistidos na tabela `logs_auditoria` | **APROVADO** |
| **CT-SEC-09** | `test_minimizacao_dados_colaboradores_lgpd` | `test_security.py` | Ausência comprovada de campos sensíveis de PII | **APROVADO** |

## 3. Evidência em Arquivo
O log completo bruto da execução do pytest encontra-se armazenado em `docs/testes/evidencias/pytest_output.txt`.
