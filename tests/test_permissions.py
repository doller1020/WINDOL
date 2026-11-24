"""
Testes Automatizados - Controle de Acesso Baseado em Papéis / RBAC (OWASP Top 10 A01 / ASVS V4).
Valida: Bloqueio de anônimos, bloqueio de perfis sem privilégio, e acessos legítimos.
"""

def test_rota_admin_bloqueia_anonimo(client):
    """CT-PERM-01: Validar que usuário anônimo é impedido de acessar /admin."""
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 302
    assert "/" in response.headers["Location"]


def test_rota_admin_bloqueia_usuario_comum(client):
    """CT-PERM-02: Validar que usuário comum não consegue acessar o painel do administrador."""
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario1"
        sess["tipo"] = "usuario"

    response = client.get("/admin", follow_redirects=True)
    assert response.status_code == 200
    assert "Acesso não autorizado para o seu perfil funcional" in response.get_data(as_text=True)


def test_rota_admin_permite_administrador(client):
    """CT-PERM-03: Validar que administrador acessa com êxito o painel /admin."""
    with client.session_transaction() as sess:
        sess["usuario"] = "admin"
        sess["tipo"] = "admin"

    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 200
    assert "Painel do Administrador" in response.get_data(as_text=True)


def test_rota_chamados_bloqueia_usuario_comum(client):
    """CT-PERM-04: Validar que usuário comum não acessa a fila de triagem técnica (/chamados)."""
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario1"
        sess["tipo"] = "usuario"

    response = client.get("/chamados", follow_redirects=True)
    assert response.status_code == 200
    assert "Acesso não autorizado" in response.get_data(as_text=True)


def test_rota_chamados_permite_tecnico_n1(client):
    """CT-PERM-05: Validar que técnico N1 acessa a fila técnica."""
    with client.session_transaction() as sess:
        sess["usuario"] = "tecnico_n1"
        sess["tipo"] = "tecnico_n1"

    response = client.get("/chamados", follow_redirects=False)
    assert response.status_code == 200


def test_rota_gerente_permite_gerente_e_admin(client):
    """CT-PERM-06: Validar que gerente e admin acessam /gerente, mas técnico é bloqueado."""
    # Teste com técnico (bloqueio)
    with client.session_transaction() as sess:
        sess["usuario"] = "tecnico_n1"
        sess["tipo"] = "tecnico_n1"

    res_tec = client.get("/gerente", follow_redirects=True)
    assert "Acesso não autorizado" in res_tec.get_data(as_text=True)

    # Teste com gerente (sucesso)
    with client.session_transaction() as sess:
        sess["usuario"] = "gerente"
        sess["tipo"] = "gerente"

    res_ger = client.get("/gerente", follow_redirects=False)
    assert res_ger.status_code == 200


def test_rota_auditoria_permite_admin_e_gerente(client):
    """CT-PERM-07: Validar que trilha de auditoria é restrita a admin e gerente."""
    # Usuário comum bloqueado
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario1"
        sess["tipo"] = "usuario"
    res_usr = client.get("/admin/auditoria", follow_redirects=True)
    assert "Acesso não autorizado" in res_usr.get_data(as_text=True)

    # Admin autorizado
    with client.session_transaction() as sess:
        sess["usuario"] = "admin"
        sess["tipo"] = "admin"
    res_adm = client.get("/admin/auditoria", follow_redirects=False)
    assert res_adm.status_code == 200
    assert "Trilhas de Auditoria" in res_adm.get_data(as_text=True)


def test_rota_colaboradores_permite_apenas_admin(client):
    """CT-PERM-08: Validar que catálogo de colaboradores é exclusivo de administradores."""
    with client.session_transaction() as sess:
        sess["usuario"] = "gerente"
        sess["tipo"] = "gerente"
    res_ger = client.get("/admin/colaboradores", follow_redirects=True)
    assert "Acesso não autorizado" in res_ger.get_data(as_text=True)

    with client.session_transaction() as sess:
        sess["usuario"] = "admin"
        sess["tipo"] = "admin"
    res_adm = client.get("/admin/colaboradores", follow_redirects=False)
    assert res_adm.status_code == 200
    assert "Catálogo Funcional de Colaboradores" in res_adm.get_data(as_text=True)
