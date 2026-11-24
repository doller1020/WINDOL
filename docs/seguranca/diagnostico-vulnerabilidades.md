# Diagnóstico de Vulnerabilidades de Segurança (Código Original)

## 1. Metodologia de Diagnóstico
A auditoria técnica inicial realizou uma análise estática de código (SAST manual) e inspeção do esquema de banco de dados no repositório original (*sistema-chamados-faculdade*). As vulnerabilidades foram classificadas conforme o catálogo **OWASP Top 10:2021** e mapeadas para a taxonomia **Common Weakness Enumeration (CWE)**.

## 2. Inventário Detalhado das Vulnerabilidades Identificadas

### VUL-01: Armazenamento de Senhas em Texto Puro
- **Classificação:** OWASP A02:2021 (Cryptographic Failures) / CWE-256 (Plaintext Storage of a Password) / CWE-312 (Cleartext Storage of Sensitive Information)
- **Localização:** `criar_banco.py` e `web.py`
- **Severidade:** Crítica (CVSS v3.1: 9.8)
- **Descrição Técnica:** O script de criação do banco inseria credenciais em texto claro diretamente no SQLite (`INSERT INTO usuarios VALUES (..., '1234', ...)`). O módulo de autenticação executava `SELECT * FROM usuarios WHERE login=? AND senha=?` comparando strings sem qualquer derivação criptográfica.
- **Risco:** Comprometimento total e imediato de todas as contas em caso de acesso físico ao arquivo `database.db`, backup desprotegido ou injeção SQL.

---

### VUL-02: Chave de Sessão Estática e Pública (Hardcoded Secret Key)
- **Classificação:** OWASP A05:2021 (Security Misconfiguration) / CWE-798 (Use of Hard-coded Credentials) / CWE-321 (Use of Hard-coded Cryptographic Key)
- **Localização:** `web.py` (Linha 7 no original: `app.secret_key = "1234"`)
- **Severidade:** Alta (CVSS v3.1: 8.6)
- **Descrição Técnica:** A chave secreta utilizada pelo Flask para assinar os cookies de sessão de cliente era um valor trivial e público, fixado no código versionado.
- **Risco:** Qualquer atacante com conhecimento do código pode forjar cookies de sessão válidos de qualquer usuário (inclusive o administrador), contornando completamente o mecanismo de autenticação sem necessidade de conhecer a senha do usuário.

---

### VUL-03: Modo Debug Ativo em Ambiente de Execução (Debug Mode Enabled)
- **Classificação:** OWASP A05:2021 (Security Misconfiguration) / CWE-489 (Active Debug Code) / CWE-200 (Exposure of Sensitive Information)
- **Localização:** `web.py` (Linha 501 no original: `app.run(debug=True)`)
- **Severidade:** Alta (CVSS v3.1: 8.2)
- **Descrição Técnica:** A aplicação era iniciada com o depurador interativo do Werkzeug ativado.
- **Risco:** Em caso de exceção não tratada, o depurador gera uma página HTML contendo o console interativo do Python. Caso o invasor contorne ou obtenha o PIN do Werkzeug, é possível executar comandos arbitrários no sistema operacional (Remote Code Execution - RCE).

---

### VUL-04: Rota de Finalização Aberta sem Verificação de Autenticação
- **Classificação:** OWASP A01:2021 (Broken Access Control) / CWE-306 (Missing Authentication for Critical Function)
- **Localização:** `web.py` (Linhas 389-413 no original)
- **Severidade:** Crítica (CVSS v3.1: 9.1)
- **Descrição Técnica:** O endpoint `@app.route("/finalizar/<int:id>", methods=["POST"])` não verificava se havia uma sessão ativa (`session.get("usuario")`). Uma requisição POST forjada podia finalizar qualquer ticket do sistema mesmo originada de um cliente não autenticado.
- **Risco:** Violação massiva de integridade e disponibilidade dos chamados corporativos.

---

### VUL-05: Rota de Atendimento Acessível por Usuário Comum (Falha RBAC)
- **Classificação:** OWASP A01:2021 (Broken Access Control) / CWE-285 (Improper Authorization)
- **Localização:** `web.py` (Linhas 347-385 no original)
- **Severidade:** Alta (CVSS v3.1: 7.5)
- **Descrição Técnica:** O endpoint `@app.route("/resolver/<int:id>")` validava apenas se o usuário estava logado, sem verificar se o perfil era técnico (`tecnico_n1`, `tecnico_n2`, `tecnico_n3`) ou administrador. Usuários com perfil `usuario` podiam assumir tickets de outros usuários diretamente.
- **Risco:** Violação do Princípio do Menor Privilégio e quebra da segregação de funções.

---

### VUL-06: Ausência de Trilha de Auditoria e Logs de Segurança
- **Classificação:** OWASP A09:2021 (Security Logging and Monitoring Failures) / CWE-778 (Insufficient Logging)
- **Localização:** Omissão arquitetural em todo o projeto legado
- **Severidade:** Média (CVSS v3.1: 5.3)
- **Descrição Técnica:** O sistema não possuía nenhum mecanismo para registrar tentativas de login, acessos negados, exclusões de dados ou alterações de estado.
- **Risco:** Impossibilidade de detecção de ataques em andamento, incapacidade de realização de perícia pós-incidente e descumprimento do dever legal de prestação de contas (LGPD Art. 6º, X).

---

### VUL-07: Inexistência de Proteção contra Cross-Site Request Forgery (CSRF)
- **Classificação:** OWASP A01:2021 (Broken Access Control) / CWE-352 (Cross-Site Request Forgery)
- **Localização:** Todos os formulários HTML e rotas POST
- **Severidade:** Alta (CVSS v3.1: 8.1)
- **Descrição Técnica:** Nenhum formulário continha tokens de validação sincronizados com a sessão. Um atacante poderia induzir um usuário autenticado a clicar em um link externo malicioso contendo um formulário oculto que disparasse requisições POST para o sistema Help Desk.
- **Risco:** Execução de ações administrativas e operacionais forjadas em nome da vítima autenticada.

---

### VUL-08: Exposição de Hash/Senha em Campos de Entrada HTML
- **Classificação:** OWASP A02:2021 (Cryptographic Failures) / CWE-200 (Information Exposure)
- **Localização:** `templates/editar_usuario.html` (Linha 30 no original)
- **Severidade:** Média (CVSS v3.1: 5.5)
- **Descrição Técnica:** Ao carregar a tela de edição de usuário, o valor armazenado na coluna `senha` era injetado diretamente no atributo `value` do input `<input type="text" name="senha" value="{{ usuario['senha'] }}">`.
- **Risco:** Exposição da credencial a observadores físicos (*shoulder surfing*) e inclusão da senha no DOM em texto claro.
