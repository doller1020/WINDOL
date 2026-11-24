"""
Sistema Help Desk WINDOL - Módulo Principal da Aplicação Web
Desenvolvido com Python / Flask / SQLite.
Alinhado aos princípios de Segurança e Privacidade:
- LGPD (Lei nº 13.709/2018 - Artigos 6º, 9º, 18 e 46)
- OWASP ASVS v4.0.3 (V2 Autenticação, V3 Sessão, V4 Controle de Acesso, V14 Configuração)
- OWASP Top 10:2021 (A01 Broken Access Control, A02 Cryptographic Failures, A05 Security Misconfiguration)
- CIS Critical Security Controls v8 (Controles 3, 8 e 16)
- NIST SSDF SP 800-218 (Práticas PW.1 e RV.1)
"""

from datetime import datetime
from functools import wraps
import os
import secrets
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ================= SEGREDOS E CONFIGURAÇÃO (CIS 16.4 / OWASP ASVS V14.2) =================
def carregar_secret_key():
    """Carrega a SECRET_KEY com garantia de Fail-Secure a partir do ambiente ou arquivo .env."""
    key = os.environ.get("WINDOL_SECRET_KEY")
    if key:
        return key

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("WINDOL_SECRET_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val

    # Para testes controlados ou execução sem .env configurado
    if os.environ.get("FLASK_ENV") == "testing" or app.config.get("TESTING"):
        return "chave-secreta-de-testes-apenas-para-ci-cd-12345"

    raise RuntimeError(
        "[ERRO DE SEGURANÇA] A variável de ambiente 'WINDOL_SECRET_KEY' não está definida. "
        "Defina-a no sistema operacional ou crie o arquivo .env conforme .env.example."
    )

app.secret_key = carregar_secret_key()

# Configuração de segurança de Cookies de Sessão (OWASP ASVS V3.4)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# ================= CONEXÃO COM O BANCO DE DADOS =================
def get_db_connection():
    """Retorna uma conexão isolada com o banco SQLite com fábrica de linhas indexadas por nome."""
    db_path = app.config.get("DATABASE_PATH")
    if not db_path:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# ================= TRILHAS DE AUDITORIA (CIS CONTROLS V8 CONTROLE 8 / LGPD ART. 6º, X) =================
def registrar_log(acao, detalhes="", usuario=None):
    """Registra eventos críticos e operacionais na trilha de auditoria para fins de governança e não repúdio."""
    try:
        usuario_ativo = usuario or session.get("usuario", "ANONIMO")
        ip = request.remote_addr or "127.0.0.1"
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO logs_auditoria (data_hora, usuario, acao, detalhes, ip_origem) VALUES (?, ?, ?, ?, ?)",
            (data_hora, usuario_ativo, acao, detalhes, ip)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERRO DE AUDITORIA] Falha ao persistir log: {e}")


# ================= PROTEÇÃO CONTRA CSRF (OWASP ASVS V4.2 / TOP 10) =================
@app.before_request
def csrf_protect():
    """Valida o token CSRF em todas as requisições que alteram estado (POST, PUT, DELETE)."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)

    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        if app.config.get("TESTING_CSRF_DISABLED"):
            return None
        
        token = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
        if not token or token != session.get("csrf_token"):
            registrar_log(
                "FALHA_CSRF",
                f"Tentativa de requisição {request.method} na rota '{request.path}' com token CSRF inválido ou ausente"
            )
            flash("Sessão ou formulário expirado. Por favor, tente novamente.")
            return render_template("erro.html", codigo=403, mensagem="Requisição rejeitada por falha na validação CSRF (Cross-Site Request Forgery)."), 403

@app.context_processor
def inject_csrf_token():
    """Injeta a função geradora de token CSRF em todos os templates renderizados."""
    def get_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)
        return session["csrf_token"]
    return dict(csrf_token=get_token)


# ================= SECURITY HEADERS (OWASP ASVS V14 / CIS 16) =================
@app.after_request
def aplicar_security_headers(response):
    """Aplica cabeçalhos de proteção contra XSS, Clickjacking e sniffing MIME."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ================= DECORADORES DE CONTROLE DE ACESSO (RBAC / OWASP A01 / ASVS V4) =================
