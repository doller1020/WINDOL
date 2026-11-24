# Análise de Dependências e Bibliotecas — WINDOL vs Sistema Original

> **Dimensão 21 do Relatório Comparativo (Etapa 3 — Auditoria Comparativa dos Sistemas)**
> Referência: OWASP Top 10:2021 — A06:2021 (Vulnerable and Outdated Components) / CWE-1035 / NIST SSDF RV.1

---

## 1. Sistema Original — Dependências Implícitas

O sistema original (`sistema-chamados-faculdade`) não possuía arquivo `requirements.txt`, tornando as dependências implícitas e não rastreáveis.

| Biblioteca | Versão no original | Como utilizada | Risco identificado |
|---|---|---|---|
| **Flask** | Não declarada (última disponível no ambiente) | Framework web completo | Versão desconhecida; possível uso de versão com vulnerabilidades conhecidas |
| **Werkzeug** | Não declarada (dependência do Flask) | WSGI server + debug mode | Werkzeug com `debug=True` expunha console interativo RCE |
| **sqlite3** | Biblioteca padrão do Python | Conexão com banco | Sem risco na biblioteca; risco na forma de uso (concatenação de strings em queries) |

**Ausências críticas no original:**
- Nenhum arquivo `requirements.txt` → impossibilidade de reprodução controlada do ambiente
- Nenhuma versão pinada → risco de dependências em conflito em redeployments
- Nenhuma verificação de vulnerabilidades conhecidas (CVE) nas bibliotecas

---

## 2. Sistema WINDOL — Dependências Declaradas

O WINDOL atualizado possui `requirements.txt` com dependências explícitas e rastreáveis.

**Arquivo `requirements.txt` (commitado no repositório):**

```
Flask>=3.0.0
Werkzeug>=3.0.0
pytest>=8.0.0
python-docx>=1.1.0
matplotlib>=3.9.0
```

| Biblioteca | Versão mínima | Finalidade | Alinhamento de Segurança |
|---|---|---|---|
| **Flask** | ≥ 3.0.0 | Framework web (rotas, templates, sessões) | Flask 3.x inclui correções de segurança; versão Long-Term Support |
| **Werkzeug** | ≥ 3.0.0 | Hash PBKDF2:SHA-256 (`generate_password_hash` / `check_password_hash`), WSGI | Werkzeug 3.x eleva padrão de hashing para 1.000.000 iterações por padrão (CWE-916) |
| **pytest** | ≥ 8.0.0 | Suíte de testes automatizados (33 casos) | Dependência exclusiva de desenvolvimento; não entra em produção |
| **python-docx** | ≥ 1.1.0 | Geração do documento TCC em formato `.docx` | Dependência auxiliar; sem superfície de ataque em produção |
| **matplotlib** | ≥ 3.9.0 | Geração dos gráficos comparativos e diagramas PNG | Dependência auxiliar; não interage com a aplicação Flask em produção |

---

## 3. Análise Comparativa

| Critério | Sistema Original | Sistema WINDOL | Risco reduzido |
|---|---|---|---|
| Dependências declaradas | Nenhuma (zero `requirements.txt`) | 5 dependências versionadas | A06:2021 Vulnerable and Outdated Components |
| Reprodutibilidade do ambiente | Impossível de reproduzir com exatidão | `pip install -r requirements.txt` garante ambiente idêntico | Risco de inconsistência entre ambientes |
| Versão do Werkzeug | Desconhecida (risco de CVE) | ≥ 3.0.0 (iterações PBKDF2 elevadas) | CWE-916 — algoritmo fraco de hash |
| Modo debug do Flask | `debug=True` hardcoded (Werkzeug RCE exposto) | `debug=False` obrigatório (`web.py` linha 537) | CWE-489 — código de debug ativo |
| Separação dev/prod | Nenhuma separação | `pytest`, `python-docx`, `matplotlib` são dev-only | Superfície de ataque em produção |

---

## 4. Limitações Remanescentes

| Limitação | Descrição | Mitigação sugerida |
|---|---|---|
| Dependências não pinadas a hash | `requirements.txt` usa `>=` em vez de hashes SHA256 do pip-tools | Em produção: `pip-compile --generate-hashes` para garantir integridade das dependências |
| Sem varredura automatizada de CVE | Ausência de ferramenta como `safety`, `pip-audit` ou Dependabot | Integrar `pip audit` ao pipeline CI/CD |
| SQLite como banco de produção | SQLite não é adequado para múltiplos usuários simultâneos em produção | Migrar para PostgreSQL em implantação real |

---

## 5. Como Verificar

```bash
# Instalar dependências em ambiente isolado
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Verificar vulnerabilidades conhecidas (requer pip-audit)
pip install pip-audit
pip-audit

# Executar suíte de testes
pytest tests/ -v
```

---

*Documento gerado em 24/11/2026 — Referência: `docs/seguranca/diagnostico-vulnerabilidades.md` / OWASP A06:2021*
