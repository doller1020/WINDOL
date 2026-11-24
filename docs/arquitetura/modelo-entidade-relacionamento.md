# Modelo Entidade-Relacionamento (DER) e Estrutura de Dados

## 1. Descrição do Modelo de Dados
O banco de dados SQLite (`database.db`) foi modelado para suportar as operações essenciais do Help Desk, incorporando as diretrizes de **minimização de dados pessoais (LGPD Art. 6º, III)** e **trilhas de auditoria imutáveis (LGPD Art. 6º, X)**.

## 2. Diagrama Entidade-Relacionamento (Mermaid)

```mermaid
erDiagram
    USUARIOS {
        INTEGER id PK "Identificador único incremental"
        TEXT login UK "Login corporativo (único)"
        TEXT senha "Hash PBKDF2:SHA-256 com salt individual"
        TEXT tipo "Perfil RBAC (usuario, tecnico_n*, gerente, admin)"
        TEXT nome_completo "Nome profissional do usuário"
        TEXT email_corporativo "E-mail institucional (@windol.local)"
    }

    CHAMADOS {
        INTEGER id PK "Identificador único do chamado"
        TEXT titulo "Título sintético do incidente/solicitação"
        TEXT descricao "Descrição detalhada do problema"
        TEXT status "Estado operacional (aberto, em andamento, finalizado)"
        TEXT usuario "Login do solicitante (FK lógica para usuarios.login)"
        TEXT nivel "Nível técnico de atendimento (N1, N2, N3)"
        TEXT tecnico_responsavel "Login do técnico em atendimento"
        TEXT resposta_tecnica "Parecer técnico de encerramento"
        TEXT data_abertura "Data e hora de registro"
        TEXT data_atendimento "Data e hora de início do atendimento"
        TEXT data_finalizacao "Data e hora de conclusão"
        TEXT bloqueado_por "Controle de concorrência / lock de edição"
    }

    COLABORADORES {
        INTEGER id PK "Identificador do colaborador"
        TEXT usuario_login UK "Login funcional (FK lógica usuarios.login)"
        TEXT nome_completo "Nome funcional sintético"
        TEXT departamento "Área de atuação (Suporte, Redes, Gestão)"
        TEXT email_corporativo "E-mail corporativo minimizado"
        TEXT especialidade "Área técnica de competência"
        INTEGER status_ativo "Flag indicador de atividade (1 ativo, 0 inativo)"
    }

    LOGS_AUDITORIA {
        INTEGER id PK "Identificador sequencial do log"
        TEXT data_hora "Timestamp no fuso local (YYYY-MM-DD HH:MM:SS)"
        TEXT usuario "Identificador do agente (ou ANONIMO / SISTEMA)"
        TEXT acao "Identificador padronizado da ação de segurança"
        TEXT detalhes "Metadados técnicos e justificativa operacional"
        TEXT ip_origem "Endereço IP de origem da requisição"
    }

    USUARIOS ||--o{ CHAMADOS : "abre e acompanha"
    USUARIOS ||--o| COLABORADORES : "possui perfil profissional"
    USUARIOS ||--o{ LOGS_AUDITORIA : "gera eventos auditáveis"
```

## 3. Dicionário de Dados e Controles de Proteção

### Tabela `usuarios`
- Armazena credenciais e atributos de identidade funcional.
- A coluna `senha` armazena exclusivamente resumos criptográficos gerados com a função `werkzeug.security.generate_password_hash(method="pbkdf2:sha256", salt_length=16)`.
- Hashes possuem comprimento médio de 108 caracteres, inviabilizando ataques por dicionário ou tabelas rainbow.

### Tabela `colaboradores` (Módulo LGPD)
- Implementada sob o princípio de *Privacy by Design* e minimização.
- Armazena apenas dados públicos-profissionais e técnicos, sem acúmulo de dados sensíveis (sem CPF, RG, filiação, dados bancários ou domiciliares).
- Utilizada para alocação de chamados conforme a competência técnica.

### Tabela `logs_auditoria`
- Componente de governança e não repúdio.
- Permite a investigação de acessos não autorizados (`ACESSO_NEGADO_RBAC`), falhas de login (`LOGIN_FALHA`), criação/exclusão de usuários e manipulação de tickets.
