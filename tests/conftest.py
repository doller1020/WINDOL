"""
Configurações e Fixtures para os Testes Automatizados com Pytest.
Garante o isolamento completo: cria um banco de dados temporário exclusivo para testes,
sem nunca alterar ou comprometer a base de dados real do sistema.
"""

import os
import tempfile
import sqlite3
import pytest
from werkzeug.security import generate_password_hash

# Define variáveis de ambiente antes de importar o web.py
os.environ["WINDOL_SECRET_KEY"] = "chave-secreta-de-testes-pytest-1234567890abcdef"
os.environ["FLASK_ENV"] = "testing"

from web import app


@pytest.fixture
def test_db():
    """Cria um banco de dados SQLite temporário e inicializa o esquema completo de segurança."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Criação do esquema
    cur.execute("""
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL,
        nome_completo TEXT,
        email_corporativo TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE chamados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT NOT NULL,
        status TEXT NOT NULL,
        usuario TEXT NOT NULL,
        nivel TEXT NOT NULL,
        tecnico_responsavel TEXT,
        resposta_tecnica TEXT,
        data_abertura TEXT,
        data_atendimento TEXT,
        data_finalizacao TEXT,
        bloqueado_por TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE colaboradores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_login TEXT NOT NULL UNIQUE,
        nome_completo TEXT NOT NULL,
        departamento TEXT NOT NULL,
        email_corporativo TEXT NOT NULL,
        especialidade TEXT NOT NULL,
        status_ativo INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE logs_auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora TEXT NOT NULL,
        usuario TEXT NOT NULL,
        acao TEXT NOT NULL,
        detalhes TEXT,
        ip_origem TEXT NOT NULL
    )
    """)

    # Usuários com PBKDF2:SHA-256 e salt
    senha_hash = generate_password_hash("senha123", method="pbkdf2:sha256", salt_length=16)
    admin_hash = generate_password_hash("admin123", method="pbkdf2:sha256", salt_length=16)

    usuarios = [
        ("admin", admin_hash, "admin", "Admin Geral", "admin@windol.local"),
        ("usuario1", senha_hash, "usuario", "Solicitante 1", "usuario1@windol.local"),
        ("usuario2", senha_hash, "usuario", "Solicitante 2", "usuario2@windol.local"),
        ("tecnico_n1", senha_hash, "tecnico_n1", "Técnico N1", "tecnico1@windol.local"),
        ("tecnico_n2", senha_hash, "tecnico_n2", "Técnico N2", "tecnico2@windol.local"),
        ("tecnico_n3", senha_hash, "tecnico_n3", "Técnico N3", "tecnico3@windol.local"),
        ("gerente", senha_hash, "gerente", "Gerente Operações", "gerente@windol.local"),
    ]

    for u in usuarios:
        cur.execute(
            "INSERT INTO usuarios (login, senha, tipo, nome_completo, email_corporativo) VALUES (?, ?, ?, ?, ?)",
            u
        )

    # Chamados iniciais de teste
    cur.execute("""
        INSERT INTO chamados (titulo, descricao, status, usuario, nivel, data_abertura)
        VALUES ('Problema Impressora', 'Falha ao imprimir na recepção', 'aberto', 'usuario1', 'N1', '23/11/2026 10:00')
    """)
    cur.execute("""
        INSERT INTO chamados (titulo, descricao, status, usuario, nivel, data_abertura)
        VALUES ('VPN Falhou', 'Erro de autenticação VPN', 'aberto', 'usuario2', 'N1', '23/11/2026 11:00')
    """)

    # Colaboradores sintéticos LGPD
    cur.execute("""
        INSERT INTO colaboradores (usuario_login, nome_completo, departamento, email_corporativo, especialidade)
        VALUES ('tecnico_n1', 'Carlos Fictício N1', 'Suporte', 'carlos@windol.local', 'Atendimento N1')
    """)

    conn.commit()
    conn.close()

    yield db_path

    # Limpeza segura do arquivo temporário
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client(test_db):
    """Fixture do cliente de teste Flask apontando para a base isolada."""
    app.config["TESTING"] = True
    app.config["DATABASE_PATH"] = test_db
    app.config["TESTING_CSRF_DISABLED"] = True  # Para testes unitários gerais

    with app.test_client() as client:
        yield client
