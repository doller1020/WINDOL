# Riscos Residuais e Limitações do Estudo

## 1. Princípio de Transparência Acadêmica
Nenhum sistema computacional pode ser declarado 100% invulnerável ou infalível. A engenharia de segurança de software preconiza a identificação honesta e o gerenciamento contínuo dos **riscos residuais** — vulnerabilidades remanescentes ou limitações arquiteturais que decorrem do escopo, da tecnologia adotada ou de restrições operacionais do projeto.

## 2. Inventário de Riscos Residuais e Limitações Conhecidas

### 2.1 Camada de Persistência Monolítica em Arquivo (SQLite)
- **Descrição:** O WINDOL utiliza o SQLite 3 como mecanismo de banco de dados relacional embutido.
- **Risco Residual:**
  * Embora eficiente para protótipos acadêmicos e pequenas operações, o SQLite opera com bloqueio de arquivo em nível de tabela (*table-level lock*) durante escritas concorrentes, o que limita a escalabilidade para centenas de acessos simultâneos.
  * O arquivo físico `database.db` reside no mesmo sistema de arquivos da aplicação, exigindo permissões estritas no nível do sistema operacional para evitar cópia direta do arquivo.
- **Plano de Tratamento Futuro:** Migração para um SGBD corporativo client-server (como PostgreSQL ou MariaDB) com suporte nativo a criptografia transparente em repouso (TDE - Transparent Data Encryption).

### 2.2 Autenticação de Fator Único (Single-Factor Authentication)
- **Descrição:** O sistema realiza a validação de identidade exclusivamente por combinação de login e senha forte criptografada.
- **Risco Residual:** Caso um usuário legítimo utilize uma senha previsível ou seja vítima de engenharia social (*phishing*), a sessão pode ser comprometida na ausência de um segundo fator.
- **Plano de Tratamento Futuro:** Implementação de Autenticação Multifator (MFA / 2FA) baseada no padrão aberto TOTP (RFC 6238 - Time-Based One-Time Password) para perfis administrativos e técnicos.

### 2.3 Ausência de Camada TLS Nativa no Servidor Embutido
- **Descrição:** O servidor de desenvolvimento do Flask atende nativamente sobre HTTP plano na porta 5000.
- **Risco Residual:** A execução em ambiente de produção sem um *Reverse Proxy* (como Nginx ou Apache) deixaria o tráfego sujeito a interceptação em rede local (*Man-in-the-Middle*).
- **Mitigação Recomendada:** Em ambiente de produção real, a aplicação deve ser executada atrás de um servidor web reverso com terminação TLS (HTTPS) utilizando certificados válidos (ex: Let's Encrypt), ativando a flag `SESSION_COOKIE_SECURE = True`.

### 2.4 Ausência de Rate Limiting e Bloqueio de IP por Força Bruta
- **Descrição:** Embora falhas de login sejam registradas na tabela `logs_auditoria`, o sistema não implementa bloqueio temporário de conta ou *backoff* exponencial após N tentativas consecutivas de senha incorreta.
- **Risco Residual:** Ataques automatizados de força bruta contra o endpoint `/` poderiam gerar sobrecarga de processamento criptográfico PBKDF2.
- **Plano de Tratamento Futuro:** Incorporação de biblioteca de limitação de taxa (como Flask-Limiter) suportada por Redis para limitar tentativas por endereço IP.

### 2.5 Automatização de Direitos do Titular LGPD (Art. 18)
- **Descrição:** Atualmente, solicitações de retificação, portabilidade ou exclusão de dados dependem de intervenção manual do Administrador no banco ou painel.
- **Risco Residual:** Demora operacional no atendimento caso o volume de solicitações de titulares aumente significativamente.
- **Plano de Tratamento Futuro:** Desenvolvimento de um módulo de autoatendimento para exportação e revogação de consentimento pelo próprio titular.