def login_required(f):
    """Garante que a rota só seja acessível por usuários autenticados."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            flash("Acesso restrito. Faça login para continuar.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def perfil_required(*perfis_permitidos):
    """Aplica o princípio do Menor Privilégio, restringindo endpoints aos perfis explicitamente autorizados."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "usuario" not in session:
                flash("Acesso restrito. Faça login para continuar.")
                return redirect(url_for("login"))

            tipo_usuario = session.get("tipo")
            if tipo_usuario not in perfis_permitidos:
                registrar_log(
                    "ACESSO_NEGADO_RBAC",
                    f"Tentativa de acesso não autorizado à rota '{request.path}' por perfil '{tipo_usuario}'"
                )
                flash("Acesso não autorizado para o seu perfil funcional.")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ================= LOGIN (CRIPTOGRAFIA DE SENHAS - ASVS V2) =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Consulta parametrizada segura contra SQL Injection
        cursor.execute("SELECT * FROM usuarios WHERE login=?", (usuario,))
        resultado = cursor.fetchone()
        conn.close()

        # Validação com função de hash adaptativo (PBKDF2/SHA-256)
        if resultado and check_password_hash(resultado["senha"], senha):
            session["usuario"] = resultado["login"]
            session["tipo"] = resultado["tipo"]
            session["nome"] = resultado["nome_completo"] if "nome_completo" in resultado.keys() else resultado["login"]

            registrar_log("LOGIN_SUCESSO", f"Perfil autenticado: {resultado['tipo']}", usuario=usuario)

            # Redirecionamento por perfil funcional
            if resultado["tipo"] == "usuario":
                return redirect(url_for("meus_chamados"))
            elif resultado["tipo"] in ["tecnico_n1", "tecnico_n2", "tecnico_n3"]:
                return redirect(url_for("listar_chamados"))
            elif resultado["tipo"] == "admin":
                return redirect(url_for("admin"))
            elif resultado["tipo"] == "gerente":
                return redirect(url_for("gerente"))

        # Registro de falha de autenticação para monitoramento de força bruta
        registrar_log("LOGIN_FALHA", "Credencial inválida ou usuário inexistente", usuario=usuario or "DESCONHECIDO")
        flash("Login ou senha inválidos!")
        return redirect(url_for("login"))

    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    usuario = session.get("usuario")
    if usuario:
        registrar_log("LOGOUT", "Sessão encerrada pelo usuário", usuario=usuario)
    session.clear()
    flash("Sessão finalizada com sucesso.")
    return redirect(url_for("login"))


