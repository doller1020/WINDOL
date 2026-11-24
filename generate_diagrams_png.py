"""
Gerador de diagramas PNG para o Sistema WINDOL — TCC UPIS
Renderiza os diagramas de arquitetura em formato PNG utilizando matplotlib.
Os diagramas Mermaid originais estão nos arquivos .md em docs/arquitetura/.
Este script gera versões visuais PNG prontas para inclusão no TCC.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "docs", "arquitetura", "png")
os.makedirs(OUT_DIR, exist_ok=True)

PALETTE = {
    "header_bg": "#1A237E",
    "header_fg": "white",
    "original_node": "#EF9A9A",
    "original_edge": "#C62828",
    "windol_node": "#A5D6A7",
    "windol_edge": "#1B5E20",
    "security_node": "#CE93D8",
    "security_edge": "#6A1B9A",
    "db_node": "#90CAF9",
    "db_edge": "#0D47A1",
    "auth_node": "#FFE082",
    "auth_edge": "#F57F17",
    "rbac_node": "#80DEEA",
    "rbac_edge": "#006064",
    "neutral": "#E0E0E0",
    "text": "#212121",
    "arrow": "#37474F",
}

def add_box(ax, x, y, w, h, text, fc, ec, fontsize=8, bold=False, wrap=True):
    box = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.02",
        facecolor=fc, edgecolor=ec, linewidth=1.5, zorder=3
    )
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=PALETTE["text"], fontweight=weight, wrap=wrap,
            multialignment="center", zorder=4)

def add_arrow(ax, x1, y1, x2, y2, color=None):
    color = color or PALETTE["arrow"]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.5), zorder=2)

def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {path}")

# ─────────────────────────────────────────────────────────────
# DIAGRAMA 1 — Arquitetura do Sistema Original
# ─────────────────────────────────────────────────────────────
def diagrama_arquitetura_original():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_facecolor("white")

    fig.patch.set_facecolor("white")
    ax.set_title("Arquitetura do Sistema Original\n(sistema-chamados-faculdade — Commit 2a3b243)",
                 fontsize=13, fontweight="bold", color=PALETTE["header_bg"], pad=12)

    # Atores
    add_box(ax, 1.2, 6.5, 1.8, 0.7, "[U] Usuário\nComum", PALETTE["neutral"], "#757575", bold=True)
    add_box(ax, 1.2, 5.3, 1.8, 0.7, "[T] Técnico", PALETTE["neutral"], "#757575", bold=True)
    add_box(ax, 1.2, 4.1, 1.8, 0.7, "[A] Administrador", PALETTE["neutral"], "#757575", bold=True)

    # Interface HTML
    add_box(ax, 3.8, 5.5, 2.0, 2.0,
            "Interface HTML\n(Templates Flask)\n\n• login.html\n• usuario.html\n• tecnico.html\n• admin.html\n• chamados.html",
            PALETTE["neutral"], "#9E9E9E", fontsize=7)

    # web.py monolito
    add_box(ax, 7.0, 5.8, 2.6, 1.2,
            "[!] Autenticação Insegura\nsecret_key='1234'\nSenhas em texto puro\ndebug=True",
            PALETTE["original_node"], PALETTE["original_edge"], fontsize=7)
    add_box(ax, 7.0, 4.3, 2.6, 1.2,
            "[!] Sem Controle de Acesso\nRotas sem @login_required\nSem verificação de perfil\nSem proteção CSRF",
            PALETTE["original_node"], PALETTE["original_edge"], fontsize=7)
    add_box(ax, 7.0, 2.8, 2.6, 1.2,
            "[!] Sem Logs ou Auditoria\nNenhum registro de eventos\nSem trilha de auditoria\nSem tratamento de erros",
            PALETTE["original_node"], PALETTE["original_edge"], fontsize=7)

    # Banco
    add_box(ax, 10.5, 4.3, 1.8, 2.5,
            "SQLite\ndatabase.db\n\n• usuarios\n  (senha plain)\n• chamados\n  (sem audit)\n\n[X] Sem logs",
            PALETTE["db_node"], PALETTE["db_edge"], fontsize=7)

    # Setas atores → interface
    for y in [6.5, 5.3, 4.1]:
        add_arrow(ax, 2.1, y, 2.8, 5.5)

    # Interface → web.py
    add_arrow(ax, 4.8, 5.8, 5.7, 5.8)
    add_arrow(ax, 4.8, 5.3, 5.7, 4.3)
    add_arrow(ax, 4.8, 4.8, 5.7, 2.8)

    # web.py → banco
    for y in [5.8, 4.3, 2.8]:
        add_arrow(ax, 8.3, y, 9.6, 4.3)

    # Legenda
    leg = [mpatches.Patch(fc=PALETTE["original_node"], ec=PALETTE["original_edge"], label="Vulnerabilidade identificada"),
           mpatches.Patch(fc=PALETTE["db_node"], ec=PALETTE["db_edge"], label="Banco de dados"),
           mpatches.Patch(fc=PALETTE["neutral"], ec="#757575", label="Componente de interface")]
    ax.legend(handles=leg, loc="lower left", fontsize=7, framealpha=0.9)

    save(fig, "01_arquitetura_original.png")

# ─────────────────────────────────────────────────────────────
# DIAGRAMA 2 — Arquitetura do Sistema WINDOL Atualizado
# ─────────────────────────────────────────────────────────────
def diagrama_arquitetura_windol():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 9)
    ax.axis("off"); ax.set_facecolor("white"); fig.patch.set_facecolor("white")

    ax.set_title("Arquitetura do Sistema WINDOL — Versão Segura\n(Commit 124c888 — Branch main)",
                 fontsize=13, fontweight="bold", color=PALETTE["header_bg"], pad=12)

    # Perfis
    perfis = [("[U] Usuário", 7.5), ("[T] Técnico N1/N2/N3", 6.5),
              ("[G] Gerente", 5.5), ("[A] Admin", 4.5)]
    for label, y in perfis:
        add_box(ax, 1.2, y, 2.0, 0.65, label, PALETTE["neutral"], "#757575", fontsize=7, bold=True)

    # Camada CSRF + Headers
    add_box(ax, 4.2, 6.5, 2.4, 1.6,
            "[SEC] Middleware de Segurança\n\n• Security Headers\n  (X-Frame-Options,\n  X-Content-Type)\n• Validação CSRF\n  (HTTP 403 se inválido)\n• Cookies HttpOnly+Lax",
            PALETTE["security_node"], PALETTE["security_edge"], fontsize=7)

    # Autenticação
    add_box(ax, 7.0, 7.3, 2.4, 1.0,
            "[KEY] Autenticação\nPBKDF2:SHA-256\ncheck_password_hash()\nFail-Secure SECRET_KEY",
            PALETTE["auth_node"], PALETTE["auth_edge"], fontsize=7)

    # RBAC
    add_box(ax, 7.0, 5.9, 2.4, 1.0,
            "[A] RBAC Backend\n@login_required\n@perfil_required(*perfis)\nSem bypass via UI",
            PALETTE["rbac_node"], PALETTE["rbac_edge"], fontsize=7)

    # Lógica de negócio
    add_box(ax, 7.0, 4.5, 2.4, 1.0,
            "⚙ Lógica de Negócio\nAbertura / Edição\nEscalonamento N1→N2→N3\nFinalização com parecer",
            PALETTE["windol_node"], PALETTE["windol_edge"], fontsize=7)

    # Auditoria
    add_box(ax, 7.0, 3.1, 2.4, 1.0,
            "[LOG] Trilha de Auditoria\nregistrar_log(acao, ip)\nLOGIN_SUCESSO / FALHA\nACESSO_NEGADO_RBAC",
            PALETTE["windol_node"], PALETTE["windol_edge"], fontsize=7)

    # Tratamento de erros
    add_box(ax, 7.0, 1.7, 2.4, 1.0,
            "[ERR] Erros Seguros\nHandlers 400/403/404/500\nSem stack trace exposto\ntemplates/erro.html",
            PALETTE["neutral"], "#78909C", fontsize=7)

    # Banco
    add_box(ax, 11.0, 5.5, 2.5, 4.0,
            "SQLite database.db\n\n[OK] usuarios\n  hash PBKDF2+salt\n\n[OK] chamados\n  titularidade IDOR\n\n[OK] colaboradores\n  dados minimizados\n  (LGPD Art. 6º III)\n\n[OK] logs_auditoria\n  eventos + IP",
            PALETTE["db_node"], PALETTE["db_edge"], fontsize=7)

    # Env
    add_box(ax, 11.0, 2.5, 2.5, 1.2,
            "[ENV] Variáveis de Ambiente\nWINDOL_SECRET_KEY\n.env (gitignored)\ndebug=False",
            PALETTE["auth_node"], PALETTE["auth_edge"], fontsize=7)

    # Setas: perfis → middleware
    for _, y in perfis:
        add_arrow(ax, 2.2, y, 3.0, 6.5)

    # Middleware → auth + rbac
    add_arrow(ax, 5.4, 6.8, 5.8, 7.3)
    add_arrow(ax, 5.4, 6.2, 5.8, 5.9)

    # auth → rbac → negocio → audit
    add_arrow(ax, 7.0, 6.8, 7.0, 6.4)
    add_arrow(ax, 7.0, 5.4, 7.0, 5.0)
    add_arrow(ax, 7.0, 4.0, 7.0, 3.6)
    add_arrow(ax, 7.0, 2.6, 7.0, 2.2)

    # Lógica → banco e audit → banco
    add_arrow(ax, 8.2, 4.5, 9.75, 5.5)
    add_arrow(ax, 8.2, 3.1, 9.75, 4.5)
    add_arrow(ax, 8.2, 7.3, 9.75, 7.0)

    # env → autenticação
    add_arrow(ax, 11.0, 3.1, 8.2, 7.1)

    leg = [mpatches.Patch(fc=PALETTE["security_node"], ec=PALETTE["security_edge"], label="Middleware / Filtros de Segurança"),
           mpatches.Patch(fc=PALETTE["auth_node"], ec=PALETTE["auth_edge"], label="Autenticação e Configuração"),
           mpatches.Patch(fc=PALETTE["rbac_node"], ec=PALETTE["rbac_edge"], label="Controle de Acesso RBAC"),
           mpatches.Patch(fc=PALETTE["windol_node"], ec=PALETTE["windol_edge"], label="Lógica de Negócio / Auditoria"),
           mpatches.Patch(fc=PALETTE["db_node"], ec=PALETTE["db_edge"], label="Banco de Dados")]
    ax.legend(handles=leg, loc="lower left", fontsize=7, framealpha=0.9)

    save(fig, "02_arquitetura_windol.png")

# ─────────────────────────────────────────────────────────────
# DIAGRAMA 3 — Fluxo de Autenticação
# ─────────────────────────────────────────────────────────────
def diagrama_fluxo_autenticacao():
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.axis("off"); ax.set_facecolor("white"); fig.patch.set_facecolor("white")
    ax.set_title("Fluxo de Autenticação Segura — WINDOL\n(PBKDF2:SHA-256 / CSRF / Auditoria)",
                 fontsize=12, fontweight="bold", color=PALETTE["header_bg"], pad=10)

    steps = [
        (5.0, 9.2, "1. Usuário acessa GET /", PALETTE["neutral"], "#78909C"),
        (5.0, 8.1, "2. Flask retorna formulário\ncom Token CSRF embutido", PALETTE["windol_node"], PALETTE["windol_edge"]),
        (5.0, 7.0, "3. Usuário envia POST /\n{login, senha, csrf_token}", PALETTE["neutral"], "#78909C"),
        (5.0, 5.9, "4. Middleware valida Token CSRF\n(@before_request)", PALETTE["security_node"], PALETTE["security_edge"]),
    ]
    for x, y, txt, fc, ec in steps:
        add_box(ax, x, y, 5.5, 0.75, txt, fc, ec, fontsize=8)
        if y > 6.0:
            add_arrow(ax, x, y - 0.38, x, y - 0.62 + 0.38 - 0.38)

    add_arrow(ax, 5.0, 5.52, 5.0, 5.3)

    # Decisão CSRF
    add_box(ax, 5.0, 4.9, 3.5, 0.6, "Token CSRF válido?", PALETTE["auth_node"], PALETTE["auth_edge"], fontsize=8, bold=True)
    add_arrow(ax, 3.25, 4.9, 2.2, 4.1)
    ax.text(2.4, 4.5, "NÃO", fontsize=7, color=PALETTE["original_edge"], fontweight="bold")
    add_box(ax, 1.5, 3.7, 2.0, 0.6, "HTTP 403\nLog FALHA_CSRF", PALETTE["original_node"], PALETTE["original_edge"], fontsize=7)

    add_arrow(ax, 6.75, 4.9, 7.8, 4.1)
    ax.text(7.3, 4.5, "SIM", fontsize=7, color=PALETTE["windol_edge"], fontweight="bold")
    add_box(ax, 8.3, 3.7, 2.4, 0.6, "SELECT usuario\n(query parametrizada)", PALETTE["db_node"], PALETTE["db_edge"], fontsize=7)

    add_arrow(ax, 8.3, 3.4, 8.3, 2.9)
    add_box(ax, 8.3, 2.5, 2.4, 0.6, "check_password_hash()\nPBKDF2:SHA-256", PALETTE["auth_node"], PALETTE["auth_edge"], fontsize=7)
    add_arrow(ax, 8.3, 2.2, 8.3, 1.65)

    add_box(ax, 8.3, 1.3, 2.4, 0.6, "Senha correta?", PALETTE["auth_node"], PALETTE["auth_edge"], fontsize=8, bold=True)
    add_arrow(ax, 7.1, 1.3, 5.9, 1.3)
    ax.text(6.4, 1.4, "NÃO", fontsize=7, color=PALETTE["original_edge"], fontweight="bold")
    add_box(ax, 4.8, 1.3, 2.0, 0.6, "Flash genérico\n'Login ou senha inválidos'\nLog LOGIN_FALHA", PALETTE["original_node"], PALETTE["original_edge"], fontsize=7)

    add_arrow(ax, 8.3, 1.0, 8.3, 0.5)
    ax.text(8.4, 0.7, "SIM", fontsize=7, color=PALETTE["windol_edge"], fontweight="bold")
    add_box(ax, 8.3, 0.2, 2.4, 0.5, "Sessão inicializada\nRedirect por perfil\nLog LOGIN_SUCESSO", PALETTE["windol_node"], PALETTE["windol_edge"], fontsize=7)

    save(fig, "03_fluxo_autenticacao.png")

# ─────────────────────────────────────────────────────────────
# DIAGRAMA 4 — Controle de Acesso RBAC
# ─────────────────────────────────────────────────────────────
def diagrama_rbac():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis("off"); ax.set_facecolor("white"); fig.patch.set_facecolor("white")
    ax.set_title("Controle de Acesso Baseado em Papéis — RBAC\n(OWASP ASVS V4 / A01:2021 Broken Access Control)",
                 fontsize=12, fontweight="bold", color=PALETTE["header_bg"], pad=10)

    # Requisição inicial
    add_box(ax, 2.0, 7.0, 3.0, 0.7, "Requisição HTTP\n(qualquer rota protegida)", PALETTE["neutral"], "#757575", fontsize=8)
    add_arrow(ax, 2.0, 6.65, 2.0, 6.15)

    # Check login
    add_box(ax, 2.0, 5.8, 3.0, 0.65, "@login_required\nSessão ativa?", PALETTE["auth_node"], PALETTE["auth_edge"], fontsize=8, bold=True)
    add_arrow(ax, 0.5, 5.8, 0.1, 5.1)
    ax.text(0.05, 5.5, "NÃO", fontsize=7, color=PALETTE["original_edge"], fontweight="bold")
    add_box(ax, 0.8, 4.7, 1.8, 0.6, "→ /login\nFlash 'Acesso restrito'", PALETTE["original_node"], PALETTE["original_edge"], fontsize=7)

    add_arrow(ax, 3.5, 5.8, 4.2, 5.1)
    ax.text(3.9, 5.5, "SIM", fontsize=7, color=PALETTE["windol_edge"], fontweight="bold")

    add_box(ax, 5.5, 4.7, 3.0, 0.65, "@perfil_required(*perfis)\nPerfil permitido?", PALETTE["rbac_node"], PALETTE["rbac_edge"], fontsize=8, bold=True)
    add_arrow(ax, 4.0, 4.7, 3.5, 4.0)
    ax.text(3.6, 4.4, "NÃO", fontsize=7, color=PALETTE["original_edge"], fontweight="bold")
    add_box(ax, 2.8, 3.6, 2.0, 0.6, "Log ACESSO_NEGADO_RBAC\n→ /login (HTTP 302)", PALETTE["original_node"], PALETTE["original_edge"], fontsize=7)

    add_arrow(ax, 7.0, 4.7, 7.8, 4.0)
    ax.text(7.5, 4.4, "SIM", fontsize=7, color=PALETTE["windol_edge"], fontweight="bold")

    add_box(ax, 9.0, 3.6, 3.0, 0.65, "Operação de exclusão?\n(anti-IDOR check)", PALETTE["security_node"], PALETTE["security_edge"], fontsize=8, bold=True)
    add_arrow(ax, 7.5, 3.6, 7.0, 2.9)
    ax.text(7.1, 3.3, "NÃO", fontsize=7, color=PALETTE["windol_edge"], fontweight="bold")
    add_box(ax, 6.5, 2.5, 2.0, 0.6, "[OK] Executa operação\nLog sucesso", PALETTE["windol_node"], PALETTE["windol_edge"], fontsize=7)

    add_arrow(ax, 10.5, 3.6, 11.0, 2.9)
    ax.text(10.7, 3.3, "SIM", fontsize=7, color=PALETTE["windol_edge"], fontweight="bold")
    add_box(ax, 11.0, 2.5, 1.8, 0.65, "Usuário é\nauthor/titular?", PALETTE["auth_node"], PALETTE["auth_edge"], fontsize=7, bold=True)
    add_arrow(ax, 11.0, 2.17, 11.0, 1.6)
    ax.text(11.1, 1.9, "NÃO", fontsize=7, color=PALETTE["original_edge"], fontweight="bold")
    add_box(ax, 11.0, 1.2, 1.8, 0.6, "Log IDOR Bloqueado\nFlash 'Permissão negada'", PALETTE["original_node"], PALETTE["original_edge"], fontsize=7)
    add_arrow(ax, 10.1, 2.5, 8.5, 2.5)
    ax.text(9.2, 2.6, "SIM", fontsize=7, color=PALETTE["windol_edge"], fontweight="bold")

    # Perfis disponíveis
    ax.text(0.3, 1.8, "Perfis do Sistema WINDOL:", fontsize=8, fontweight="bold", color=PALETTE["header_bg"])
    perfis_txt = ["• usuario — Solicitante (meus_chamados, abrir_chamado)",
                  "• tecnico_n1/n2/n3 — Atendimento por nível de suporte",
                  "• gerente — Relatórios e painel de gestão",
                  "• admin — Administração plena"]
    for i, txt in enumerate(perfis_txt):
        ax.text(0.4, 1.4 - i * 0.35, txt, fontsize=7, color=PALETTE["text"])

    save(fig, "04_controle_acesso_rbac.png")

# ─────────────────────────────────────────────────────────────
# DIAGRAMA 5 — Ciclo de Vida dos Chamados
# ─────────────────────────────────────────────────────────────
def diagrama_ciclo_chamados():
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7)
    ax.axis("off"); ax.set_facecolor("white"); fig.patch.set_facecolor("white")
    ax.set_title("Ciclo de Vida dos Chamados de Suporte — WINDOL\n(Status: aberto → em andamento → finalizado | Níveis: N1 → N2 → N3)",
                 fontsize=11, fontweight="bold", color=PALETTE["header_bg"], pad=10)

    # Estados
    estados = [
        (1.5, 4.5, "ABERTO\n(Usuário cria\no chamado)", PALETTE["windol_node"], PALETTE["windol_edge"]),
        (4.0, 4.5, "EM ANDAMENTO\nN1\n(Técnico N1\nassume)", PALETTE["auth_node"], PALETTE["auth_edge"]),
        (6.5, 4.5, "EM ANDAMENTO\nN2\n(Escalonado\npara N2)", PALETTE["auth_node"], PALETTE["auth_edge"]),
        (9.0, 4.5, "EM ANDAMENTO\nN3\n(Escalonado\npara N3)", PALETTE["auth_node"], PALETTE["auth_edge"]),
        (5.5, 2.0, "FINALIZADO\n(Parecer técnico\nregistrado)", PALETTE["windol_node"], PALETTE["windol_edge"]),
    ]
    for x, y, txt, fc, ec in estados:
        add_box(ax, x, y, 2.2, 1.2, txt, fc, ec, fontsize=8, bold=True)

    # Setas de progresso
    add_arrow(ax, 2.6, 4.5, 2.9, 4.5); ax.text(2.75, 4.65, "Técnico\nassume", fontsize=6.5, ha="center")
    add_arrow(ax, 5.1, 4.5, 5.4, 4.5); ax.text(5.25, 4.65, "Escalona\npara N2", fontsize=6.5, ha="center")
    add_arrow(ax, 7.6, 4.5, 7.9, 4.5); ax.text(7.75, 4.65, "Escalona\npara N3", fontsize=6.5, ha="center")

    # Finalização de qualquer nível
    for x in [4.0, 6.5, 9.0]:
        add_arrow(ax, x, 3.9, 5.5, 2.6)
    ax.text(5.6, 3.3, "Técnico finaliza\ncom parecer", fontsize=7, ha="center", color=PALETTE["windol_edge"])

    # Cancelamento
    add_box(ax, 1.5, 2.0, 2.2, 1.0, "CANCELADO\n(Usuário exclui\nchamado próprio)", PALETTE["neutral"], "#78909C", fontsize=7)
    add_arrow(ax, 1.5, 3.9, 1.5, 2.5)
    ax.text(1.6, 3.2, "Usuário\ncancela", fontsize=6.5, ha="left")

    # Anti-IDOR
    add_box(ax, 10.5, 2.0, 2.2, 1.0, "BLOQUEADO\n(Anti-IDOR)\nSomente autor\npode excluir", PALETTE["original_node"], PALETTE["original_edge"], fontsize=7)
    ax.annotate("", xy=(10.5, 2.5), xytext=(9.0, 3.9),
                arrowprops=dict(arrowstyle="->", color=PALETTE["original_edge"], lw=1.5, linestyle="dashed"))
    ax.text(10.1, 3.3, "Outro usuário\ntenta excluir →\nbloqueado", fontsize=6.5, ha="center", color=PALETTE["original_edge"])

    # Banco
    add_box(ax, 11.5, 5.5, 1.2, 0.6, "SQLite\nlogs_auditoria", PALETTE["db_node"], PALETTE["db_edge"], fontsize=7)
    add_arrow(ax, 10.1, 4.5, 10.9, 5.5)
    ax.text(10.8, 5.1, "Log evento", fontsize=6, ha="center")

    save(fig, "05_ciclo_vida_chamados.png")

# ─────────────────────────────────────────────────────────────
# DIAGRAMA 6 — Modelo Entidade-Relacionamento
# ─────────────────────────────────────────────────────────────
def diagrama_der():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 8)
    ax.axis("off"); ax.set_facecolor("white"); fig.patch.set_facecolor("white")
    ax.set_title("Modelo Entidade-Relacionamento — WINDOL\n(Schema real do database.db — 4 tabelas)",
                 fontsize=12, fontweight="bold", color=PALETTE["header_bg"], pad=10)

    tabelas = [
        (2.5, 5.5, 2.8, 2.6, "USUARIOS\n─────────────\nid (PK)\nlogin (UNIQUE)\nsenha (HASH PBKDF2)\nnome\ntipo (FK→perfil)\nemail", PALETTE["db_node"], PALETTE["db_edge"]),
        (7.0, 5.5, 3.2, 3.2, "CHAMADOS\n────────────────\nid (PK)\ntitulo\ndescricao\nstatus\nnivel (N1/N2/N3)\nusuario (FK→usuarios)\nbloqueado_por\ntecnico_responsavel\nresposta_tecnica\ndata_abertura\ndata_atendimento\ndata_finalizacao\ndata", PALETTE["auth_node"], PALETTE["auth_edge"]),
        (2.5, 1.8, 2.8, 2.0, "COLABORADORES\n─────────────────\nid (PK)\nnome\ncargo\nramal\n\n(dados sintéticos\nminimizados — LGPD)", PALETTE["windol_node"], PALETTE["windol_edge"]),
        (11.2, 5.0, 2.5, 2.4, "LOGS_AUDITORIA\n──────────────\nid (PK)\nusuario\nacao\ndetalhes\nip\ntimestamp", PALETTE["security_node"], PALETTE["security_edge"]),
    ]
    for x, y, w, h, txt, fc, ec in tabelas:
        add_box(ax, x, y, w, h, txt, fc, ec, fontsize=7)

    # Relacionamentos
    add_arrow(ax, 3.9, 5.5, 5.4, 5.8); ax.text(4.6, 6.1, "abre (1:N)", fontsize=7, ha="center")
    add_arrow(ax, 11.2, 5.0, 10.0, 5.5); ax.text(10.5, 5.5, "registra\nevento (N:1)", fontsize=6.5, ha="center")
    ax.text(2.5, 0.5, "* login.py (fase CLI) reusava autenticação idêntica à tabela USUARIOS acima", fontsize=6.5, color="#78909C", ha="center")

    # Cardinalidades
    ax.text(5.6, 6.0, "N", fontsize=9, fontweight="bold", color=PALETTE["db_edge"])
    ax.text(3.7, 5.65, "1", fontsize=9, fontweight="bold", color=PALETTE["db_edge"])

    save(fig, "06_modelo_entidade_relacionamento.png")

# ─────────────────────────────────────────────────────────────
# DIAGRAMA 7 — Fluxo de Dados Pessoais (LGPD)
# ─────────────────────────────────────────────────────────────
def diagrama_fluxo_lgpd():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis("off"); ax.set_facecolor("white"); fig.patch.set_facecolor("white")
    ax.set_title("Fluxo de Tratamento de Dados Pessoais — LGPD\nLei nº 13.709/2018 — Princípios de Finalidade, Necessidade e Transparência",
                 fontsize=11, fontweight="bold", color=PALETTE["header_bg"], pad=10)

    # Titular
    add_box(ax, 1.3, 6.5, 2.0, 0.8, "[U] Titular\nde Dados\n(Usuário/Aluno)", PALETTE["neutral"], "#757575", fontsize=8, bold=True)

    # Coleta
    add_box(ax, 4.0, 7.0, 2.4, 0.7, "Coleta Mínima\n(login, nome, email, tipo)\nArt. 6º, III — Necessidade", PALETTE["windol_node"], PALETTE["windol_edge"], fontsize=7)
    add_box(ax, 4.0, 5.9, 2.4, 0.7, "Aviso de Privacidade\n(/privacidade)\nArt. 9º — Transparência", PALETTE["windol_node"], PALETTE["windol_edge"], fontsize=7)

    add_arrow(ax, 2.3, 6.7, 2.8, 7.0)
    add_arrow(ax, 2.3, 6.3, 2.8, 5.9)

    # Armazenamento
    add_box(ax, 7.2, 6.5, 2.4, 1.2,
            "Armazenamento Seguro\nSQLite (local)\nSenhas: PBKDF2+Salt\nAcesso controlado por RBAC\nArt. 46 — Segurança", PALETTE["db_node"], PALETTE["db_edge"], fontsize=7)
    add_arrow(ax, 5.2, 7.0, 6.0, 6.8)
    add_arrow(ax, 5.2, 5.9, 6.0, 6.3)

    # Processamento
    add_box(ax, 7.2, 4.8, 2.4, 0.9,
            "Processamento Legítimo\nAbertura/Gestão de Chamados\nFinalidade Declarada\nArt. 6º, I — Finalidade", PALETTE["auth_node"], PALETTE["auth_edge"], fontsize=7)
    add_arrow(ax, 7.2, 5.9, 7.2, 5.25)

    # Logs
    add_box(ax, 7.2, 3.3, 2.4, 0.9,
            "Rastreabilidade\nlogs_auditoria (IP, evento)\nPrestação de Contas\nArt. 6º, X — Responsabilização", PALETTE["security_node"], PALETTE["security_edge"], fontsize=7)
    add_arrow(ax, 7.2, 4.35, 7.2, 3.75)

    # Direitos do titular
    add_box(ax, 3.5, 3.0, 3.0, 2.0,
            "Direitos do Titular (Art. 18)\n──────────────────────────\n• Alterar senha (/alterar_senha)\n• Visualizar chamados próprios\n• Aviso de privacidade (/privacidade)\n──────────────────────────\n[!] Sem módulo formal de\nsolicitação de exclusão\n(limitação declarada)", PALETTE["windol_node"], PALETTE["windol_edge"], fontsize=7)
    add_arrow(ax, 1.3, 6.1, 1.3, 4.0)
    add_arrow(ax, 1.3, 4.0, 2.0, 3.5)

    # Limitações
    add_box(ax, 10.5, 4.0, 1.8, 2.5,
            "[!] Limitações\nDeclaradas\n────────────\n• Sem DPO\n• Sem RIPD\n• Sem módulo\n  de exclusão\n  formal\n• Sem contratos\n  operadores", PALETTE["original_node"], PALETTE["original_edge"], fontsize=7)

    ax.text(6.0, 1.0, "Fluxo implementado cobre os princípios técnicos fundamentais da LGPD, com limitações jurídicas declaradas.", 
            fontsize=7, ha="center", style="italic", color="#546E7A")

    save(fig, "07_fluxo_dados_pessoais_lgpd.png")

# ─────────────────────────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\nGerando PNGs dos diagramas de arquitetura em:\n  {OUT_DIR}\n")
    diagrama_arquitetura_original()
    diagrama_arquitetura_windol()
    diagrama_fluxo_autenticacao()
    diagrama_rbac()
    diagrama_ciclo_chamados()
    diagrama_der()
    diagrama_fluxo_lgpd()
    print(f"\n[OK] 7 diagramas PNG gerados com sucesso em docs/arquitetura/png/")

