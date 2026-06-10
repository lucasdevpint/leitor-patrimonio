import customtkinter as ctk
from tkinter import ttk

from banco import conectar

from telas.cadastro import abrir_cadastro
from telas.detalhes import abrir_detalhes
from telas.tabela import (
    listar,
    carregar_tabela,
    buscar_tabela,
    ao_clicar_tabela
)

from telas.dashboard import abrir_dashboard

conn = conectar()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Sistema Patrimonial UERGS")
app.geometry("800x500")


label = ctk.CTkLabel(app, text="Sistema Patrimonial", font=("Arial", 20))
label.pack(pady=10)

entry_busca = ctk.CTkEntry(app, placeholder_text="Buscar patrimônio...")
entry_busca.pack(pady=10)

btn_cadastro = ctk.CTkButton(
    app,
    text="Cadastrar Patrimônio",
    command=lambda: abrir_cadastro(app, conn)
)
btn_cadastro.pack(pady=5)

btn_buscar = ctk.CTkButton(
    app,
    text="Buscar",
    command=lambda: buscar_tabela(conn, tabela, entry_busca)
)
btn_buscar.pack(pady=5)


btn_listar = ctk.CTkButton(
    app,
    text="Listar Todos",
    command=lambda: listar(conn, tabela)
)
btn_listar.pack(pady=5)

btn_dashboard = ctk.CTkButton(
    app,
    text="Dashboard",
    command=lambda: abrir_dashboard(app, conn)
)
btn_dashboard.pack(pady=5)

tabela = ttk.Treeview(app, columns=("codigo", "descricao", "local", "status"), show="headings")

tabela.heading("codigo", text="Código")
tabela.heading("descricao", text="Descrição")
tabela.heading("local", text="Local")
tabela.heading("status", text="Status")

tabela.pack(fill="both", expand=True, pady=20)

btn_tabela = ctk.CTkButton(
    app,
    text="Carregar Tabela",
    command=lambda: carregar_tabela(conn, tabela)
)
btn_tabela.pack(pady=5)

tabela.bind(
    "<<TreeviewSelect>>",
    lambda event: ao_clicar_tabela(event, app, conn, tabela)
)

app.mainloop()

