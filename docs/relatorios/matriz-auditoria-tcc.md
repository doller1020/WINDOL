# Matriz de Auditoria do TCC — WINDOL
## Sistema Help Desk Acadêmico | TCC UPIS — Bacharelado em Sistemas de Informação

> **Data da Auditoria:** 24 de Novembro de 2026
> **Repositório Auditado:** https://github.com/doller1020/WINDOL — Commit `124c888`
> **Documento Auditado:** TCC_Analise_Seguranca_Windol_UPIS_Revisado.docx (Rev. Final)
> **Metodologia:** Análise estática de código (SAST manual), leitura integral do TCC, confrontação direta entre afirmações do documento e evidências no repositório.

---

## 1. Legenda de Situações

| Situação | Significado |
|---|---|
| ✅ **Comprovado** | Afirmação verificada por evidência técnica no código ou nos testes |
| ⚠️ **Parcialmente Comprovado** | Afirmação parcialmente validada; existem ressalvas ou limitações |
| ❌ **Não Comprovado** | Afirmação não possui evidência verificável no repositório |
| 🔧 **Corrigido** | Problema identificado na auditoria e corrigido nesta revisão |

---

## 2. Matriz de Auditoria (Formato Exato do Prompt)

| # | Afirmação presente no TCC | Evidência encontrada | Arquivo e localização | Situação | Problema identificado | Correção necessária / aplicada | Evidência que valida a correção |
|:---:|:---|:---|:---|:---:|:---|:---|:---|
| **1** | "O sistema original armazenava senhas em texto puro no banco SQLite" | Repositório original (`sistema-chamados-faculdade`) continha `INSERT INTO usuarios VALUES (..., '1234', ...)` sem qualquer derivação criptográfica | `criar_banco.py` legado (original) — linha de INSERT de usuários | ✅ **Comprovado** | Senhas plaintext expunham todos os usuários em caso de acesso ao arquivo `database.db` | **Corrigido:** Implementação de PBKDF2:SHA-256 com salt de 16 bytes via Werkzeug | `test_auth.py::test_armazenamento_seguro_senhas` — confirma que 100% dos hashes iniciam com `pbkdf2:sha256:` |
| **2** | "A `SECRET_KEY` era hardcoded no código como valor fixo `'1234'`" | Código original continha `app.secret_key = "1234"` na linha 7 de `web.py` original | `web.py` original — linha 7 | ✅ **Comprovado** | Chave pública no repositório permitia forjamento de cookies de sessão por qualquer atacante com acesso ao código | **Corrigido:** Função `carregar_secret_key()` com Fail-Secure via variável de ambiente `WINDOL_SECRET_KEY` | `web.py` linhas 23–46; `.env.example` commitado; `.gitignore` protege `.env` real |
| **3** | "O modo debug estava ativado em produção (`debug=True`)" | Verificado em `web.py` original: `app.run(debug=True)` na linha 501 | `web.py` legado — linha final | ✅ **Comprovado** | Werkzeug debugger exposto com possibilidade de RCE via console interativo | **Corrigido:** `debug=False` hardcoded; porta via `os.environ.get("PORT", 5000)` | `test_security.py::test_debug_mode_desativado` |
| **4** | "O sistema não validava a sessão do usuário antes de executar rotas críticas" | Rota `/finalizar/<id>` no original não continha `session.get("usuario")` antes de executar SQL de encerramento | `web.py` legado — rotas `/finalizar` e `/resolver` | ✅ **Comprovado** | Usuário anônimo podia encerrar chamados via POST direto sem qualquer sessão | **Corrigido:** Decoradores `@login_required` e `@perfil_required` em todas as rotas operacionais | `test_permissions.py::test_rota_admin_bloqueia_anonimo` |
| **5** | "O controle de acesso era baseado apenas na interface gráfica, sem validação no backend" | Templates exibiam/ocultavam menus por perfil, mas as rotas backend não verificavam perfil | `web.py` legado — ausência de verificação de `session["tipo"]` nas rotas | ✅ **Comprovado** | Usuário comum podia invocar endpoints de técnico e administrador diretamente | **Corrigido:** `@perfil_required(*perfis)` valida obrigatoriamente o perfil na sessão antes de executar qualquer lógica | `test_permissions.py::test_rota_admin_bloqueia_usuario_comum` |
| **6** | "O sistema não possuía proteção contra CSRF" | Nenhum formulário original continha campo `csrf_token`; nenhum middleware de validação existia | Templates originais: todos os `<form method="POST">` sem campo oculto de token | ✅ **Comprovado** | Requisições forjadas por terceiros eram aceitas como legítimas | **Corrigido:** Middleware `@before_request` valida token CSRF em todos os POSTs; templates injetam `<input type="hidden" name="csrf_token">` | `test_security.py::test_csrf_bloqueia_requisicao_sem_token` |
| **7** | "O sistema não registrava logs de auditoria ou eventos de segurança" | Nenhuma tabela de logs existia no banco original; nenhuma chamada de registro estava presente | `criar_banco.py` original — ausência de `CREATE TABLE logs_auditoria`; `web.py` original — sem qualquer `INSERT` de log | ✅ **Comprovado** | Impossibilidade de perícia pós-incidente e descumprimento do Art. 6º, X da LGPD | **Corrigido:** Tabela `logs_auditoria` criada com campos `id, usuario, acao, detalhes, ip, timestamp`; função `registrar_log()` chamada em login, logout, falhas CSRF e acessos negados | `test_security.py::test_registro_auditoria_eventos_criticos` |
| **8** | "A tela de edição de usuário expunha a senha hash em campo HTML visível" | Template `editar_usuario.html` continha `value="{{ usuario['senha'] }}"` em campo de texto | `templates/editar_usuario.html` original — campo `input type="text" value="{{ usuario['senha'] }}"` | ✅ **Comprovado** | Hash/senha exposta visualmente no DOM e ao inspetor de elementos do navegador | **Corrigido:** Campo de senha removido do `value`; input reformulado como opcional (vazio = sem alteração) | `templates/editar_usuario.html` atual — campo sem pré-preenchimento de senha |
| **9** | "Consultas SQL eram parcialmente vulneráveis a injeção, especialmente em parâmetros de ordenação" | Query `ORDER BY` no original usava concatenação direta com parâmetro do request | `web.py` legado — queries com f-string ou concatenação de `ordem` | ✅ **Comprovado** | Payloads como `; DROP TABLE chamados--` podiam ser injetados via parâmetro de URL | **Corrigido:** Whitelist estrita de ordenação; `ordem_sql = "ASC" if ordem == "antigo" else "DESC"` | `test_security.py::test_sql_injection_filtro_chamados_neutralizado` |
| **10** | "O WINDOL atualizado implementa hash PBKDF2:SHA-256 com salt individual" | `criar_banco.py` revisado usa `generate_password_hash(senha)` que retorna `pbkdf2:sha256:1000000$<salt>$<hash>` | `criar_banco.py` linhas 88–105 | ✅ **Comprovado** | — | Nenhuma correção necessária; funcionalidade validada | `test_auth.py::test_armazenamento_seguro_senhas` — PASSED |
| **11** | "O sistema implementa RBAC com 6 perfis funcionais: usuario, tecnico_n1, tecnico_n2, tecnico_n3, gerente, admin" | Tabela `usuarios` com coluna `tipo` validada nos decoradores; 6 perfis mapeados na matriz de permissões | `web.py` — `@perfil_required`; `docs/arquitetura/controle-acesso-rbac.md` — Tabela de Permissões | ✅ **Comprovado** | — | Nenhuma correção necessária | `test_permissions.py` — 8/8 testes PASSED cobrindo todos os perfis |
| **12** | "O sistema mantém trilha de auditoria de eventos críticos com IP e timestamp" | Tabela `logs_auditoria` populada com `acao`, `detalhes`, `usuario`, `ip`, `timestamp` | `web.py` — função `registrar_log()` e rotas que a invocam | ✅ **Comprovado** | — | Nenhuma correção necessária | `test_security.py::test_registro_auditoria_eventos_criticos` — PASSED |
| **13** | "O sistema está em conformidade com os princípios da LGPD, especialmente Minimização de Dados e Transparência" | Tabela `colaboradores` com dados minimizados (nome, cargo, ramal apenas); página `/privacidade` com aviso formal; coleta sem campos de PII excedentes | `criar_banco.py` — definição de `colaboradores`; `templates/privacidade.html` | ⚠️ **Parcialmente Comprovado** | Conformidade técnica implementada; conformidade jurídica plena exige DPO, RIPD e contratos formais — fora do escopo do sistema | Limitação transparente declarada no TCC e em `docs/seguranca/riscos-residuais.md` | `test_security.py::test_minimizacao_dados_colaboradores_lgpd` — PASSED |
| **14** | "Todas as referências ao material DEVSEG foram removidas do TCC e do código" | Busca por string `DEVSEG` retorna 0 ocorrências em todos os arquivos do repositório após revisão | `git grep -ri "devseg"` — 0 resultados | ✅ **Comprovado** | — | Nenhuma correção necessária; substituição completa por OWASP, NIST SSDF, CIS v8 e LGPD | Inspeção de todos os arquivos `.py`, `.html`, `.md` e `.docx` |
| **15** | "O sistema original apresentava protótipos de código CLI (app.py, chamados.py, login.py) como fase inicial de desenvolvimento" | Arquivos `app.py`, `chamados.py` e `login.py` presentes no repositório como protótipos CLI predecessores | `app.py`, `chamados.py`, `login.py` na raiz do projeto | ✅ **Comprovado** | Arquivos não documentados nem analisados previamente | Arquivos documentados no README como artefatos históricos da fase inicial de desenvolvimento | Presença no repositório Git com histórico de commits confirmado |
| **16** | "Scripts de migração de banco de dados (`alterar_banco.py`, `alterar_nivel.py`, `alterar_tabela.py`) comprovam a evolução incremental do schema" | Arquivos presentes com comandos `ALTER TABLE` para adicionar colunas `bloqueado_por`, `tecnico_responsavel`, `resposta_tecnica`, `nivel`, `data` | `alterar_banco.py`, `alterar_nivel.py`, `alterar_tabela.py` | ✅ **Comprovado** | Scripts não estavam documentados como evidência da evolução do banco | Referência explícita adicionada à documentação como evidência histórica do desenvolvimento incremental | Presença dos arquivos com comandos `ALTER TABLE` verificáveis |
| **17** | "Os diagramas de arquitetura foram produzidos com base na implementação real do sistema" | Diagramas Mermaid nos `.md` correspondem às rotas, tabelas e fluxos reais do `web.py` | `docs/arquitetura/*.md` — todos os 6 diagramas | ✅ **Comprovado** | PNGs não foram gerados para inclusão direta no TCC | PNGs gerados via script Python e salvos em `docs/arquitetura/png/` | Arquivos `.png` em `docs/arquitetura/png/` verificáveis |
| **18** | "Os gráficos apresentados no TCC são baseados em dados reais coletados do projeto" | 4 gráficos + 4 CSVs gerados pelo script `generate_charts.py` usando dados reais das vulnerabilidades, testes e controles | `docs/graficos/*.png` e `docs/graficos/*.csv` | ✅ **Comprovado** | — | Nenhuma correção necessária | Arquivos `generate_charts.py`, PNGs e CSVs presentes no repositório |
| **19** | "A suíte de testes automatizados cobre 33 casos com 100% de aprovação" | Execução do pytest gerou saída com `33 passed` em dois momentos independentes (sessão anterior e confirmação atual) | `docs/testes/evidencias/pytest_output.txt`; `tests/*.py` | ✅ **Comprovado** | — | Nenhuma correção necessária | `pytest_output.txt` com saída real `33 passed in 57.15s` e `33 passed in 58.82s` |
| **20** | "O relatório Wingrid.txt documenta a divisão de responsabilidades entre os autores" | Arquivo presente descrevendo contribuição colaborativa inicial (máquina Doller) e continuidade via GitHub da Wingrid | `relatório Wingrid.txt` na raiz do projeto | ✅ **Comprovado** | Arquivo não estava referenciado na documentação do projeto | Referenciado no README como documento de autoria e divisão de trabalho | Arquivo commitado no repositório com conteúdo verificável |

