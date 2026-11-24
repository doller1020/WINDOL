# Análise de Conformidade e Proteção de Dados (LGPD)

## 1. Introdução e Contexto Legal
A Lei nº 13.709, de 14 de agosto de 2018 (Lei Geral de Proteção de Dados Pessoais - LGPD), disciplina o tratamento de dados pessoais, inclusive nos meios digitais, com o objetivo de proteger os direitos fundamentais de liberdade e de privacidade e o livre desenvolvimento da personalidade da pessoa natural.

No âmbito de um sistema de Help Desk corporativo ou acadêmico, o processamento contínuo de dados funcionais, relatórios de suporte, logs de conexão e credenciais de acesso impõe deveres estritos de governança, segurança técnica e minimização.

## 2. Princípios do Artigo 6º Aplicados ao WINDOL

1. **Princípio da Finalidade (Art. 6º, I):**
   - O tratamento de dados no WINDOL possui propósitos legítimos, específicos e informados: registrar a solicitação, viabilizar o diagnóstico técnico pelo suporte de TI e comunicar a conclusão ao usuário solicitante.
   - Não há reutilização de dados para fins de marketing, traçado de perfil (*profiling*) ou comercialização com terceiros.

2. **Princípio da Adequação (Art. 6º, II):**
   - As informações solicitadas são estritamente compatíveis com as finalidades de atendimento técnico (identificador de usuário, descrição técnica do incidente e canal de comunicação).

3. **Princípio da Necessidade e Minimização (Art. 6º, III):**
   - O modelo de dados do WINDOL adotou a abordagem de *Privacy by Design*.
   - A tabela `colaboradores` contém apenas o login institucional, nome funcional sintético, departamento, e-mail corporativo e especialidade técnica.
   - Foram expressamente eliminados da base campos como CPF, RG, número de telefone pessoal, endereço domiciliar e fotografias pessoais.

4. **Princípio do Livre Acesso e Transparência (Art. 6º, IV e VI / Art. 9º):**
   - Disponibilização da rota pública `/privacidade` detalhando de forma clara e acessível quais dados são tratados, quais as finalidades, as bases legais e os prazos de retenção.
   - O solicitante pode consultar integralmente seus chamados na rota `/meus_chamados`.

5. **Princípio da Segurança e da Prevenção (Art. 6º, VII e VIII / Art. 46):**
   - **Criptografia em Repouso:** Hashes adaptativos PBKDF2:SHA-256 com salt individual de 16 bytes.
   - **Controle de Acesso Mandatório:** Interceptação no backend de todas as rotas operacionais.
   - **Proteção de Sessão:** Cookies com flags `HttpOnly` e `SameSite=Lax`, e chave secreta isolada em variáveis de ambiente.
   - **Proteção contra CSRF:** Tokens de sincronização em formulários de alteração de estado.

6. **Princípio da Responsabilização e Prestação de Contas (Art. 6º, X):**
   - Implementação da tabela `logs_auditoria`, registrando com precisão eventos de login bem-sucedido, falhas de autenticação, exclusão de dados e acessos negados por perfil (RBAC).

## 3. Bases Legais Enquadradas (Artigo 7º da LGPD)
O tratamento de dados pessoais no Sistema WINDOL enquadra-se nas seguintes hipóteses legais:
- **Art. 7º, V — Execução de Contrato ou Procedimentos Preliminares:** O tratamento é necessário para o cumprimento das obrigações internas de suporte e manutenção das ferramentas de trabalho/ensino disponibilizadas aos usuários.
- **Art. 7º, II — Cumprimento de Obrigação Legal ou Regulatória:** A manutenção de registros de conexão e de auditoria atende ao comando expresso do Art. 15 da Lei nº 12.965/2014 (Marco Civil da Internet).
- **Art. 7º, IX — Legítimo Interesse do Controlador:** Salvaguarda da segurança da informação da rede institucional e prevenção contra incidentes de segurança cibernética.

## 4. Racional de Utilização de Dados Sintéticos
Para a validação e demonstração das funcionalidades do sistema em ambiente acadêmico, foram utilizados exclusivamente **dados sintéticos** (dados fictícios gerados artificialmente para simulação operacional). Essa decisão garante a conformidade com a LGPD durante os testes, eliminando o risco de exposição de PII real de colaboradores ou alunos da instituição.
