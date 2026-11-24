"""
Testes Automatizados - Módulo de Autenticação e Gestão de Credenciais (OWASP ASVS V2).
Valida: Login válido, inválido, hashing seguro, integridade de sessão e troca de senha.
"""

import sqlite3
from werkzeug.security import check_password_hash


def test_login_valido_usuario(client, test_db):
    """CT-AUT-01: Validar autenticação com credencial legítima e redirecionamento correto."""
    response = client.post("/", data={"usuario": "usuario1", "senha": "senha123"}, follow_redirects=False)
    assert response.status_code == 302
    assert "/meus_chamados" in response.headers["Location"]

    with client.session_transaction() as sess:
        assert sess.get("usuario") == "usuario1"
        assert sess.get("tipo") == "usuario"


def test_login_valido_admin(client, test_db):
    """CT-AUT-02: Validar autenticação do administrador e redirecionamento para /admin."""
    response = client.post("/", data={"usuario": "admin", "senha": "admin123"}, follow_redirects=False)
    assert response.status_code == 302
    assert "/admin" in response.headers["Location"]

    with client.session_transaction() as sess:
        assert sess.get("usuario") == "admin"
        assert sess.get("tipo") == "admin"


def test_login_invalido_senha_incorreta(client, test_db):
    """CT-AUT-03: Validar que senha incorreta rejeita acesso e não inicializa sessão."""
    response = client.post("/", data={"usuario": "usuario1", "senha": "senha_errada_999"}, follow_redirects=True)
    assert response.status_code == 200
    assert "Login ou senha inválidos" in response.get_data(as_text=True)

    with client.session_transaction() as sess:
        assert "usuario" not in sess


def test_login_invalido_usuario_inexistente(client, test_db):
    """CT-AUT-04: Validar que usuário não cadastrado é rejeitado."""
    response = client.post("/", data={"usuario": "usuario_fantasma", "senha": "qualquer_senha"}, follow_redirects=True)
    assert response.status_code == 200
    assert "Login ou senha inválidos" in response.get_data(as_text=True)


def test_armazenamento_seguro_senhas(test_db):
    """CT-AUT-05: Comprovar que nenhuma senha está em texto puro no banco de dados (ASVS V2)."""
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT login, senha FROM usuarios")
    registros = cur.fetchall()
    conn.close()

    assert len(registros) > 0
    for login, senha in registros:
        assert not senha.startswith("123")
        assert senha.startswith("pbkdf2:sha256:")
        assert len(senha) > 50  # Hash adaptativo longo com salt


def test_logout_encerra_sessao(client, test_db):
    """CT-AUT-06: Validar que logout limpa todas as variáveis de sessão."""
    client.post("/", data={"usuario": "usuario1", "senha": "senha123"})
    
    with client.session_transaction() as sess:
        assert "usuario" in sess

    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert "/" in response.headers["Location"]

    with client.session_transaction() as sess:
        assert "usuario" not in sess
        assert "tipo" not in sess


def test_alterar_senha_sucesso(client, test_db):
    """CT-AUT-07: Validar fluxo seguro de alteração de senha com atualização do hash."""
    # Login prévio
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario1"
        sess["tipo"] = "usuario"

    response = client.post(
        "/alterar_senha",
        data={"nova_senha": "NovaSenhaForte@2026", "confirma_senha": "NovaSenhaForte@2026"},
        follow_redirects=False
    )
    assert response.status_code == 302

    # Verificar novo hash no banco
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT senha FROM usuarios WHERE login='usuario1'")
    novo_hash = cur.fetchone()[0]
    conn.close()

    assert check_password_hash(novo_hash, "NovaSenhaForte@2026")
    assert not check_password_hash(novo_hash, "senha123")


def test_alterar_senha_rejeita_curta(client, test_db):
    """CT-AUT-08: Validar que senhas menores que 6 caracteres são rejeitadas."""
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario1"
        sess["tipo"] = "usuario"

    response = client.post(
        "/alterar_senha",
        data={"nova_senha": "123", "confirma_senha": "123"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert "no mínimo 6 caracteres" in response.get_data(as_text=True)
