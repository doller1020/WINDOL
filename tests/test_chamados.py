"""
Testes Automatizados - Ciclo de Vida dos Chamados e Proteção contra BOLA/IDOR (OWASP A01).
Valida: Abertura, listagem filtrada, assunção de tickets, escalonamento, encerramento e validação de propriedade.
"""

import sqlite3


def test_abertura_chamado_sucesso(client, test_db):
    """CT-CHAM-01: Validar que usuário autenticado consegue registrar chamado."""
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario1"
        sess["tipo"] = "usuario"

    response = client.post(
        "/abrir_chamado",
        data={"titulo": "Monitor Piscando", "descricao": "O monitor apaga intermitentemente."},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert "Chamado aberto com sucesso" in response.get_data(as_text=True)

    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT id, status, nivel FROM chamados WHERE titulo='Monitor Piscando'")
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row[1] == "aberto"
    assert row[2] == "N1"


def test_abertura_chamado_rejeita_campos_vazios(client, test_db):
    """CT-CHAM-02: Validar que chamado com título ou descrição vazia é rejeitado."""
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario1"
        sess["tipo"] = "usuario"

    response = client.post(
        "/abrir_chamado",
        data={"titulo": "", "descricao": ""},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert "campos obrigatórios" in response.get_data(as_text=True)


def test_meus_chamados_filtra_por_usuario(client, test_db):
    """CT-CHAM-03: Validar que a tela /meus_chamados exibe apenas chamados do solicitante logado."""
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario1"
        sess["tipo"] = "usuario"

    response = client.get("/meus_chamados", follow_redirects=False)
    html = response.get_data(as_text=True)

    assert "Problema Impressora" in html  # Pertence a usuario1
    assert "VPN Falhou" not in html       # Pertence a usuario2


def test_tecnico_assume_chamado(client, test_db):
    """CT-CHAM-04: Validar que técnico N1 assume atendimento de chamado N1."""
    with client.session_transaction() as sess:
        sess["usuario"] = "tecnico_n1"
        sess["tipo"] = "tecnico_n1"

    response = client.get("/resolver/1", follow_redirects=False)
    assert response.status_code == 200
    assert "Atendimento do Chamado #1" in response.get_data(as_text=True)

    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT status, tecnico_responsavel, bloqueado_por FROM chamados WHERE id=1")
    row = cur.fetchone()
    conn.close()

    assert row[0] == "em andamento"
    assert row[1] == "tecnico_n1"
    assert row[2] == "tecnico_n1"


def test_tecnico_escalona_chamado_n1_para_n2(client, test_db):
    """CT-CHAM-05: Validar que técnico N1 encaminha chamado para N2."""
    with client.session_transaction() as sess:
        sess["usuario"] = "tecnico_n1"
        sess["tipo"] = "tecnico_n1"

    response = client.post("/encaminhar/1", data={"resposta": "Necessário técnico de campo N2"}, follow_redirects=False)
    assert response.status_code == 302

    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT nivel, status, bloqueado_por FROM chamados WHERE id=1")
    row = cur.fetchone()
    conn.close()

    assert row[0] == "N2"
    assert row[1] == "aberto"
    assert row[2] is None


def test_tecnico_finaliza_chamado(client, test_db):
    """CT-CHAM-06: Validar finalização de chamado com parecer técnico."""
    with client.session_transaction() as sess:
        sess["usuario"] = "tecnico_n2"
        sess["tipo"] = "tecnico_n2"

    response = client.post("/finalizar/1", data={"resposta": "Cabo de rede substituído com sucesso."}, follow_redirects=False)
    assert response.status_code == 302

    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT status, resposta_tecnica, data_finalizacao FROM chamados WHERE id=1")
    row = cur.fetchone()
    conn.close()

    assert row[0] == "finalizado"
    assert "Cabo de rede substituído" in row[1]
    assert row[2] is not None


def test_exclusao_chamado_titular_sucesso(client, test_db):
    """CT-CHAM-07: Validar que o autor legítimo consegue excluir seu próprio chamado."""
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario2"
        sess["tipo"] = "usuario"

    # Chamado #2 pertence ao usuario2
    response = client.post("/deletar_chamado/2", follow_redirects=False)
    assert response.status_code == 302

    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT id FROM chamados WHERE id=2")
    row = cur.fetchone()
    conn.close()

    assert row is None


def test_exclusao_chamado_nao_titular_bloqueado(client, test_db):
    """CT-CHAM-08: Mitigação de IDOR/BOLA - Usuário comum NÃO pode deletar chamado de terceiro."""
    with client.session_transaction() as sess:
        sess["usuario"] = "usuario2"
        sess["tipo"] = "usuario"

    # Chamado #1 pertence a usuario1
    response = client.post("/deletar_chamado/1", follow_redirects=True)
    assert response.status_code == 200
    assert "você só pode excluir chamados de sua autoria" in response.get_data(as_text=True)

    # Comprovar que o chamado #1 PERMANECE intacto no banco
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT id FROM chamados WHERE id=1")
    row = cur.fetchone()
    conn.close()

    assert row is not None
