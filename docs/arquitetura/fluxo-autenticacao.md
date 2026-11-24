# Fluxo de Autenticação Segura e Gestão de Sessões

## 1. Descrição do Processo
O processo de autenticação do Sistema WINDOL implementa derivação criptográfica adaptativa de chaves (PBKDF2-HMAC-SHA256), proteção contra ataques de força bruta com registro de auditoria, emissão de cookies de sessão assinados com segredo de alta entropia e isolamento de privilégios.

## 2. Diagrama de Sequência de Autenticação (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor Usuario as Usuário / Navegador
    participant Web as Aplicação Flask (web.py)
    participant CSRF as Filtro CSRF
    participant DB as Banco SQLite (database.db)
    participant Audit as Trilha de Auditoria (logs_auditoria)

    Usuario->>Web: GET / (Acessa tela de login)
    Web->>Usuario: Retorna formulário com Token CSRF de sessão
    
    Usuario->>Web: POST / com {usuario, senha, csrf_token}
    Web->>CSRF: Valida conformidade do token CSRF
    alt Token CSRF Inválido ou Ausente
        CSRF-->>Usuario: HTTP 403 Forbidden (Falha CSRF registrada)
        CSRF->>Audit: Registra evento 'FALHA_CSRF'
    else Token Válido
        Web->>DB: SELECT * FROM usuarios WHERE login = ? (Parametrizado)
        DB-->>Web: Retorna dados do usuário (incluindo hash PBKDF2)
        
        alt Usuário Inexistente ou Senha Incorreta
            Web->>Audit: Registra 'LOGIN_FALHA' (IP, usuário tentado, timestamp)
            Web-->>Usuario: Flash 'Login ou senha inválidos' (Sem indicar qual campo falhou)
        else Credencial Válida (check_password_hash == True)
            Web->>Web: Inicializa session['usuario'], session['tipo'], session['csrf_token']
            Web->>Audit: Registra 'LOGIN_SUCESSO' com perfil funcional
            alt Perfil = 'usuario'
                Web-->>Usuario: HTTP 302 Redirect para /meus_chamados
            else Perfil = 'tecnico_n1' / 'tecnico_n2' / 'tecnico_n3'
                Web-->>Usuario: HTTP 302 Redirect para /chamados
            else Perfil = 'admin'
                Web-->>Usuario: HTTP 302 Redirect para /admin
            else Perfil = 'gerente'
                Web-->>Usuario: HTTP 302 Redirect para /gerente
            end
        end
    end
```

## 3. Critérios Criptográficos e de Segurança da Sessão
- **Algoritmo:** PBKDF2 com HMAC-SHA256 (Password-Based Key Derivation Function 2);
- **Salt:** 16 bytes pseudo-aleatórios gerados por `os.urandom()` via Werkzeug para cada credencial, garantindo que hashes de senhas idênticas sejam completamente distintos no banco;
- **Iterações:** Padrão Werkzeug 3.x (1.000.000 iterações), oferecendo alta resistência a ataques de força bruta acelerados por GPU;
- **Assinatura de Sessão:** Chave HMAC de 256 bits (`WINDOL_SECRET_KEY`) gerada com entropia criptográfica;
- **Mitigação de Enumeração de Contas:** Em caso de credencial incorreta, o sistema retorna uma mensagem genérica (*"Login ou senha inválidos!"*), sem informar se o erro foi no identificador ou na senha.
