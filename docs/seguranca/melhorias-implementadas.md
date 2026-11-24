# Melhorias de Segurança Implementadas no Sistema WINDOL

## 1. Resumo Executivo das Implementações
A evolução do sistema Help Desk para o Sistema WINDOL consistiu em uma intervenção estruturada de engenharia de software para transformar um protótipo legado repleto de vulnerabilidades bloqueantes em uma aplicação web endurecida (*hardened*), rastreável e aderente aos requisitos legais da LGPD.

## 2. Detalhamento Técnico das Modificações

### 2.1 Criptografia Adaptativa de Senhas (PBKDF2/SHA-256)
- **Arquivo Modificado:** `criar_banco.py` e `web.py`
- **Implementação:** Substituição do armazenamento em texto claro pelo método `werkzeug.security.generate_password_hash(senha, method="pbkdf2:sha256", salt_length=16)` e validação via `check_password_hash()`.
- **Efeito:** Caso o arquivo `database.db` seja vazado ou acessado indevidamente, as senhas originais dos usuários não podem ser revertidas, inviabilizando ataques por tabelas rainbow devido ao salt de 16 bytes e 1.000.000 iterações.

### 2.2 Isolamento de Segredos e Fail-Secure (WINDOL_SECRET_KEY)
- **Arquivo Modificado:** `web.py` e `.env.example`
- **Implementação:** Função `carregar_secret_key()` que busca o segredo exclusivamente em `os.environ["WINDOL_SECRET_KEY"]` ou arquivo `.env` local. Caso o segredo não seja encontrado em produção, a aplicação encerra imediatamente com `RuntimeError` (*Fail-Secure*).
- **Efeito:** Chaves criptográficas não são mais versionadas no GitHub e cookies de sessão possuem garantia de autenticidade criptográfica.

### 2.3 Hardening Operacional (debug=False e Tratamento Seguro de Erros)
- **Arquivo Modificado:** `web.py` e `templates/erro.html`
- **Implementação:** O servidor é executado com `app.run(debug=False)`. Foram implementados manipuladores globais para status HTTP 400, 403, 404 e 500 renderizando templates amigáveis genéricos, enquanto detalhes da exceção são registrados internamente na auditoria.
- **Efeito:** Mitiga CWE-489 e CWE-200. O atacante não recebe rastros de pilha (*stack traces*), versões de pacotes ou códigos-fonte ao forçar erros.

### 2.4 Controle de Acesso Mandatório por Decoradores (RBAC)
- **Arquivo Modificado:** `web.py`
- **Implementação:** Decoradores Python `@login_required` e `@perfil_required(*perfis_permitidos)`. Cada rota administrativa ou operacional valida expressamente os privilégios da sessão antes de qualquer acesso ao banco relacional.
- **Efeito:** Extinção de Broken Access Control (OWASP Top 10 A01). Usuários comuns são barrados ao tentar acessar rotas de suporte ou administrativas.

### 2.5 Validação de Titularidade e Prevenção contra BOLA/IDOR
- **Arquivo Modificado:** `web.py` e `templates/meus_chamados.html`
- **Implementação:** No endpoint `/deletar_chamado/<id>`, o backend consulta a propriedade do chamado e valida se o usuário autenticado coincide com o autor do chamado (`chamado['usuario'] == session['usuario']`).
- **Efeito:** Impede que um usuário autenticado exclua ou manipule chamados de terceiros alterando o ID na requisição.

### 2.6 Proteção contra Cross-Site Request Forgery (CSRF)
- **Arquivo Modificado:** `web.py`, `templates/*.html`
- **Implementação:** Middleware `@app.before_request` que gera um token aleatório seguro de 32 bytes (`secrets.token_hex(32)`) na sessão e valida a presença e igualdade do campo `csrf_token` em todas as requisições `POST`, `PUT` ou `DELETE`.
- **Efeito:** Rejeição de requisições maliciosas enviadas por sites externos em nome de usuários autenticados (HTTP 403).

### 2.7 Cabeçalhos Defensivos de Segurança (Security Headers)
- **Arquivo Modificado:** `web.py`
- **Implementação:** Middleware `@app.after_request` adicionando:
  * `X-Content-Type-Options: nosniff` (impede MIME-sniffing);
  * `X-Frame-Options: SAMEORIGIN` (mitiga Clickjacking);
  * `X-XSS-Protection: 1; mode=block` (filtro XSS de navegadores legados);
  * `Referrer-Policy: strict-origin-when-cross-origin`.
- **Efeito:** Defesa em profundidade no nível do protocolo HTTP.

### 2.8 Trilhas de Auditoria e Governança (logs_auditoria)
- **Arquivo Criado/Modificado:** `criar_banco.py`, `web.py` e `templates/auditoria.html`
- **Implementação:** Tabela dedicada no banco registrando data/hora, usuário ativo, ação executada, detalhes técnicos e endereço IP de origem. Painel restrito a administradores e gerentes em `/admin/auditoria`.
- **Efeito:** Rastreabilidade, não repúdio e conformidade com o princípio da Prestação de Contas (LGPD Art. 6º, X).
