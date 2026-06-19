# gui/main.py
# Sistema Patrimonial v3 — GUI completa com login, auditoria,
# fotos, manutenção e relatórios.

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import threading

from db.banco import conectar
from core import auth, auditoria as aud_core, patrimonio as pat_core
from core import movimentacao as mov_core, dashboard as dash_core
from core import inventario as inv_core, manutencao as man_core
from core import relatorios as rel_core

# ── Tema ─────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT     = "#3B8BEB"
DANGER     = "#E05252"
WARN       = "#F0A500"
SUCCESS    = "#4CAF7D"
BG_MAIN    = "#1A1A2E"
BG_SIDEBAR = "#16213E"
BG_CARD    = "#0F3460"
TEXT_MUTED = "#8892A4"
SIDEBAR_W  = 210


# ════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ════════════════════════════════════════════════════════════
class TelaLogin(ctk.CTk):
    def __init__(self, conn):
        super().__init__()
        self.conn   = conn
        self.title("Login — Sistema Patrimonial")
        self.geometry("420x380")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="📦", font=ctk.CTkFont(size=48)).pack(pady=(40, 4))
        ctk.CTkLabel(self, text="Sistema Patrimonial",
                     font=ctk.CTkFont(size=18, weight="bold")).pack()
        ctk.CTkLabel(self, text="Faça login para continuar",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(pady=(2, 24))

        form = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14)
        form.pack(padx=40, fill="x")

        self._entry_login = ctk.CTkEntry(form, placeholder_text="Login", height=40)
        self._entry_login.pack(padx=20, pady=(20, 8), fill="x")

        self._entry_senha = ctk.CTkEntry(form, placeholder_text="Senha",
                                          show="•", height=40)
        self._entry_senha.pack(padx=20, pady=(0, 8), fill="x")
        self._entry_senha.bind("<Return>", lambda _: self._entrar())

        self._msg = ctk.CTkLabel(form, text="", text_color=DANGER,
                                  font=ctk.CTkFont(size=11))
        self._msg.pack()

        ctk.CTkButton(form, text="Entrar", height=40, fg_color=ACCENT,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._entrar).pack(padx=20, pady=(4, 20), fill="x")

    def _entrar(self):
        login  = self._entry_login.get().strip()
        senha  = self._entry_senha.get()
        ok, resultado = auth.login(self.conn, login, senha)

        if not ok:
            self._msg.configure(text=resultado)
            return

        aud_core.registrar(self.conn, "LOGIN", f"Usuário {login} entrou no sistema.")
        self.destroy()
        app = AppPrincipal(self.conn)
        app.mainloop()

    def _entrar(self):
        login = self._entry_login.get().strip()
        senha = self._entry_senha.get()
        ok, resultado = auth.login(self.conn, login, senha)
        if not ok:
            self._msg.configure(text=resultado)
            return
        aud_core.registrar(self.conn, "LOGIN", f"Usuário {login} entrou no sistema.")
        self.destroy()
        app = AppPrincipal(self.conn)
        app.mainloop()


