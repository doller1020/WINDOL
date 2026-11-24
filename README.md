# WINDOL — Sistema Help Desk Seguro & Governança LGPD

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask%203.x-green.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/pytest-33%2F33%20passed%20(100%25)-brightgreen.svg)]()
[![Security Standards](https://img.shields.io/badge/OWASP-ASVS%20v4.0.3%20%7C%20Top%2010-orange.svg)](https://owasp.org/)
[![Compliance](https://img.shields.io/badge/compliance-LGPD%20(Lei%2013.709%2F2018)-blue.svg)](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
[![Status](https://img.shields.io/badge/release-Go%20(Aprovado)-success.svg)]()

> **Trabalho de Conclusão de Curso (TCC) — Bacharelado em Sistemas de Informação**  
> **Instituição:** União Pioneira de Integração Social – UPIS / FATEC  
> **Autores:** Doller Felipe Macedo Costa & Wingrid da Costa Silva  
> **Orientador:** Prof. Me. Cleber Mitchell  
> **Repositório Original (Legado):** [doller1020/sistema-chamados-faculdade](https://github.com/doller1020/sistema-chamados-faculdade)  
> **Repositório Oficial Atualizado:** [doller1020/WINDOL](https://github.com/doller1020/WINDOL)  

---

## 1. Apresentação do WINDOL
O **WINDOL** é um sistema web corporativo de Help Desk e Service Desk voltado à centralização, triagem, atendimento e rastreamento de incidentes e solicitações de tecnologia da informação. 

Desenvolvido originalmente como um protótipo acadêmico funcional, o sistema foi submetido a uma rigorosa auditoria de segurança da informação e privacidade, culminando em uma evolução arquitetural fundamentada no paradigma do ***Security and Privacy by Design***. O projeto demonstra na prática como refatorações de código e salvaguardas direcionadas elevam a maturidade de segurança e a conformidade legal com a **LGPD (Lei nº 13.709/2018)** sem demandar a reescrita integral de sistemas legados.

---

## 2. Tecnologias Utilizadas
- **Linguagem:** Python 3.10+ (validado no Python 3.14)
- **Framework Web:** Flask 3.x
- **Camada Criptográfica:** Werkzeug Security (PBKDF2-HMAC-SHA256, 1.000.000 iterações, salt individual de 16 bytes)
- **Persistência Relacional:** SQLite 3 (consultas 100% parametrizadas)
- **Framework de Testes:** pytest 9.x (com fixtures isoladas em tempo de execução)
- **Ciência de Dados & Gráficos:** Matplotlib 3.x
- **Frontend:** HTML5 semântico, CSS3 responsivo (Dark Mode corporativo) e templates Jinja2

---

## 3. Funcionalidades do Sistema por Perfil (RBAC)

O WINDOL adota **Controle de Acesso Baseado em Papéis (RBAC)** rigorosamente validado no servidor (*backend*):

| Perfil Funcional | Funcionalidades Autorizadas |
| :--- | :--- |
| **Usuário Solicitante (`usuario`)** | Abertura de chamados, visualização filtrada de seus próprios chamados (`/meus_chamados`), cancelamento de chamados de sua autoria e alteração de senha pessoal. |
| **Técnico Nível 1 (`tecnico_n1`)** | Triagem da fila N1, assunção de tickets em atendimento, finalização com parecer técnico e escalonamento para Nível 2. |
| **Técnico Nível 2 (`tecnico_n2`)** | Atendimento especializado de redes e servidores (N2), resolução de incidentes e escalonamento para Nível 3. |
| **Técnico Nível 3 (`tecnico_n3`)** | Resolução de incidentes críticos, problemas de arquitetura e sistemas (N3). |
| **Gerente de Operações (`gerente`)** | Visão analítica de chamados finalizados (`/gerente`), acompanhamento de SLAs operacionais e consulta à trilha de auditoria (`/admin/auditoria`). |
| **Administrador (`admin`)** | Gestão de contas de usuários (criação, edição e exclusão segura), catálogo funcional de colaboradores minimizado (LGPD), trilhas de auditoria globais e gestão integral de tickets. |

---

## 4. Arquitetura do Sistema e Defesas em Profundidade

```
[Navegador do Usuário]
         │
         ▼  (HTTPS / Cookie HttpOnly & SameSite=Lax)
[Middleware de Segurança HTTP]
  ├── Security Headers (X-Frame-Options, X-Content-Type, X-XSS-Protection)
  └── Validador Mandatório anti-CSRF (@before_request)
         │
         ▼
[Camada de Aplicação Flask - web.py]
  ├── Fail-Secure: os.environ.get('WINDOL_SECRET_KEY')
  ├── Hardening Operacional: debug = False (CWE-489 mitigado)
  ├── Decoradores de Autorização RBAC (@login_required / @perfil_required)
  ├── Autenticação Criptográfica: check_password_hash (PBKDF2/SHA-256)
  └── Error Handlers Genéricos: 400, 403, 404 e 500 sem vazamento de stacktrace
         │
         ▼  (Consultas 100% Parametrizadas contra SQL Injection)
[Banco de Dados SQLite - database.db]
  ├── usuarios (senhas com hashes PBKDF2 irreversíveis)
  ├── chamados (validação de titularidade / mitigação IDOR)
  ├── colaboradores (dados sintéticos profissionais - Minimização LGPD)
  └── logs_auditoria (rastreabilidade e prestação de contas - LGPD Art. 6º, X)
```

---

## 5. Medidas de Segurança Implementadas

1. **Criptografia Adaptativa de Senhas (OWASP ASVS V2 e LGPD Art. 46):** Senhas nunca são salvas em texto claro. Utiliza-se PBKDF2:SHA-256 com salt de 16 bytes, inviabilizando ataques por dicionário ou tabelas rainbow.
2. **Isolamento de Segredos (CIS Control 16.4):** Chave de sessão isolada em variáveis de ambiente, com política de *Fail-Secure* que bloqueia a inicialização caso o segredo não esteja definido.
3. **Controle de Acesso Mandatório (OWASP Top 10 A01 - Broken Access Control):** Interceptação mandatória no backend de cada rota sensível por decoradores Python.
4. **Proteção contra Cross-Site Request Forgery (CSRF):** Tokens únicos por sessão validados obrigatoriamente em todos os métodos que alteram estado (`POST`, `PUT`, `DELETE`).
5. **Mitigação de IDOR/BOLA (OWASP Top 10 A01):** Validação estrita de propriedade na exclusão de chamados (`chamado['usuario'] == session['usuario']`).
6. **Hardening e Resposta Segura a Erros (CWE-489 e CWE-200):** Execução com `debug=False` e substituição de mensagens técnicas por telas amigáveis genéricas (`erro.html`).
7. **Minimização de Dados (LGPD Art. 6º, III):** Catálogo de colaboradores composto por dados estritamente profissionais (sem CPF, RG ou dados pessoais sensíveis).
8. **Trilhas de Auditoria (LGPD Art. 6º, X / CIS Control 8):** Persistência automática de tentativas de login, acessos negados e operações administrativas para auditoria forense.

---

## 6. Estrutura de Diretórios do Repositório

```
WINDOL/
├── .env.example                     # Exemplo de configuração de variáveis de ambiente
├── .gitignore                       # Proteção contra commit de segredos (.env) e caches
├── requirements.txt                 # Dependências do projeto (Flask, Werkzeug, pytest, matplotlib)
├── README.md                        # Documentação principal do projeto
├── web.py                           # Aplicação web principal segura
├── criar_banco.py                   # Script de migração e inicialização do banco seguro
├── database.db                      # Banco SQLite relacional seguro
├── generate_charts.py               # Script automatizado de geração de gráficos estatísticos
│
├── static/                          # Folhas de estilo e recursos estáticos
│   └── style.css                    # Estilo corporativo responsivo (Dark Mode)
│
├── templates/                       # Templates Jinja2 com proteção CSRF
│   ├── abrir_chamado.html           # Abertura de novos chamados
│   ├── admin.html                   # Painel administrativo
│   ├── alterar_senha.html           # Troca de senha criptografada
│   ├── auditoria.html               # Painel de trilhas de auditoria
│   ├── colaboradores.html           # Catálogo de colaboradores minimizado (LGPD)
│   ├── editar_usuario.html          # Edição segura de dados cadastrais
│   ├── erro.html                    # Tratador genérico de erros HTTP (400, 403, 404, 500)
│   ├── gerente.html                 # Painel da gerência operacional
│   ├── listar_chamados.html         # Fila de atendimento técnico por nível
│   ├── login.html                   # Tela de login com link para privacidade
│   ├── mensagem.html                # Notificações de confirmação
│   ├── meus_chamados.html           # Painel do solicitante
│   ├── painel_resolver.html         # Atendimento técnico e escalonamento
│   ├── privacidade.html             # Aviso de Privacidade e direitos LGPD
│   └── usuarios.html                # Gestão administrativa de usuários
│
├── tests/                           # Suíte de testes automatizados com pytest
│   ├── conftest.py                  # Fixtures com banco SQLite isolado e dados de teste
│   ├── test_auth.py                 # Testes de autenticação, hashing e senhas (8 testes)
│   ├── test_permissions.py          # Testes de controle de acesso RBAC (8 testes)
│   ├── test_chamados.py             # Testes de ciclo de vida e IDOR (8 testes)
│   └── test_security.py             # Testes de SQLi, CSRF, Headers e LGPD (9 testes)
│
└── docs/                            # Documentação técnica e acadêmica do TCC
    ├── arquitetura/                 # Diagramas de arquitetura e fluxos
    │   ├── arquitetura-original.md
    │   ├── arquitetura-atual.md
    │   ├── fluxo-autenticacao.md
    │   ├── controle-acesso-rbac.md
    │   ├── modelo-entidade-relacionamento.md
    │   └── fluxo-dados-pessoais.md
    ├── seguranca/                   # Diagnósticos e matrizes normativas
    │   ├── diagnostico-vulnerabilidades.md
    │   ├── matriz-controles.md
    │   ├── analise-lgpd.md
    │   ├── melhorias-implementadas.md
    │   └── riscos-residuais.md
    ├── testes/                      # Planos e relatórios de execução de QA
    │   ├── plano-de-testes.md
    │   ├── casos-de-teste.md
    │   ├── resultados-dos-testes.md
    │   └── evidencias/
    │       └── pytest_output.txt
    ├── relatorios/                  # Relatórios gerenciais e comparativos
    │   ├── comparativo-antes-depois.md
    │   └── relatorio-auditoria.md
    └── graficos/                    # Gráficos em alta resolução e dados de origem
        ├── dados_controles_antes_depois.csv
        ├── dados_vulnerabilidades_severidade.csv
        ├── dados_resultados_testes.csv
        ├── dados_conformidade_lgpd.csv
        ├── grafico_1_controles_antes_depois.png
        ├── grafico_2_vulnerabilidades_severidade.png
        ├── grafico_3_resultados_testes.png
        └── grafico_4_conformidade_lgpd.png
```

---

## 7. Instruções de Instalação e Execução

### Pré-requisitos
- Python 3.10 ou superior
- Git instalado

### Passo a Passo

1. **Clonar o Repositório:**
   ```bash
   git clone https://github.com/doller1020/WINDOL.git
   cd WINDOL
   ```

2. **Criar e Ativar o Ambiente Virtual:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar as Variáveis de Ambiente:**
   Crie o arquivo `.env` na raiz do projeto com base no `.env.example`:
   ```bash
   # No Windows (PowerShell)
   Copy-Item .env.example .env

   # No Linux / macOS
   cp .env.example .env
   ```
   *Edite o arquivo `.env` e configure uma chave segura de 32 bytes para `WINDOL_SECRET_KEY`.*

5. **Inicializar o Banco de Dados Seguro:**
   ```bash
   python criar_banco.py
   ```

6. **Executar a Aplicação:**
   ```bash
   python web.py
   ```
   *Acesse no navegador: `http://127.0.0.1:5000`*

### Credenciais Padrão Pré-cadastradas:

| Perfil | Usuário | Senha Padrão | Finalidade |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | Acesso integral, gestão de usuários e auditoria |
| **Solicitante** | `wingrid` | `senha123` | Abertura e acompanhamento de chamados |
| **Solicitante** | `doller` | `senha123` | Abertura e acompanhamento de chamados |
| **Técnico N1** | `tecnico1` | `senha123` | Triagem e suporte geral N1 |
| **Técnico N2** | `tecnico2` | `senha123` | Suporte a infraestrutura e redes N2 |
| **Técnico N3** | `tecnico3` | `senha123` | Especialista em sistemas e segurança N3 |
| **Gerente** | `gerente` | `senha123` | Relatórios operacionais e auditoria |

---

## 8. Como Executar os Testes Automatizados

A suíte de testes utiliza o framework `pytest` em uma base SQLite isolada em memória temporária:

```bash
# Execução simples com resumo
pytest

# Execução detalhada (verbose)
pytest -v

# Execução com relatório de cobertura por módulo
pytest tests/test_auth.py -v
pytest tests/test_permissions.py -v
pytest tests/test_chamados.py -v
pytest tests/test_security.py -v
```

**Resultado Obtido:** **33 testes executados / 33 aprovados (100% de taxa de sucesso)**.

---

## 9. Limitações Conhecidas e Trabalhos Futuros
- **Banco de Dados Monolítico:** A utilização do SQLite embutido atende a fins acadêmicos e pequenas equipes, mas recomenda-se a migração para PostgreSQL com criptografia transparente (TDE) para ambientes com alta concorrência de escritas.
- **Autenticação de Fator Único:** Recomenda-se a futura implementação de autenticação multifator baseada em TOTP (RFC 6238) para contas administrativas.
- **Ambiente de Produção:** O servidor embutido do Flask deve ser executado atrás de um proxy reverso (Nginx/Apache) com terminação TLS (HTTPS obrigatório).

---

## 10. Licença e Autores
Projeto acadêmico desenvolvido por **Doller Felipe Macedo Costa** e **Wingrid da Costa Silva** sob a orientação do **Prof. Me. Cleber Mitchell** no curso de Sistemas de Informação da **UPIS (2026)**. Disponibilizado para fins educacionais e de portfólio profissional de engenharia de software e cibersegurança.
