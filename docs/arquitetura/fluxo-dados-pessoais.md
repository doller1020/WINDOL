# Fluxo de Tratamento de Dados Pessoais (LGPD)

## 1. Contexto e Enquadramento Legal
O tratamento de dados pessoais no Sistema WINDOL foi estruturado para atender aos requisitos da **Lei nº 13.709/2018 (LGPD)**, com ênfase nos seguintes princípios fundamentais do Artigo 6º:
- **Finalidade (Art. 6º, I):** Tratamento restrito à triagem, resolução de chamados de TI e segurança do ambiente corporativo.
- **Necessidade / Minimização (Art. 6º, III):** Coleta estritamente limitada ao indispensável para a prestação do serviço.
- **Segurança e Prevenção (Art. 6º, VII e VIII):** Salvaguardas criptográficas e controle de acesso para prevenir acessos não autorizados.
- **Responsabilização e Prestação de Contas (Art. 6º, X):** Trilhas de auditoria contínuas para comprovar a eficácia das medidas protetivas.

## 2. Diagrama do Fluxo de Dados e Ciclo de Vida (Mermaid)

```mermaid
flowchart TD
    subgraph Coleta["1. Coleta e Entrada de Dados"]
        InUser["Usuário Solicitante abre chamado<br>(Login, Título, Descrição do Incidente)"]
        InAdmin["Administrador cadastra usuário<br>(Login, Nome Funcional, E-mail Corporativo)"]
        FiltroMinimizacao["Filtro de Minimização:<br>Rejeita dados excessivos (sem CPF/RG/endereço)"]
    end

    subgraph Armazenamento["2. Processamento e Armazenamento Protegido"]
        HashPass["Derivação PBKDF2/SHA-256 com Salt<br>(Armazena apenas digest criptográfico)"]
        DBUsuarios["Tabela 'usuarios' (Dados Minimizados)"]
        DBChamados["Tabela 'chamados' (Histórico Operacional)"]
        DBColab["Tabela 'colaboradores' (Dados Sintéticos)"]
    end

    subgraph Acesso["3. Acesso e Uso Conforme Perfil (RBAC)"]
        VisaoUser["Solicitante: Acessa apenas seus próprios chamados"]
        VisaoTec["Técnico: Acessa fila do seu nível (N1, N2 ou N3)"]
        VisaoGer["Gerente: Acessa relatórios estatísticos finalizados"]
        VisaoAdm["Admin: Gestão de acessos e auditoria"]
    end

    subgraph Governanca["4. Auditoria e Direitos do Titular (Art. 18)"]
        TrilhaAudit["Tabela 'logs_auditoria':<br>Registro pericial de acessos e operações"]
        AvisoPrivacidade["Aviso de Privacidade (/privacidade):<br>Transparência ativa sobre o tratamento"]
    end

    InUser --> FiltroMinimizacao
    InAdmin --> FiltroMinimizacao
    FiltroMinimizacao --> HashPass
    HashPass --> DBUsuarios
    FiltroMinimizacao --> DBChamados
    FiltroMinimizacao --> DBColab

    DBChamados --> VisaoUser
    DBChamados --> VisaoTec
    DBChamados --> VisaoGer
    DBUsuarios --> VisaoAdm
    DBColab --> VisaoAdm

    VisaoUser -.->|Gera Registro de Acesso| TrilhaAudit
    VisaoTec -.->|Gera Registro de Atendimento| TrilhaAudit
    VisaoAdm -.->|Gera Registro Administrativo| TrilhaAudit
```

## 3. Matriz de Tratamento de Dados por Categoria

| Dado Pessoal Tratado | Categoria do Dado | Base Legal (Art. 7º) | Princípio da Minimização | Medida de Segurança Aplicada |
| :--- | :--- | :--- | :--- | :--- |
| **Login do Usuário** | Dado Cadastral Comum | Execução de Contrato (Inciso V) | Coleta indispensável para identificação unívoca | Indexação com chave única (`UNIQUE`), validação de sessão |
| **Senha de Acesso** | Credencial de Segurança | Execução de Contrato (Inciso V) | Nunca armazenada em texto claro | Hash irreversível PBKDF2:SHA-256 com salt de 16 bytes |
| **Nome Completo** | Dado Cadastral Comum | Legítimo Interesse (Inciso IX) | Limitado ao nome profissional/funcional | Exibição restrita na interface por perfil |
| **E-mail Corporativo** | Dado de Contato | Execução de Contrato (Inciso V) | Apenas domínio corporativo (`@windol.local`) | Sem exposição pública na aplicação |
| **Histórico de Chamados** | Dado Operacional | Execução de Contrato (Inciso V) | Apenas descrições de falhas de hardware/software | Isolamento via SQL parametrizado por solicitante |
| **Endereço IP e Data/Hora** | Registro de Conexão | Cumprimento de Obrigação Legal (Marco Civil, Art. 15) | Coleta automática de metadados de auditoria | Tabela `logs_auditoria` acessível apenas a admin/gerente |