# ════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ════════════════════════════════════════════════════════════
class AppPrincipal(ctk.CTk):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.title("Sistema Patrimonial")
        self.geometry("1180x700")
        self.minsize(960, 580)
        self.configure(fg_color=BG_MAIN)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._alertas_ao_iniciar()
        self._build_sidebar()
        self._build_content()
        self.mostrar_frame("dashboard")

    def _alertas_ao_iniciar(self):
        """Mostra alerta de manutenções vencidas logo ao abrir."""
        alertas = man_core.alertas_proximos(self.conn, dias=7)
        if alertas:
            messagebox.showwarning(
                "⚠️ Manutenções Próximas",
                f"Há {len(alertas)} manutenção(ões) prevista(s) para os próximos 7 dias.\n"
                "Acesse a seção Manutenção para mais detalhes."
            )

    # ── Sidebar ──────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=SIDEBAR_W, fg_color=BG_SIDEBAR, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(12, weight=1)

        ctk.CTkLabel(sb, text="📦", font=ctk.CTkFont(size=30)).grid(
            row=0, column=0, pady=(24, 2), padx=20)
        ctk.CTkLabel(sb, text="Patrimônio",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(row=1, column=0)

        usuario = auth.usuario_atual()
        nivel_txt = f"({usuario['nivel']})" if usuario else ""
        ctk.CTkLabel(sb, text=f"{usuario['nome']} {nivel_txt}" if usuario else "",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED
                     ).grid(row=2, column=0, pady=(0, 16))

        self._nav_btns = {}
        nav = [
            ("dashboard",    "📊  Dashboard"),
            ("listagem",     "🗂  Listagem"),
            ("cadastrar",    "➕  Cadastrar"),
            ("movimentacao", "🔀  Movimentar"),
            ("historico",    "📋  Histórico"),
            ("inventario",   "📦  Inventário"),
            ("manutencao",   "🔧  Manutenção"),
            ("busca",        "🔍  Busca"),
            ("relatorios",   "📄  Relatórios"),
            ("auditoria",    "🛡  Auditoria"),
        ]
        # Oculta auditoria para não-admins
        usuario = auth.usuario_atual()
        if usuario and usuario["nivel"] != "admin":
            nav = [n for n in nav if n[0] != "auditoria"]

        for i, (key, label) in enumerate(nav, start=3):
            btn = ctk.CTkButton(
                sb, text=label, anchor="w",
                fg_color="transparent", hover_color=BG_CARD,
                font=ctk.CTkFont(size=12),
                command=lambda k=key: self.mostrar_frame(k)
            )
            btn.grid(row=i, column=0, padx=10, pady=2, sticky="ew")
            self._nav_btns[key] = btn

        # Botão sair
        ctk.CTkButton(
            sb, text="⬅  Sair", fg_color="transparent",
            hover_color=DANGER, font=ctk.CTkFont(size=11),
            command=self._sair
        ).grid(row=13, column=0, padx=10, pady=14, sticky="ew")

    def _sair(self):
        aud_core.registrar(self.conn, "LOGOUT",
                           f"Usuário {auth.usuario_atual()['login']} saiu.")
        auth.logout()
        self.destroy()
        tela = TelaLogin(self.conn)
        tela.mainloop()

    def _highlight_nav(self, key):
        for k, b in self._nav_btns.items():
            b.configure(fg_color=ACCENT if k == key else "transparent")

    # ── Área de conteúdo ─────────────────────────────────────
    def _build_content(self):
        self.content = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self._toast_lbl = ctk.CTkLabel(self.content, text="", height=0,
                                        font=ctk.CTkFont(size=12), corner_radius=6)
        self._toast_lbl.grid(row=0, column=0, sticky="ew", padx=20, pady=(6, 0))
        self._frame_atual = None

    def mostrar_frame(self, key: str):
        self._highlight_nav(key)
        if self._frame_atual:
            self._frame_atual.destroy()
        mapa = {
            "dashboard":    FrameDashboard,
            "listagem":     FrameListagem,
            "cadastrar":    FrameCadastrar,
            "movimentacao": FrameMovimentacao,
            "historico":    FrameHistorico,
            "inventario":   FrameInventario,
            "manutencao":   FrameManutencao,
            "busca":        FrameBusca,
            "relatorios":   FrameRelatorios,
            "auditoria":    FrameAuditoria,
        }
        cls = mapa.get(key, FrameDashboard)
        self._frame_atual = cls(self.content, self)
        self._frame_atual.grid(row=1, column=0, sticky="nsew", padx=20, pady=(8, 20))

    def toast(self, msg: str, tipo: str = "ok"):
        cor = SUCCESS if tipo == "ok" else (WARN if tipo == "warn" else DANGER)
        self._toast_lbl.configure(text=f"  {msg}  ", fg_color=cor,
                                   text_color="white", height=32)
        self.after(3500, lambda: self._toast_lbl.configure(
            text="", fg_color="transparent", height=0))


# ════════════════════════════════════════════════════════════
# BASE FRAME
# ════════════════════════════════════════════════════════════
class _Base(ctk.CTkFrame):
    def __init__(self, master, app: AppPrincipal):
        super().__init__(master, fg_color="transparent")
        self.app  = app
        self.conn = app.conn
        self.grid_columnconfigure(0, weight=1)

    def ok(self, msg):  self.app.toast(msg, "ok")
    def erro(self, msg): self.app.toast(msg, "erro")
    def warn(self, msg): self.app.toast(msg, "warn")

    def _titulo(self, txt):
        ctk.CTkLabel(self, text=txt,
                     font=ctk.CTkFont(size=19, weight="bold")
                     ).grid(row=0, column=0, sticky="w", pady=(0, 10))

    def _pode(self, nivel="editor"):
        if not auth.requer_nivel(nivel):
            self.erro("Sem permissão para esta ação.")
            return False
        return True

    def _tabela(self, parent, cols, dados, row=0):
        frm = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10)
        frm.grid(row=row, column=0, sticky="nsew")
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("P.Treeview",
            background=BG_CARD, foreground="white",
            fieldbackground=BG_CARD, rowheight=28,
            font=("Helvetica", 11))
        style.configure("P.Treeview.Heading",
            background=BG_SIDEBAR, foreground=ACCENT,
            font=("Helvetica", 11, "bold"))
        style.map("P.Treeview", background=[("selected", ACCENT)])

        tree = ttk.Treeview(frm, columns=cols, show="headings", style="P.Treeview")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120, minwidth=60)
        for linha in dados:
            tree.insert("", "end", values=linha)

        sb = ttk.Scrollbar(frm, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        sb.grid(row=0, column=1, sticky="ns")
        return tree, frm

    def _campo(self, form, label, row, col=0, placeholder="", largura=1):
        ctk.CTkLabel(form, text=label, anchor="e", width=150).grid(
            row=row, column=col*2, padx=(14, 6), pady=5, sticky="e")
        e = ctk.CTkEntry(form, placeholder_text=placeholder)
        e.grid(row=row, column=col*2+1, padx=(0, 14), pady=5, sticky="ew",
               columnspan=largura)
        return e


# ════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════
class FrameDashboard(_Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.grid_rowconfigure(2, weight=1)
        self._titulo("📊  Dashboard")
        self._carregar()

    def _carregar(self):
        if not self.conn: return
        s = dash_core.obter_estatisticas(self.conn)

        # Cards de topo
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        cores = {"Em uso": ACCENT, "Disponível": SUCCESS,
                 "Em manutenção": WARN, "Defeito": DANGER, "Descarte": "#888"}

        cards = [
            ("Total", s["total"], "#FFFFFF"),
            ("Valor Total", f"R$ {s['total_valor']:,.2f}".replace(",","X").replace(".",",").replace("X","."), SUCCESS),
            ("Manut. Próximas", s["manutencoes_proximas"], WARN),
            ("Manut. Atrasadas", s["manutencoes_atrasadas"], DANGER),
        ] + [(k, v, cores[k]) for k, v in s["por_status"].items()]

        for i, (label, valor, cor) in enumerate(cards):
            cards_frame.grid_columnconfigure(i, weight=1)
            card = ctk.CTkFrame(cards_frame, fg_color=BG_CARD, corner_radius=12)
            card.grid(row=0, column=i, padx=5, sticky="ew")
            ctk.CTkLabel(card, text=str(valor),
                         font=ctk.CTkFont(size=22, weight="bold"),
                         text_color=cor).grid(row=0, column=0, padx=14, pady=(12, 2))
            ctk.CTkLabel(card, text=label,
                         font=ctk.CTkFont(size=10), text_color=TEXT_MUTED
                         ).grid(row=1, column=0, padx=14, pady=(0, 12))

        # Tabela por local
        ctk.CTkLabel(self, text="Distribuição por Local",
                     font=ctk.CTkFont(size=13, weight="bold")
                     ).grid(row=2, column=0, sticky="w", pady=(4, 4))
        self.grid_rowconfigure(3, weight=1)
        cols = ("Local", "Quantidade")
        linhas = [(r["local"], r["quantidade"]) for r in s["por_local"]]
        _, frm = self._tabela(self, cols, linhas, row=3)
        frm.grid_columnconfigure(0, weight=1)


# ════════════════════════════════════════════════════════════
# LISTAGEM
# ════════════════════════════════════════════════════════════
class FrameListagem(_Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.grid_rowconfigure(1, weight=1)
        self._dados = []
        self._titulo("🗂  Listagem de Patrimônios")
        self._carregar()

    def _carregar(self):
        self._dados = pat_core.listar_patrimonios(self.conn)
        cols  = ("Código", "Tipo", "Descrição", "Marca", "Modelo",
                 "Nº Série", "Status", "Responsável", "Local", "Valor")
        linhas = [(
            r["codigo"], r["tipo_patrimonio"], r["descricao"],
            r["marca"], r["modelo"], r["numero_serie"], r["status"],
            r["responsavel"], r["local"],
            f"R$ {r['valor']:,.2f}" if r["valor"] else ""
        ) for r in self._dados]
        self._tree, frm = self._tabela(self, cols, linhas, row=1)
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_rowconfigure(0, weight=1)
        # Duplo clique abre detalhes
        self._tree.bind("<Double-1>", self._abrir_detalhes)
        ctk.CTkLabel(self, text="💡 Duplo clique em um item para ver detalhes e editar",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED
                     ).grid(row=2, column=0, sticky="w", pady=(4, 0))
        ctk.CTkLabel(self, text=f"{len(self._dados)} item(s)",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED
                     ).grid(row=3, column=0, sticky="w")

    def _abrir_detalhes(self, event):
        sel = self._tree.selection()
        if not sel:
            return
        codigo = self._tree.item(sel[0])["values"][0]
        pat = pat_core.buscar_por_codigo(self.conn, str(codigo))
        if pat:
            JanelaDetalhes(self, self.app, pat)


# ════════════════════════════════════════════════════════════
# JANELA DE DETALHES + EDITAR
# ════════════════════════════════════════════════════════════
class JanelaDetalhes(ctk.CTkToplevel):
    def __init__(self, master, app, pat: dict):
        super().__init__(master)
        self.app  = app
        self.conn = app.conn
        self.pat  = pat
        self.title(f"Patrimônio — {pat['codigo']}")
        self.geometry("620x600")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        self.grab_set()   # bloqueia a janela principal enquanto aberta
        self._modo_edicao = False
        self._build()

    def _build(self):
        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"📦  {self.pat['codigo']}",
                     font=ctk.CTkFont(size=18, weight="bold")
                     ).pack(side="left", padx=20, pady=14)

        # Badge de status
        cores_status = {
            "Em uso": ACCENT, "Disponível": SUCCESS,
            "Em manutenção": WARN, "Defeito": DANGER, "Descarte": "#888"
        }
        cor = cores_status.get(self.pat["status"], ACCENT)
        ctk.CTkLabel(header, text=f"  {self.pat['status']}  ",
                     fg_color=cor, corner_radius=8,
                     font=ctk.CTkFont(size=11, weight="bold")
                     ).pack(side="right", padx=20, pady=14)

        # Corpo com scroll
        self._corpo = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._corpo.pack(fill="both", expand=True, padx=20, pady=10)
        self._corpo.grid_columnconfigure(1, weight=1)

        self._entradas = {}
        self._campos_def = [
            ("Código",           "codigo",           True),
            ("Cód. Secundário",  "codigo_secundario", False),
            ("Tipo",             "tipo_patrimonio",   False),
            ("Descrição",        "descricao",         False),
            ("Marca",            "marca",             False),
            ("Modelo",           "modelo",            False),
            ("Nº Série",         "numero_serie",      False),
            ("Responsável",      "responsavel",       False),
            ("Data Aquisição",   "data_aquisicao",    False),
            ("Valor (R$)",       "valor",             False),
            ("Local",            "local",             True),
            ("Observações",      "observacoes",       False),
        ]

        for i, (label, key, readonly) in enumerate(self._campos_def):
            ctk.CTkLabel(self._corpo, text=label, anchor="e",
                         width=140, text_color=TEXT_MUTED,
                         font=ctk.CTkFont(size=11)
                         ).grid(row=i, column=0, padx=(0, 10), pady=4, sticky="e")

            valor = str(self.pat.get(key) or "")
            entry = ctk.CTkEntry(self._corpo, width=340)
            entry.insert(0, valor)
            entry.configure(state="disabled")
            entry.grid(row=i, column=1, pady=4, sticky="ew")
            self._entradas[key] = (entry, readonly)

        # Status dropdown (oculto até editar)
        ctk.CTkLabel(self._corpo, text="Status", anchor="e",
                     width=140, text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=11)
                     ).grid(row=len(self._campos_def), column=0,
                            padx=(0,10), pady=4, sticky="e")
        self._status_var = ctk.StringVar(value=self.pat["status"])
        self._status_menu = ctk.CTkOptionMenu(
            self._corpo, variable=self._status_var,
            values=pat_core.STATUS_VALIDOS, state="disabled"
        )
        self._status_menu.grid(row=len(self._campos_def), column=1,
                               pady=4, sticky="w")

        # Rodapé com botões
        rodape = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0)
        rodape.pack(fill="x", side="bottom")

        self._btn_editar = ctk.CTkButton(
            rodape, text="✏️  Editar", width=130, fg_color=ACCENT,
            command=self._toggle_edicao
        )
        self._btn_editar.pack(side="left", padx=14, pady=12)

        self._btn_salvar = ctk.CTkButton(
            rodape, text="💾  Salvar", width=130, fg_color=SUCCESS,
            command=self._salvar, state="disabled"
        )
        self._btn_salvar.pack(side="left", padx=4, pady=12)

        ctk.CTkButton(
            rodape, text="Fechar", width=100, fg_color="transparent",
            border_width=1, command=self.destroy
        ).pack(side="right", padx=14, pady=12)

    def _toggle_edicao(self):
        """Alterna entre modo visualização e modo edição."""
        pode = auth.requer_nivel("editor")
        if not pode:
            self.app.toast("Sem permissão para editar.", "erro")
            return

        self._modo_edicao = not self._modo_edicao

        for key, (entry, readonly) in self._entradas.items():
            if not readonly:
                entry.configure(state="normal" if self._modo_edicao else "disabled")

        self._status_menu.configure(
            state="normal" if self._modo_edicao else "disabled"
        )
        self._btn_editar.configure(
            text="❌  Cancelar" if self._modo_edicao else "✏️  Editar",
            fg_color=DANGER if self._modo_edicao else ACCENT
        )
        self._btn_salvar.configure(
            state="normal" if self._modo_edicao else "disabled"
        )

    def _salvar(self):
        dados = {}
        for key, (entry, readonly) in self._entradas.items():
            if not readonly:
                dados[key] = entry.get().strip()
        dados["status"] = self._status_var.get()

        ok, msg = pat_core.editar_patrimonio(self.conn, self.pat["codigo"], dados)
        if ok:
            self.app.toast(msg, "ok")
            # Atualiza pat local e volta para modo visualização
            self.pat.update(dados)
            self._toggle_edicao()
        else:
            self.app.toast(msg, "erro")