# ================= ALTERAR SENHA (HASH PBKDF2 / OWASP ASVS V2) =================
@app.route("/alterar_senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    if request.method == "POST":
        nova_senha = request.form.get("nova_senha", "")
        confirma_senha = request.form.get("confirma_senha", "")

        if len(nova_senha) < 6:
            flash("A senha deve conter no mínimo 6 caracteres.")
            return render_template("alterar_senha.html")

        if nova_senha != confirma_senha:
            flash("As senhas não coincidem. Tente novamente.")
            return render_template("alterar_senha.html")

        senha_hash = generate_password_hash(nova_senha, method="pbkdf2:sha256", salt_length=16)
        usuario_logado = session["usuario"]

        conn = get_db_connection()
        conn.execute("UPDATE usuarios SET senha=? WHERE login=?", (senha_hash, usuario_logado))
        conn.commit()
        conn.close()

        registrar_log("ALTERAR_SENHA", f"Senha atualizada com sucesso para o usuário '{usuario_logado}'")
        flash("Senha atualizada com sucesso!")

        tipo = session.get("tipo")
        if tipo == "usuario":
            return redirect(url_for("meus_chamados"))
        elif tipo == "admin":
            return redirect(url_for("admin"))
        elif tipo == "gerente":
            return redirect(url_for("gerente"))
        else:
            return redirect(url_for("listar_chamados"))

    return render_template("alterar_senha.html")


# ================= ADMINISTRAÇÃO (PERFIL ADMIN) =================
@app.route("/admin")
@perfil_required("admin")
def admin():
    return render_template("admin.html")


# ================= GERENCIAR USUÁRIOS =================
@app.route("/usuarios")
@perfil_required("admin")
def usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, login, tipo, nome_completo, email_corporativo FROM usuarios ORDER BY id ASC")
    lista_usuarios = cursor.fetchall()
    conn.close()
    return render_template("usuarios.html", usuarios=lista_usuarios)


# ================= CRIAR USUÁRIO (HASH SEGURO DE SENHAS) =================
@app.route("/criar_usuario", methods=["POST"])
@perfil_required("admin")
def criar_usuario():
    login_novo = request.form.get("login", "").strip()
    senha_plana = request.form.get("senha", "")
    tipo = request.form.get("tipo", "usuario")
    nome = request.form.get("nome_completo", login_novo)
    email = request.form.get("email_corporativo", f"{login_novo}@windol.local")

    if not login_novo or not senha_plana:
        flash("Login e senha são obrigatórios.")
        return redirect(url_for("admin"))

    # Hashing seguro com salt da nova senha
    senha_hash = generate_password_hash(senha_plana, method="pbkdf2:sha256", salt_length=16)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios (login, senha, tipo, nome_completo, email_corporativo)
            VALUES (?, ?, ?, ?, ?)
        """, (login_novo, senha_hash, tipo, nome, email))
        conn.commit()
        registrar_log("CRIAR_USUARIO", f"Usuário '{login_novo}' criado com perfil '{tipo}'")
        flash("Usuário criado com sucesso com credenciais seguras!")
    except sqlite3.IntegrityError:
        flash("Erro: Esse login já existe no sistema.")
    finally:
        conn.close()

    return redirect(url_for("admin"))


# ================= EDITAR USUÁRIO =================
@app.route("/editar_usuario/<int:id>", methods=["GET", "POST"])
@perfil_required("admin")
def editar_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        login_novo = request.form.get("login", "").strip()
        senha_plana = request.form.get("senha", "").strip()
        tipo = request.form.get("tipo")
        nome = request.form.get("nome_completo", "")
        email = request.form.get("email_corporativo", "")

        if senha_plana:
            senha_hash = generate_password_hash(senha_plana, method="pbkdf2:sha256", salt_length=16)
            cursor.execute("""
                UPDATE usuarios
                SET login=?, senha=?, tipo=?, nome_completo=?, email_corporativo=?
                WHERE id=?
            """, (login_novo, senha_hash, tipo, nome, email, id))
        else:
            cursor.execute("""
                UPDATE usuarios
                SET login=?, tipo=?, nome_completo=?, email_corporativo=?
                WHERE id=?
            """, (login_novo, tipo, nome, email, id))

        conn.commit()
        conn.close()
        registrar_log("EDITAR_USUARIO", f"Usuário ID {id} ({login_novo}) atualizado")
        flash("Usuário atualizado com sucesso!")
        return redirect(url_for("usuarios"))

    cursor.execute("SELECT * FROM usuarios WHERE id=?", (id,))
    usuario = cursor.fetchone()
    conn.close()

    return render_template("editar_usuario.html", usuario=usuario)


# ================= EXCLUIR USUÁRIO =================
@app.route("/excluir_usuario/<int:id>", methods=["GET", "POST"])
@perfil_required("admin")
def excluir_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT login FROM usuarios WHERE id=?", (id,))
    alvo = cursor.fetchone()
    alvo_login = alvo["login"] if alvo else f"ID {id}"

    # Prevenção: Administrador não pode excluir a si mesmo
    if alvo_login == session.get("usuario"):
        conn.close()
        flash("Operação negada: não é permitido excluir o usuário atualmente autenticado.")
        return redirect(url_for("usuarios"))

    cursor.execute("DELETE FROM usuarios WHERE id=?", (id,))
    conn.commit()
    conn.close()

    registrar_log("EXCLUIR_USUARIO", f"Usuário '{alvo_login}' removido do sistema")
    flash("Usuário excluído com sucesso!")
    return redirect(url_for("usuarios"))


# ================= GERÊNCIA (RELATÓRIOS CONCLUÍDOS) =================
@app.route("/gerente")
@perfil_required("gerente", "admin")
def gerente():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM chamados
        WHERE status='finalizado'
        ORDER BY id DESC
    """)
    chamados = cursor.fetchall()
    conn.close()
    return render_template("gerente.html", chamados=chamados)


