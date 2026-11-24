# Relatório Final de Auditoria, Segurança e Governança

## 1. Identificação do Projeto e Metadados
- **Título do Projeto:** Análise de Segurança e Proteção de Dados em um Sistema Help Desk Web
- **Sistema Avaliado:** WINDOL (Evolução do Sistema Help Desk Acadêmico)
- **Instituição:** União Pioneira de Integração Social – UPIS / FATEC
- **Curso:** Bacharelado em Sistemas de Informação
- **Autores:** Doller Felipe Macedo Costa & Wingrid da Costa Silva
- **Data da Conclusão dos Testes:** 23 de Novembro de 2026
- **Repositório Oficial:** [https://github.com/doller1020/WINDOL](https://github.com/doller1020/WINDOL)

## 2. Parecer Técnico Multidisciplinar

### Engenharia e Arquitetura de Software
A aplicação foi refatorada com êxito, eliminando acoplamentos inseguros e estabelecendo uma fronteira de confiança sólida no backend. Os decoradores de controle de acesso interceptam 100% das requisições para rotas operacionais e administrativas, desonerando a camada de interface da responsabilidade de segurança.

### Especialista em Segurança da Informação
Todas as vulnerabilidades críticas e de alta severidade diagnosticadas no sistema original (senhas em texto claro, segredos hardcoded, execução em debug e rotas desprotegidas) foram remediadas. As defesas em profundidade adicionadas (hashing PBKDF2 com salt de 16 bytes, tokens anti-CSRF, cabeçalhos HTTP defensivos e tratadores de erro genéricos) elevam a postura de segurança para conformidade com o padrão OWASP ASVS v4.0.3 e salvaguardas CIS Controls v8.

### Especialista em LGPD e Privacidade
O sistema incorpora o princípio do *Privacy by Design* e da Minimização de Dados (Art. 6º, III da LGPD). Não há coleta de dados excessivos, e o catálogo funcional de colaboradores é suportado por dados sintéticos para experimentação acadêmica. A rastreabilidade por meio de trilhas de auditoria contínuas atende ao princípio da Responsabilização e Prestação de Contas (Art. 6º, X), enquanto o Aviso de Privacidade garante transparência ativa aos titulares (Art. 9º).

### Engenharia de Testes (QA)
A suíte automatizada desenvolvida em `pytest` realizou a cobertura de 33 casos de teste cobrindo autenticação, permissões RBAC, integridade de chamados, injeção SQL, CSRF, security headers e auditoria. O índice de aprovação obtido foi de **100% (33 testes aprovados)**, sem regressões funcionais.

## 3. Conclusão da Auditoria
Emite-se parecer conclusivo de **APROVAÇÃO TÉCNICA E CONFORMIDADE NORMATIVA**, atestando que o Sistema WINDOL encontra-se seguro, documentado, testado e pronto para entrega e publicação oficial.