# ════════════════════════════════════════════════════════════
# CADASTRAR
# ════════════════════════════════════════════════════════════
class FrameCadastrar(_Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._titulo("➕  Cadastrar Patrimônio")
        self._build()

    def _build(self):
        form = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10)
        form.grid(row=1, column=0, sticky="ew")
        form.grid_columnconfigure((1, 3), weight=1)

        self._e = {}
        campos_esq = [
            ("Código *",          "codigo",           "PAT-0001"),
            ("Cód. Secundário",   "codigo_secundario",""),
            ("Tipo",              "tipo_patrimonio",  "Notebook, Mesa..."),
            ("Descrição",         "descricao",        ""),
            ("Nº Série",          "numero_serie",     ""),
        ]
        campos_dir = [
            ("Marca",             "marca",            ""),
            ("Modelo",            "modelo",           ""),
            ("Responsável",       "responsavel",      ""),
            ("Data Aquisição",    "data_aquisicao",   "AAAA-MM-DD"),
            ("Valor (R$)",        "valor",            "0.00"),
        ]
        for i, (lbl, key, ph) in enumerate(campos_esq):
            self._e[key] = self._campo(form, lbl, i, col=0, placeholder=ph)
        for i, (lbl, key, ph) in enumerate(campos_dir):
            self._e[key] = self._campo(form, lbl, i, col=1, placeholder=ph)

        # Observações (linha inteira)
        ctk.CTkLabel(form, text="Observações", anchor="e", width=150).grid(
            row=len(campos_esq), column=0, padx=(14,6), pady=5, sticky="e")
        self._e["observacoes"] = ctk.CTkEntry(form, placeholder_text="")
        self._e["observacoes"].grid(row=len(campos_esq), column=1,
                                     columnspan=3, padx=(0,14), pady=5, sticky="ew")

        # Status
        ctk.CTkLabel(form, text="Status *", anchor="e", width=150).grid(
            row=len(campos_esq)+1, column=0, padx=(14,6), pady=5, sticky="e")
        self._status = ctk.StringVar(value="Disponível")
        ctk.CTkOptionMenu(form, variable=self._status,
                          values=pat_core.STATUS_VALIDOS
                          ).grid(row=len(campos_esq)+1, column=1, padx=(0,14), sticky="w")

        # Local
        ctk.CTkLabel(form, text="Local", anchor="e", width=150).grid(
            row=len(campos_esq)+2, column=0, padx=(14,6), pady=5, sticky="e")
        self._locais = pat_core.listar_locais(self.conn)
        nomes = [l["nome"] for l in self._locais]
        self._local_var = ctk.StringVar(value=nomes[0] if nomes else "")
        ctk.CTkOptionMenu(form, variable=self._local_var,
                          values=nomes or ["(sem locais)"]
                          ).grid(row=len(campos_esq)+2, column=1, padx=(0,14), sticky="w")

        # Foto
        ctk.CTkLabel(form, text="Foto principal", anchor="e", width=150).grid(
            row=len(campos_esq)+3, column=0, padx=(14,6), pady=5, sticky="e")
        self._foto_path = ctk.StringVar(value="")
        ctk.CTkEntry(form, textvariable=self._foto_path, state="disabled"
                     ).grid(row=len(campos_esq)+3, column=1, padx=(0,6), sticky="ew")
        ctk.CTkButton(form, text="Selecionar", width=100,
                      command=self._escolher_foto
                      ).grid(row=len(campos_esq)+3, column=2, padx=(0,14))

        ctk.CTkButton(self, text="Salvar Patrimônio", fg_color=ACCENT,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._salvar
                      ).grid(row=2, column=0, pady=14, sticky="w")

    def _escolher_foto(self):
        path = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.webp"), ("Todos", "*.*")])
        if path:
            self._foto_path.set(path)

    def _salvar(self):
        if not self._pode("editor"): return
        local_id = next((l["id"] for l in self._locais
                         if l["nome"] == self._local_var.get()), None)
        dados = {k: e.get().strip() for k, e in self._e.items()}
        dados["status"]   = self._status.get()
        dados["local_id"] = local_id

        if not dados.get("codigo"):
            self.erro("O campo Código é obrigatório.")
            return

        ok, msg = pat_core.cadastrar_patrimonio(self.conn, dados)
        if ok:
            self.ok(msg)
            # Salva foto se selecionada
            if self._foto_path.get():
                pat = pat_core.buscar_por_codigo(self.conn, dados["codigo"])
                if pat:
                    pat_core.salvar_foto(self.conn, pat["id"],
                                         self._foto_path.get(), principal=True)
            for e in self._e.values():
                e.delete(0, "end")
            self._foto_path.set("")
        else:
            self.erro(msg)