# ================= ABRIR CHAMADO =================
@app.route("/abrir_chamado", methods=["GET", "POST"])
@login_required
def abrir_chamado():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        usuario_logado = session["usuario"]
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

        if not titulo or not descricao:
            flash("Título e descrição são campos obrigatórios.")
            return render_template("abrir_chamado.html")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO chamados
            (titulo, descricao, status, usuario, nivel, data_abertura)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (titulo, descricao, "aberto", usuario_logado, "N1", data_atual))

        novo_id = cursor.lastrowid
        conn.commit()
        conn.close()

        registrar_log("ABRIR_CHAMADO", f"Chamado #{novo_id} aberto pelo usuário '{usuario_logado}'")

        return render_template(
            "mensagem.html",
            titulo="Chamado aberto com sucesso!",
            mensagem=f"Seu chamado #{novo_id} foi registrado com sucesso no sistema Windol."
        )

    return render_template("abrir_chamado.html")


# ================= MEUS CHAMADOS (USUÁRIO SOLICITANTE) =================
@app.route("/meus_chamados")
@login_required
def meus_chamados():
    ordem = request.args.get("ordem")
    ordem_sql = "ASC" if ordem == "antigo" else "DESC"

    conn = get_db_connection()
    cursor = conn.cursor()

    # Prevenção contra injeção SQL: lista permitida (whitelist) para ordenação e parâmetro para o usuário
    query = f"""
        SELECT * FROM chamados
        WHERE usuario=?
        ORDER BY id {ordem_sql}
    """
    cursor.execute(query, (session["usuario"],))
    chamados = cursor.fetchall()
    conn.close()

    return render_template("meus_chamados.html", chamados=chamados)


# ================= LISTAR CHAMADOS (FILA TÉCNICA COM RBAC) =================
@app.route("/chamados")
@perfil_required("tecnico_n1", "tecnico_n2", "tecnico_n3", "admin")
def listar_chamados():
    tipo = session["tipo"]

    if tipo == "tecnico_n1":
        nivel = "N1"
    elif tipo == "tecnico_n2":
        nivel = "N2"
    elif tipo == "tecnico_n3":
        nivel = "N3"
    else:
        nivel = request.args.get("nivel", "N1")
        if nivel not in ["N1", "N2", "N3"]:
            nivel = "N1"

    ordem = request.args.get("ordem")
    ordem_sql = "ASC" if ordem == "antigo" else "DESC"

    conn = get_db_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT * FROM chamados
        WHERE nivel=?
        AND status!='finalizado'
        AND (bloqueado_por IS NULL OR bloqueado_por=?)
        ORDER BY id {ordem_sql}
    """
    cursor.execute(query, (nivel, session["usuario"]))
    chamados = cursor.fetchall()
    conn.close()

    return render_template("listar_chamados.html", chamados=chamados)


# ================= RESOLVER CHAMADO (ASSUMIR ATENDIMENTO) =================
@app.route("/resolver/<int:id>")
@perfil_required("tecnico_n1", "tecnico_n2", "tecnico_n3", "admin")
def resolver(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE chamados
        SET
            bloqueado_por=?,
            status='em andamento',
            tecnico_responsavel=?,
            data_atendimento=?
        WHERE id=?
    """, (
        session["usuario"],
        session["usuario"],
        datetime.now().strftime("%d/%m/%Y %H:%M"),
        id
    ))
    conn.commit()

    cursor.execute("SELECT * FROM chamados WHERE id=?", (id,))
    chamado = cursor.fetchone()
    conn.close()

    registrar_log("ASSUMIR_CHAMADO", f"Chamado #{id} assumido pelo técnico '{session['usuario']}'")

    return render_template("painel_resolver.html", chamado=chamado)


# ================= FINALIZAR CHAMADO (PROTEGIDO COM RBAC E AUDITORIA) =================
@app.route("/finalizar/<int:id>", methods=["POST"])
@perfil_required("tecnico_n1", "tecnico_n2", "tecnico_n3", "admin")
def finalizar(id):
    resposta = request.form.get("resposta", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE chamados
        SET
            status='finalizado',
            resposta_tecnica=?,
            data_finalizacao=?,
            bloqueado_por=NULL
        WHERE id=?
    """, (
        resposta,
        datetime.now().strftime("%d/%m/%Y %H:%M"),
        id
    ))
    conn.commit()
    conn.close()

    registrar_log("FINALIZAR_CHAMADO", f"Chamado #{id} finalizado por '{session['usuario']}'")
    flash("Chamado finalizado com sucesso!")
    return redirect(url_for("listar_chamados"))


# ================= ENCAMINHAR CHAMADO (ESCALONAMENTO SEGURO) =================
@app.route("/encaminhar/<int:id>", methods=["POST"])
@perfil_required("tecnico_n1", "tecnico_n2", "admin")
def encaminhar(id):
    tipo = session["tipo"]
    novo_nivel = "N2" if tipo == "tecnico_n1" else "N3"
    resposta = request.form.get("resposta", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE chamados
        SET
            nivel=?,
            status='aberto',
            resposta_tecnica=?,
            bloqueado_por=NULL
        WHERE id=?
    """, (novo_nivel, resposta, id))

    conn.commit()
    conn.close()

    registrar_log("ENCAMINHAR_CHAMADO", f"Chamado #{id} escalonado para {novo_nivel} por '{session['usuario']}'")
    flash(f"Chamado encaminhado para o nível {novo_nivel}!")
    return redirect(url_for("listar_chamados"))


