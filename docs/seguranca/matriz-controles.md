# Matriz de Requisitos e Controles de Segurança e Privacidade

## 1. Fundamentação Normativa
Esta matriz consolida os requisitos técnicos de segurança da informação e privacidade implementados no Sistema WINDOL, substituindo modelos proprietários ou fontes não verificáveis por padrões abertos e consagrados internacionalmente:
- **LGPD:** Lei nº 13.709/2018 (Artigos 6º, 9º, 18, 46 e 48);
- **OWASP ASVS:** Application Security Verification Standard v4.0.3 (Níveis de Verificação 1 e 2);
- **OWASP Top 10:2021:** Os 10 riscos mais críticos em aplicações web;
- **CIS Controls v8:** Center for Internet Security Critical Security Controls (Controles 3, 8 e 16);
- **NIST SSDF SP 800-218:** Secure Software Development Framework v1.1.

## 2. Matriz Consolidada de Controles

| ID | Categoria | Descrição do Requisito de Segurança | Referência Normativa Primária | Salvaguarda CIS Controls v8 | Critério Técnico de Verificação | Situação no WINDOL |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **RS-001** | **Identidade e Sessão** | Identificação unívoca do usuário com integridade de sessão criptográfica | OWASP ASVS V3.1 e V3.4 | CIS Control 16.4 | Sessão assinada via HMAC com chave de alta entropia | **Implementado e Aprovado** |
| **RS-002** | **Autenticação Mandatória** | Bloqueio mandatório de acessos não autenticados em rotas operacionais | OWASP ASVS V2.1 / OWASP Top 10 A01 | CIS Control 16.5 | Decorador `@login_required` interceptando requisições no backend | **Implementado e Aprovado** |
| **RS-003** | **Controle de Acesso (RBAC)** | Validação mandatória no backend de perfil autorizado por rota (Menor Privilégio) | OWASP ASVS V4.1 / OWASP Top 10 A01 | CIS Control 16.7 | Decorador `@perfil_required` bloqueando perfis não autorizados | **Implementado e Aprovado** |
| **RS-004** | **Criptografia de Senhas** | Armazenamento de credenciais via algoritmo de derivação adaptativo com salt | OWASP ASVS V2.4 / LGPD Art. 46 | CIS Control 3.11 | PBKDF2:SHA-256 com salt de 16 bytes e 1.000.000 iterações | **Implementado e Aprovado** |
| **RS-005** | **Gestão de Segredos** | Isolamento de chave secreta (`SECRET_KEY`) fora do código com Fail-Secure | OWASP ASVS V14.2 / NIST SSDF PW.1 | CIS Control 16.4 | Obtenção via `os.environ` ou `.env`; ausência impede inicialização | **Implementado e Aprovado** |
| **RS-006** | **Hardening Operacional** | Desativação de modo depuração em execução operacional (`debug=False`) | CWE-489 / OWASP Top 10 A05 | CIS Control 16.7 | Execução com `debug=False` e supressão de consoles interativos | **Implementado e Aprovado** |
| **RS-007** | **Tratamento de Erros** | Respostas de erro amigáveis sem exposição de stack traces ao cliente | CWE-200 / CWE-209 / ASVS V14.5 | CIS Control 16.8 | Manipuladores customizados para 400, 403, 404 e 500 (`erro.html`) | **Implementado e Aprovado** |
| **RS-008** | **Proteção contra CSRF** | Validação mandatória de token anti-CSRF sincronizado em requisições de estado | OWASP ASVS V4.2 / OWASP Top 10 A01 | CIS Control 16.10 | Middleware `@app.before_request` exigindo token CSRF em POSTs | **Implementado e Aprovado** |
| **RS-009** | **Defesa em Profundidade** | Cabeçalhos de segurança HTTP contra Clickjacking, Sniffing e Injeções | OWASP ASVS V14.4 / CIS Control 16 | CIS Control 16.3 | Headers `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection` | **Implementado e Aprovado** |
| **RS-010** | **Proteção contra IDOR** | Validação de titularidade de tickets na operação de exclusão (BOLA/IDOR) | OWASP ASVS V4.1 / OWASP Top 10 A01 | CIS Control 16.7 | Verificação de `chamado['usuario'] == session['usuario']` | **Implementado e Aprovado** |
| **RS-011** | **Minimização LGPD** | Coleta e armazenamento estritamente limitado ao necessário para a finalidade | LGPD Art. 6º, III (Necessidade) | CIS Control 3.1 | Tabela `colaboradores` com dados sintéticos profissionais (sem PII) | **Implementado e Aprovado** |
| **RS-012** | **Trilhas de Auditoria** | Registro persistente e imutável de eventos de autenticação e ações críticas | LGPD Art. 6º, X / OWASP ASVS V8 | CIS Control 8.2 | Tabela `logs_auditoria` com data/hora, usuário, ação, detalhes e IP | **Implementado e Aprovado** |
| **RS-013** | **Transparência Ativa** | Disponibilização de Aviso de Privacidade e direitos dos titulares | LGPD Art. 9º e Art. 18 | CIS Control 3 | Rota pública `/privacidade` detalhando finalidades e bases legais | **Implementado e Aprovado** |