# ════════════════════════════════════════════════════════════
# MOVIMENTAÇÃO
# ════════════════════════════════════════════════════════════
class FrameMovimentacao(_Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._titulo("🔀  Movimentar Patrimônio")
        self._build()

    def _build(self):
        form = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10)
        form.grid(row=1, column=0, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        self._cod = self._campo(form, "Código do patrimônio *", 0, placeholder="PAT-0001")
        self._locais = pat_core.listar_locais(self.conn)
        nomes = [l["nome"] for l in self._locais]
        ctk.CTkLabel(form, text="Local de destino *", anchor="e", width=150).grid(
            row=1, column=0, padx=(14,6), pady=10, sticky="e")
        self._local_var = ctk.StringVar(value=nomes[0] if nomes else "")
        ctk.CTkOptionMenu(form, variable=self._local_var,
                          values=nomes or ["(sem locais)"]
                          ).grid(row=1, column=1, padx=(0,14), sticky="w")

        ctk.CTkButton(self, text="Registrar Movimentação", fg_color=ACCENT,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._mover
                      ).grid(row=2, column=0, pady=14, sticky="w")

    def _mover(self):
        if not self._pode("editor"): return
        codigo   = self._cod.get().strip()
        local_id = next((l["id"] for l in self._locais
                         if l["nome"] == self._local_var.get()), None)
        if not codigo or not local_id:
            self.erro("Preencha o código e o local de destino.")
            return
        ok, msg = mov_core.movimentar_patrimonio(self.conn, codigo, local_id)
        (self.ok if ok else self.erro)(msg)
        if ok: self._cod.delete(0, "end")


# ════════════════════════════════════════════════════════════
# HISTÓRICO
# ════════════════════════════════════════════════════════════
class FrameHistorico(_Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.grid_rowconfigure(2, weight=1)
        self._titulo("📋  Histórico de Movimentações")
        self._build()

    def _build(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", pady=(0,8))
        barra.grid_columnconfigure(0, weight=1)
        self._cod = ctk.CTkEntry(barra, placeholder_text="Código do patrimônio")
        self._cod.grid(row=0, column=0, sticky="ew", padx=(0,8))
        self._cod.bind("<Return>", lambda _: self._buscar())
        ctk.CTkButton(barra, text="Buscar", width=90, fg_color=ACCENT,
                      command=self._buscar).grid(row=0, column=1)
        self._res = ctk.CTkFrame(self, fg_color="transparent")
        self._res.grid(row=2, column=0, sticky="nsew")
        self._res.grid_columnconfigure(0, weight=1)
        self._res.grid_rowconfigure(0, weight=1)

    def _buscar(self):
        for w in self._res.winfo_children(): w.destroy()
        cod = self._cod.get().strip()
        if not cod: self.erro("Informe o código."); return
        hist = mov_core.historico_patrimonio(self.conn, cod)
        if not hist:
            ctk.CTkLabel(self._res, text="Nenhuma movimentação encontrada.",
                         text_color=TEXT_MUTED).grid(pady=20)
            return
        cols = ("Data/Hora", "Origem", "Destino")
        linhas = [(str(h["data_movimentacao"])[:16], h["origem"], h["destino"])
                  for h in hist]
        _, frm = self._tabela(self._res, cols, linhas, row=0)
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_rowconfigure(0, weight=1)


# ════════════════════════════════════════════════════════════
# INVENTÁRIO
# ════════════════════════════════════════════════════════════
class FrameInventario(_Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.grid_rowconfigure(2, weight=1)
        self._titulo("📦  Inventário por Local")
        self._build()

    def _build(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", pady=(0,8))
        self._locais = pat_core.listar_locais(self.conn)
        nomes = ["Todos os locais"] + [l["nome"] for l in self._locais]
        self._local_var = ctk.StringVar(value="Todos os locais")
        ctk.CTkOptionMenu(barra, variable=self._local_var, values=nomes,
                          width=240, command=lambda _: self._carregar()
                          ).grid(row=0, column=0, padx=(0,8))
        ctk.CTkButton(barra, text="Atualizar", width=90, fg_color=ACCENT,
                      command=self._carregar).grid(row=0, column=1)
        self._tbl_frm = ctk.CTkFrame(self, fg_color="transparent")
        self._tbl_frm.grid(row=2, column=0, sticky="nsew")
        self._tbl_frm.grid_columnconfigure(0, weight=1)
        self._tbl_frm.grid_rowconfigure(0, weight=1)
        self._carregar()

    def _carregar(self):
        for w in self._tbl_frm.winfo_children(): w.destroy()
        nome = self._local_var.get()
        lid  = next((l["id"] for l in self._locais if l["nome"] == nome), None)
        dados = inv_core.listar_por_local(self.conn, lid)
        cols  = ("Local", "Código", "Descrição", "Tipo", "Status", "Responsável")
        linhas = [(r["local"], r["codigo"], r["descricao"],
                   r["tipo_patrimonio"], r["status"], r["responsavel"]) for r in dados]
        _, frm = self._tabela(self._tbl_frm, cols, linhas, row=0)
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_rowconfigure(0, weight=1)


# ════════════════════════════════════════════════════════════
# MANUTENÇÃO
# ════════════════════════════════════════════════════════════
class FrameManutencao(_Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.grid_rowconfigure(2, weight=1)
        self._titulo("🔧  Manutenção Programada")
        self._build()

    def _build(self):
        # Abas
        self._aba = ctk.StringVar(value="pendentes")
        abas = ctk.CTkFrame(self, fg_color="transparent")
        abas.grid(row=1, column=0, sticky="ew", pady=(0,8))
        for key, label in [("pendentes","Pendentes"), ("agendar","Agendar Nova"),
                            ("concluir","Registrar Conclusão")]:
            ctk.CTkButton(abas, text=label, width=160, height=32,
                          fg_color=ACCENT if self._aba.get()==key else BG_CARD,
                          command=lambda k=key: self._trocar_aba(k)
                          ).pack(side="left", padx=4)

        self._corpo = ctk.CTkFrame(self, fg_color="transparent")
        self._corpo.grid(row=2, column=0, sticky="nsew")
        self._corpo.grid_columnconfigure(0, weight=1)
        self._corpo.grid_rowconfigure(0, weight=1)
        self._mostrar_pendentes()

    def _trocar_aba(self, key):
        self._aba.set(key)
        for w in self._corpo.winfo_children(): w.destroy()
        {"pendentes": self._mostrar_pendentes,
         "agendar":   self._mostrar_agendar,
         "concluir":  self._mostrar_concluir}[key]()

    def _mostrar_pendentes(self):
        dados = man_core.listar_pendentes(self.conn)
        cols  = ("Código", "Patrimônio", "Local", "Tipo",
                 "Descrição", "Data Prevista", "Responsável", "Dias Restantes")
        linhas = [(r["codigo"], r["patrimonio"], r["local"], r["tipo"],
                   r["descricao"], str(r["data_prevista"]),
                   r["responsavel"], r["dias_restantes"]) for r in dados]
        _, frm = self._tabela(self._corpo, cols, linhas, row=0)
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_rowconfigure(0, weight=1)

    def _mostrar_agendar(self):
        form = ctk.CTkFrame(self._corpo, fg_color=BG_CARD, corner_radius=10)
        form.grid(row=0, column=0, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        self._am = {}
        campos = [
            ("Código do Patrimônio *", "codigo",       "PAT-0001"),
            ("Descrição",              "descricao",    ""),
            ("Data Prevista *",        "data_prevista","AAAA-MM-DD"),
            ("Responsável",            "responsavel",  ""),
            ("Custo Estimado",         "custo",        "0.00"),
        ]
        for i, (lbl, key, ph) in enumerate(campos):
            ctk.CTkLabel(form, text=lbl, anchor="e", width=180).grid(
                row=i, column=0, padx=(14,6), pady=6, sticky="e")
            e = ctk.CTkEntry(form, placeholder_text=ph)
            e.grid(row=i, column=1, padx=(0,14), pady=6, sticky="ew")
            self._am[key] = e

        ctk.CTkLabel(form, text="Tipo *", anchor="e", width=180).grid(
            row=len(campos), column=0, padx=(14,6), pady=6, sticky="e")
        self._am_tipo = ctk.StringVar(value="preventiva")
        ctk.CTkOptionMenu(form, variable=self._am_tipo,
                          values=man_core.TIPOS
                          ).grid(row=len(campos), column=1, padx=(0,14), sticky="w")

        ctk.CTkButton(self._corpo, text="Agendar Manutenção", fg_color=ACCENT,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._agendar
                      ).grid(row=1, column=0, pady=12, sticky="w")

    def _agendar(self):
        if not self._pode("editor"): return
        codigo = self._am["codigo"].get().strip()
        pat = pat_core.buscar_por_codigo(self.conn, codigo)
        if not pat:
            self.erro("Patrimônio não encontrado.")
            return
        dados = {k: e.get().strip() for k, e in self._am.items() if k != "codigo"}
        dados["tipo"] = self._am_tipo.get()
        ok, msg = man_core.agendar(self.conn, pat["id"], dados)
        (self.ok if ok else self.erro)(msg)

    def _mostrar_concluir(self):
        form = ctk.CTkFrame(self._corpo, fg_color=BG_CARD, corner_radius=10)
        form.grid(row=0, column=0, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="ID da Manutenção *", anchor="e", width=180).grid(
            row=0, column=0, padx=(14,6), pady=8, sticky="e")
        self._c_id = ctk.CTkEntry(form, placeholder_text="ID da manutenção")
        self._c_id.grid(row=0, column=1, padx=(0,14), pady=8, sticky="ew")

        ctk.CTkLabel(form, text="Data Realizada *", anchor="e", width=180).grid(
            row=1, column=0, padx=(14,6), pady=8, sticky="e")
        self._c_data = ctk.CTkEntry(form, placeholder_text="AAAA-MM-DD")
        self._c_data.grid(row=1, column=1, padx=(0,14), pady=8, sticky="ew")

        ctk.CTkLabel(form, text="Custo Real", anchor="e", width=180).grid(
            row=2, column=0, padx=(14,6), pady=8, sticky="e")
        self._c_custo = ctk.CTkEntry(form, placeholder_text="0.00")
        self._c_custo.grid(row=2, column=1, padx=(0,14), pady=8, sticky="ew")

        ctk.CTkButton(self._corpo, text="Registrar como Concluída", fg_color=SUCCESS,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._concluir
                      ).grid(row=1, column=0, pady=12, sticky="w")

    def _concluir(self):
        if not self._pode("editor"): return
        mid  = self._c_id.get().strip()
        data = self._c_data.get().strip()
        custo = self._c_custo.get().strip() or None
        if not mid or not data:
            self.erro("Informe o ID e a data realizada.")
            return
        ok, msg = man_core.registrar_realizada(self.conn, int(mid), data, custo)
        (self.ok if ok else self.erro)(msg)


# ════════════════════════════════════════════════════════════
# BUSCA
# ════════════════════════════════════════════════════════════
class FrameBusca(_Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.grid_rowconfigure(2, weight=1)
        self._titulo("🔍  Busca Avançada")
        self._build()

    def _build(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", pady=(0,8))
        barra.grid_columnconfigure(0, weight=1)
        self._termo = ctk.CTkEntry(
            barra, placeholder_text="Buscar por código, descrição, marca, modelo, responsável ou Nº série...")
        self._termo.grid(row=0, column=0, sticky="ew", padx=(0,8))
        self._termo.bind("<Return>", lambda _: self._buscar())
        ctk.CTkButton(barra, text="Buscar", width=90, fg_color=ACCENT,
                      command=self._buscar).grid(row=0, column=1)
        self._res = ctk.CTkFrame(self, fg_color="transparent")
        self._res.grid(row=2, column=0, sticky="nsew")
        self._res.grid_columnconfigure(0, weight=1)
        self._res.grid_rowconfigure(0, weight=1)

    def _buscar(self):
        for w in self._res.winfo_children(): w.destroy()
        t = self._termo.get().strip()
        if not t: self.erro("Digite algo para buscar."); return
        res = pat_core.buscar_patrimonios(self.conn, t)
        if not res:
            ctk.CTkLabel(self._res, text="Nenhum resultado.",
                         text_color=TEXT_MUTED).grid(pady=20); return
        cols  = ("Código","Tipo","Descrição","Marca","Modelo","Status","Responsável","Local")
        linhas = [(r["codigo"],r["tipo_patrimonio"],r["descricao"],r["marca"],
                   r["modelo"],r["status"],r["responsavel"],r["local"]) for r in res]
        _, frm = self._tabela(self._res, cols, linhas, row=0)
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(self._res, text=f'{len(res)} resultado(s) para "{t}"',
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED
                     ).grid(row=1, column=0, sticky="w", pady=(4,0))


# ════════════════════════════════════════════════════════════
# RELATÓRIOS
# ════════════════════════════════════════════════════════════
class FrameRelatorios(_Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._titulo("📄  Relatórios e Exportação")
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        card.grid(row=1, column=0, sticky="ew", pady=8)

        ctk.CTkLabel(card, text="Relatório Completo (Excel)",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).grid(row=0, column=0, padx=20, pady=(16,4), sticky="w")
        ctk.CTkLabel(card,
                     text="Gera um arquivo .xlsx com 4 abas:\n"
                          "• Todos os Patrimônios\n"
                          "• Resumo por Status\n"
                          "• Manutenções Pendentes\n"
                          "• Log de Auditoria",
                     justify="left", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=12)
                     ).grid(row=1, column=0, padx=20, pady=(0,12), sticky="w")

        self._btn = ctk.CTkButton(
            card, text="📥  Gerar Relatório Excel", fg_color=ACCENT,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._gerar
        )
        self._btn.grid(row=2, column=0, padx=20, pady=(0,20), sticky="w")

        self._resultado = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=11))
        self._resultado.grid(row=3, column=0, padx=20, pady=(0,16), sticky="w")

    def _gerar(self):
        if not self._pode("editor"): return
        self._btn.configure(state="disabled", text="Gerando...")

        def _run():
            caminho, msg = rel_core.gerar_relatorio_completo(self.conn)
            self.after(0, lambda: self._pos_gerar(caminho, msg))

        threading.Thread(target=_run, daemon=True).start()

    def _pos_gerar(self, caminho, msg):
        self._btn.configure(state="normal", text="📥  Gerar Relatório Excel")
        if caminho:
            aud_core.registrar(self.conn, "EXPORTAR",
                               f"Relatório Excel gerado: {os.path.basename(caminho)}",
                               "relatorios")
            self.ok(msg)
            self._resultado.configure(
                text=f"Arquivo salvo em:\n{caminho}", text_color=SUCCESS)
        else:
            self.erro(msg)


# ════════════════════════════════════════════════════════════
# AUDITORIA (só admin)
# ════════════════════════════════════════════════════════════
class FrameAuditoria(_Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.grid_rowconfigure(2, weight=1)
        self._titulo("🛡  Log de Auditoria")
        self._build()

    def _build(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", pady=(0,8))
        self._filtro_usuario = ctk.CTkEntry(barra, placeholder_text="Filtrar por usuário", width=200)
        self._filtro_usuario.grid(row=0, column=0, padx=(0,8))
        acoes = ["", "LOGIN", "LOGOUT", "CADASTRAR", "EDITAR",
                 "MOVER", "ALTERAR_STATUS", "EXPORTAR", "MANUTENCAO_AGENDAR"]
        self._filtro_acao = ctk.StringVar(value="")
        ctk.CTkOptionMenu(barra, variable=self._filtro_acao,
                          values=acoes, width=180).grid(row=0, column=1, padx=(0,8))
        ctk.CTkButton(barra, text="Filtrar", width=90, fg_color=ACCENT,
                      command=self._carregar).grid(row=0, column=2)

        self._tbl = ctk.CTkFrame(self, fg_color="transparent")
        self._tbl.grid(row=2, column=0, sticky="nsew")
        self._tbl.grid_columnconfigure(0, weight=1)
        self._tbl.grid_rowconfigure(0, weight=1)
        self._carregar()

    def _carregar(self):
        for w in self._tbl.winfo_children(): w.destroy()
        logs = aud_core.listar_logs(
            self.conn,
            usuario_login=self._filtro_usuario.get().strip() or None,
            acao=self._filtro_acao.get() or None
        )
        cols   = ("Data/Hora", "Usuário", "Ação", "Tabela", "ID", "Descrição")
        linhas = [(str(l["criado_em"])[:16], l["usuario_login"], l["acao"],
                   l["tabela"], l["registro_id"], l["descricao"]) for l in logs]
        _, frm = self._tabela(self._tbl, cols, linhas, row=0)
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_rowconfigure(0, weight=1)


# ════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        conn = conectar()
    except ConnectionError as e:
        import tkinter as tk
        from tkinter import messagebox
        r = tk.Tk(); r.withdraw()
        messagebox.showerror("Erro de Conexão", str(e))
        r.destroy()
        sys.exit(1)

    tela = TelaLogin(conn)
    tela.mainloop()
