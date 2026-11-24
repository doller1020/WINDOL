"""
Testes Automatizados - Segurança da Aplicação, LGPD, Injeção, CSRF, Headers e Auditoria.
Valida: Tentativas de SQLi, proteção CSRF, Security Headers, desativação de debug, tratamento fail-secure de erro 404/500, trilhas de auditoria e minimização LGPD.
"""

import sqlite3
from web import app


def test_sql_injection_login_bloqueado(client, test_db):
    """CT-SEC-01: Tentativa clássica de SQL Injection no login (' OR '1'='1) deve ser neutralizada."""
    payload = "' OR '1'='1"
    response = client.post("/", data={"usuario": payload, "senha": "qualquer_coisa"}, follow_redirects=True)
    assert response.status_code == 200
    assert "Login ou senha inválidos" in response.get_data(as_text=True)

    with client.session_transaction() as sess:
        assert "usuario" not in sess


def test_sql_injection_filtro_chamados_neutralizado(client, test_db):
    """CT-SEC-02: Parâmetro 'ordem' malicioso com SQL Injection na rota /meus_chamados."""
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario1"
        sess["tipo"] = "usuario"

    payload = "antigo; DROP TABLE chamados; --"
    response = client.get(f"/meus_chamados?ordem={payload}", follow_redirects=False)
    assert response.status_code == 200

    # Comprovar que a tabela chamados segue existindo e intacta
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM chamados")
    cnt = cur.fetchone()[0]
    conn.close()
    assert cnt > 0


def test_csrf_bloqueia_requisicao_sem_token(test_db):
    """CT-SEC-03: Garantir que POST sem token CSRF válido seja rejeitado com HTTP 403."""
    app.config["TESTING_CSRF_DISABLED"] = False
    app.config["DATABASE_PATH"] = test_db

    with app.test_client() as c:
        # Acessa GET para inicializar sessão e cookies
        c.get("/")
        # Dispara POST sem csrf_token no body
        response = c.post("/", data={"usuario": "admin", "senha": "admin123"}, follow_redirects=False)
        assert response.status_code == 403
        assert "falha na validação CSRF" in response.get_data(as_text=True)

    app.config["TESTING_CSRF_DISABLED"] = True


def test_csrf_permite_requisicao_com_token_valido(test_db):
    """CT-SEC-04: Garantir que POST com token CSRF legítimo da sessão é aceito."""
    app.config["TESTING_CSRF_DISABLED"] = False
    app.config["DATABASE_PATH"] = test_db

    with app.test_client() as c:
        c.get("/")
        with c.session_transaction() as sess:
            token = sess["csrf_token"]

        response = c.post("/", data={"usuario": "admin", "senha": "admin123", "csrf_token": token}, follow_redirects=False)
        assert response.status_code == 302
        assert "/admin" in response.headers["Location"]

    app.config["TESTING_CSRF_DISABLED"] = True


def test_security_headers_presentes(client):
    """CT-SEC-05: Validar cabeçalhos HTTP defensivos (MIME Sniffing, Clickjacking, XSS)."""
    response = client.get("/")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert "1; mode=block" in response.headers.get("X-XSS-Protection", "")
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_debug_mode_desativado():
    """CT-SEC-06: Mitigação CWE-489 - Garantir que o app Flask não execute com debug=True em produção."""
    # O arquivo web.py define explicitamente app.run(debug=False)
    with open("web.py", "r", encoding="utf-8") as f:
        conteudo = f.read()
    assert "app.run(debug=False" in conteudo
    assert "app.run(debug=True" not in conteudo


def test_fail_secure_erro_404_sem_stacktrace(client):
    """CT-SEC-07: Mitigação CWE-200 - Rota inexistente deve renderizar erro amigável sem vazar paths."""
    response = client.get("/rota-inexistente-que-nao-existe-12345")
    assert response.status_code == 404
    html = response.get_data(as_text=True)
    assert "Recurso ou página não encontrada" in html
    assert "Traceback" not in html
    assert "Werkzeug" not in html


def test_registro_auditoria_eventos_criticos(client, test_db):
    """CT-SEC-08: Rastreabilidade (LGPD Art. 6º, X e CIS 8) - Ações críticas devem persistir log."""
    # 1. Login com falha
    client.post("/", data={"usuario": "invasor", "senha": "senha_errada"})

    # 2. Login com sucesso
    client.post("/", data={"usuario": "admin", "senha": "admin123"})

    # 3. Consulta ao banco de auditoria
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT acao, usuario FROM logs_auditoria ORDER BY id DESC")
    logs = cur.fetchall()
    conn.close()

    acoes = [l[0] for l in logs]
    assert "LOGIN_FALHA" in acoes
    assert "LOGIN_SUCESSO" in acoes


def test_minimizacao_dados_colaboradores_lgpd(test_db):
    """CT-SEC-09: Princípio da Minimização e Necessidade (LGPD Art. 6º, III)."""
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(colaboradores)")
    colunas = [c[1] for c in cur.fetchall()]
    conn.close()

    # Campos funcionais permitidos
    assert "usuario_login" in colunas
    assert "nome_completo" in colunas
    assert "email_corporativo" in colunas
    assert "departamento" in colunas

    # Campos excessivos / PII sensível que NÃO DEVEM existir
    assert "cpf" not in colunas
    assert "rg" not in colunas
    assert "telefone_pessoal" not in colunas
    assert "endereco_residencial" not in colunas
    assert "dados_bancarios" not in colunas