---

## 3. Resumo Quantitativo da Auditoria

| Situação | Quantidade | Percentual |
|---|---|---|
| ✅ Comprovado | 18 | 90% |
| ⚠️ Parcialmente Comprovado | 1 | 5% |
| ❌ Não Comprovado | 0 | 0% |
| 🔧 Corrigido nesta revisão | 10 | — |

---

## 4. Itens com Limitações Remanescentes

| Item | Limitação declarada | Risco residual |
|---|---|---|
| Conformidade LGPD | Conformidade técnica parcial; conformidade jurídica plena exige DPO, RIPD, contratos com operadores | Baixo — mitigado pela transparência acadêmica |
| MFA (Autenticação Multifator) | Não implementado no escopo do TCC | Médio — credenciais únicas vulneráveis a phishing |
| Rate limiting | Ausência de bloqueio após N tentativas de login | Médio — força bruta ainda possível, embora mitigada pelo PBKDF2 |
| PDF do TCC | Microsoft Word COM não disponível neste ambiente | Nenhum — `.docx` completo e funcional |
| Logs no mesmo banco | `logs_auditoria` compartilha o SQLite com dados operacionais | Baixo — risco acadêmico irrelevante; em produção exigiria segregação |

---

*Auditoria realizada em 24/11/2026 — Commit de referência: `124c888` — Branch: `main`*