# ================= EXCLUIR CHAMADO (VALIDAÇÃO DE TITULARIDADE - BOLA/IDOR) =================
@app.route("/deletar_chamado/<int:id>", methods=["POST"])
@login_required
def deletar_chamado(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT usuario, status, nivel FROM chamados WHERE id=?", (id,))
    chamado = cursor.fetchone()

    if not chamado:
        conn.close()
        flash("Chamado não encontrado.")
        return redirect(url_for("meus_chamados"))

    tipo_usuario = session.get("tipo")
    usuario_logado = session.get("usuario")

    # Regra estrita de autorização (Menor Privilégio e Proteção de Propriedade):
    # Usuário comum só pode excluir chamados de sua própria autoria
    if tipo_usuario == "usuario" and chamado["usuario"] != usuario_logado:
        conn.close()
        registrar_log(
            "TENTATIVA_EXCLUSAO_INDEVIDA",
            f"Usuário '{usuario_logado}' tentou excluir chamado #{id} de '{chamado['usuario']}'"
        )
        flash("Permissão negada: você só pode excluir chamados de sua autoria!")
        return redirect(url_for("meus_chamados"))

    cursor.execute("DELETE FROM chamados WHERE id=?", (id,))
    conn.commit()
    conn.close()

    registrar_log("DELETAR_CHAMADO", f"Chamado #{id} excluído com sucesso por '{usuario_logado}'")
    flash("Chamado excluído com sucesso!")

    if tipo_usuario in ["tecnico_n1", "tecnico_n2", "tecnico_n3"]:
        return redirect(url_for("listar_chamados"))
    return redirect(url_for("meus_chamados"))


# ================= PAINEL DE AUDITORIA E LOGS (CIS CONTROLS V8 / LGPD ART. 6º, X) =================
@app.route("/admin/auditoria")
@perfil_required("admin", "gerente")
def painel_auditoria():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs_auditoria ORDER BY id DESC LIMIT 100")
    logs = cursor.fetchall()
    conn.close()
    return render_template("auditoria.html", logs=logs)


# ================= GESTÃO DE COLABORADORES (LGPD / DADOS SINTÉTICOS / MINIMIZAÇÃO) =================
@app.route("/admin/colaboradores")
@perfil_required("admin")
def painel_colaboradores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM colaboradores ORDER BY id ASC")
    colaboradores = cursor.fetchall()
    conn.close()
    return render_template("colaboradores.html", colaboradores=colaboradores)


# ================= AVISO DE PRIVACIDADE E POLÍTICA LGPD (ART. 9º) =================
@app.route("/privacidade")
def politica_privacidade():
    return render_template("privacidade.html")


# ================= TRATADORES DE ERRO SEGUROS (FAIL SECURE / CWE-200 / CWE-209) =================
@app.errorhandler(400)
def requisicao_invalida(e):
    return render_template("erro.html", codigo=400, mensagem="Requisição inválida ou parâmetros malformados."), 400


@app.errorhandler(403)
def acesso_proibido(e):
    return render_template("erro.html", codigo=403, mensagem="Acesso negado: você não possui as permissões necessárias para acessar este recurso."), 403


@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template("erro.html", codigo=404, mensagem="Recurso ou página não encontrada."), 404


@app.errorhandler(500)
def erro_interno_servidor(e):
    registrar_log("ERRO_INTERNO_500", "Exceção não tratada capturada pelo handler seguro")
    return render_template("erro.html", codigo=500, mensagem="Ocorreu um erro interno. A equipe técnica foi notificada."), 500


# ================= EXECUÇÃO SEGURA (HARDENING: DEBUG DESATIVADO - CWE-489) =================
if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="127.0.0.1", port=porta)
