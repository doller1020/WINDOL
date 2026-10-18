import sqlite3
import os
from werkzeug.security import generate_password_hash

# ================= CONEXÃO =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

conexao = sqlite3.connect(db_path)
cursor = conexao.cursor()

print("Inicializando o banco de dados seguro do Sistema Windol...")

# ================= TABELA USUÁRIOS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL
)
""")

# Migração suave: verificar se colunas adicionais existem
cursor.execute("PRAGMA table_info(usuarios)")
colunas_usuarios = [col[1] for col in cursor.fetchall()]

if "nome_completo" not in colunas_usuarios:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN nome_completo TEXT")
if "email_corporativo" not in colunas_usuarios:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN email_corporativo TEXT")

# ================= TABELA CHAMADOS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS chamados (
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

# ================= TABELA COLABORADORES (LGPD / DADOS SINTÉTICOS) =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS colaboradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_login TEXT NOT NULL UNIQUE,
    nome_completo TEXT NOT NULL,
    departamento TEXT NOT NULL,
    email_corporativo TEXT NOT NULL,
    especialidade TEXT NOT NULL,
    status_ativo INTEGER DEFAULT 1
)
""")

# ================= TABELA LOGS DE AUDITORIA =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs_auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_hora TEXT NOT NULL,
    usuario TEXT NOT NULL,
    acao TEXT NOT NULL,
    detalhes TEXT,
    ip_origem TEXT NOT NULL
)
""")

# ================= POPULAR / ATUALIZAR USUÁRIOS COM HASH SEGURO =================
usuarios = [
    ("admin", "admin123", "admin", "Administrador do Sistema", "admin@windol.local"),
    ("wingrid", "senha123", "usuario", "Wingrid Costa (Solicitante)", "wingrid@windol.local"),
    ("doller", "senha123", "usuario", "Doller Costa (Solicitante)", "doller@windol.local"),
    ("tecnico1", "senha123", "tecnico_n1", "Técnico Nível 1 - Suporte", "tecnico1@windol.local"),
    ("tecnico2", "senha123", "tecnico_n2", "Técnico Nível 2 - Redes", "tecnico2@windol.local"),
    ("tecnico3", "senha123", "tecnico_n3", "Técnico Nível 3 - Especialista", "tecnico3@windol.local"),
    ("gerente", "senha123", "gerente", "Gerência de Operações de TI", "gerente@windol.local")
]

for login, senha_plana, tipo, nome, email in usuarios:
    # Gerar hash seguro (PBKDF2 com salt)
    senha_hash = generate_password_hash(senha_plana, method="pbkdf2:sha256", salt_length=16)
    
    cursor.execute("SELECT id FROM usuarios WHERE login=?", (login,))
    existe = cursor.fetchone()
    
    if existe:
        cursor.execute("""
            UPDATE usuarios 
            SET senha=?, tipo=?, nome_completo=?, email_corporativo=? 
            WHERE login=?
        """, (senha_hash, tipo, nome, email, login))
    else:
        cursor.execute("""
            INSERT INTO usuarios (login, senha, tipo, nome_completo, email_corporativo) 
            VALUES (?, ?, ?, ?, ?)
        """, (login, senha_hash, tipo, nome, email))

# ================= POPULAR COLABORADORES COM DADOS SINTÉTICOS (LGPD) =================
colaboradores_sinteticos = [
    ("tecnico1", "Carlos Eduardo Fictício", "Suporte Técnico", "carlos.ficticio@windol.local", "Atendimento Geral N1"),
    ("tecnico2", "Mariana Souza Fictícia", "Infraestrutura e Redes", "mariana.ficticia@windol.local", "Roteamento e Servidores N2"),
    ("tecnico3", "Roberto Mendes Fictício", "Segurança e Arquitetura", "roberto.ficticio@windol.local", "Bancos de Dados e Aplicações N3"),
    ("gerente", "Ana Paula Fictícia", "Gestão de TI", "ana.ficticia@windol.local", "Coordenação de Serviços de Suporte")
]

for login, nome, depto, email, esp in colaboradores_sinteticos:
    cursor.execute("SELECT id FROM colaboradores WHERE usuario_login=?", (login,))
    existe = cursor.fetchone()
    if existe:
        cursor.execute("""
            UPDATE colaboradores 
            SET nome_completo=?, departamento=?, email_corporativo=?, especialidade=? 
            WHERE usuario_login=?
        """, (nome, depto, email, esp, login))
    else:
        cursor.execute("""
            INSERT INTO colaboradores (usuario_login, nome_completo, departamento, email_corporativo, especialidade)
            VALUES (?, ?, ?, ?, ?)
        """, (login, nome, depto, email, esp))

# ================= INSERIR LOG DE INICIALIZAÇÃO =================
cursor.execute("""
    INSERT INTO logs_auditoria (data_hora, usuario, acao, detalhes, ip_origem)
    VALUES (datetime('now', 'localtime'), 'SISTEMA', 'INIT_DATABASE', 'Migração de banco com hashes seguros PBKDF2 e catálogo sintético LGPD', '127.0.0.1')
""")

# ================= FINALIZAÇÃO =================
conexao.commit()
conexao.close()

print("\n[OK] Banco de dados do Sistema Windol configurado com SUCESSO!")
print("Segurança aplicada:")
print(" - Senhas migradas para hash PBKDF2:SHA-256 (com salt)")
print(" - Tabela 'colaboradores' criada com dados sintéticos (LGPD Art. 6º)")
print(" - Tabela 'logs_auditoria' estruturada para rastreabilidade (DEVSEG / CIS 16)")
print("\nCredenciais atualizadas:")
print(" - admin    / admin123  (Perfil: admin)")
print(" - wingrid  / senha123  (Perfil: usuario)")
print(" - doller   / senha123  (Perfil: usuario)")
print(" - tecnico1 / senha123  (Perfil: tecnico_n1)")
print(" - tecnico2 / senha123  (Perfil: tecnico_n2)")
print(" - tecnico3 / senha123  (Perfil: tecnico_n3)")
print(" - gerente  / senha123  (Perfil: gerente)")