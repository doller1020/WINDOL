# Especificação dos Casos de Teste Automatizados

## 1. Relação Completa dos 33 Casos de Teste

### Módulo 1: Autenticação e Credenciais (`tests/test_auth.py`)
1. **CT-AUT-01:** Login com credencial válida de usuário comum -> Redireciona para `/meus_chamados` com sessão inicializada.
2. **CT-AUT-02:** Login com credencial de administrador -> Redireciona para `/admin` com `tipo='admin'`.
3. **CT-AUT-03:** Login com senha incorreta -> Rejeita acesso com flash "Login ou senha inválidos", sem iniciar sessão.
4. **CT-AUT-04:** Login com usuário inexistente -> Rejeita sem vazar informação de que o usuário não existe.
5. **CT-AUT-05:** Inspeção física de senhas no banco -> Comprova que 100% dos registros utilizam PBKDF2:SHA-256 com salt individual de 16 bytes.
6. **CT-AUT-06:** Encerramento de sessão (Logout) -> Limpa completamente os dados da sessão e redireciona para login.
7. **CT-AUT-07:** Fluxo de troca de senha -> Atualiza o hash criptográfico no SQLite, invalidando a senha antiga.
8. **CT-AUT-08:** Validação de complexidade mínima de senha -> Rejeita senhas menores que 6 caracteres.

### Módulo 2: Controle de Acesso Baseado em Papéis (`tests/test_permissions.py`)
9. **CT-PERM-01:** Acesso anônimo à rota `/admin` -> Bloqueado com redirecionamento para login.
10. **CT-PERM-02:** Usuário comum tentando acessar `/admin` -> Bloqueado com mensagem de perfil não autorizado.
11. **CT-PERM-03:** Administrador acessando `/admin` -> Acesso autorizado e renderização correta do painel.
12. **CT-PERM-04:** Usuário comum tentando acessar `/chamados` -> Bloqueado com negação de privilégio.
13. **CT-PERM-05:** Técnico N1 acessando `/chamados` -> Acesso autorizado à fila técnica.
14. **CT-PERM-06:** Técnico tentando acessar `/gerente` -> Bloqueado; acesso liberado para perfil gerente.
15. **CT-PERM-07:** Consulta à trilha de auditoria `/admin/auditoria` -> Restrita exclusivamente a admin e gerente; usuário comum bloqueado.
16. **CT-PERM-08:** Gestão de catálogo de colaboradores `/admin/colaboradores` -> Exclusivo para administradores.

### Módulo 3: Ciclo de Vida de Chamados e IDOR (`tests/test_chamados.py`)
17. **CT-CHAM-01:** Abertura de chamado válido -> Persiste chamado com status "aberto", nível "N1" e autor logado.
18. **CT-CHAM-02:** Abertura de chamado com campos vazios -> Rejeitado com aviso de campos obrigatórios.
19. **CT-CHAM-03:** Filtragem de chamados em `/meus_chamados` -> Exibe apenas chamados do titular autenticado.
20. **CT-CHAM-04:** Atendimento técnico (/resolver) -> Técnico assume ticket, alterando status para "em andamento" e definindo lock de atendimento.
21. **CT-CHAM-05:** Escalonamento técnico (/encaminhar) -> Técnico N1 eleva chamado para nível N2 e libera lock.
22. **CT-CHAM-06:** Finalização de chamado (/finalizar) -> Grava parecer técnico, data de conclusão e status "finalizado".
23. **CT-CHAM-07:** Exclusão de chamado pelo próprio autor -> Chamado removido com sucesso do banco.
24. **CT-CHAM-08:** Prevenção de IDOR/BOLA -> Usuário A tenta excluir chamado do Usuário B; operação é bloqueada e chamado original é preservado intacto.

### Módulo 4: Segurança, LGPD, Injeção e Auditoria (`tests/test_security.py`)
25. **CT-SEC-01:** Tentativa de injeção SQL clássica (`' OR '1'='1`) no login -> Rejeitada e neutralizada pela parametrização.
26. **CT-SEC-02:** Injeção SQL no parâmetro de ordenação (`ordem=antigo; DROP TABLE...`) -> Neutralizada por lista permitida (*whitelist*).
27. **CT-SEC-03:** Requisição POST sem token CSRF -> Bloqueada com status HTTP 403 Forbidden.
28. **CT-SEC-04:** Requisição POST com token CSRF válido da sessão -> Aprovada e processada.
29. **CT-SEC-05:** Inspeção de Security Headers HTTP -> Presença mandatória de `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN` e `Referrer-Policy`.
30. **CT-SEC-06:** Verificação de desativação de modo debug -> Comprovação de que `debug=False` está ativo na inicialização.
31. **CT-SEC-07:** Resposta Fail-Secure para erro 404 -> Retorna template genérico amigável sem vazar paths ou stack traces.
32. **CT-SEC-08:** Geração de trilhas de auditoria -> Eventos de falha e sucesso de login registrados com precisão na tabela `logs_auditoria`.
33. **CT-SEC-09:** Minimização de dados LGPD na tabela `colaboradores` -> Comprova ausência de dados excessivos (sem CPF, RG, telefone pessoal, etc.).
