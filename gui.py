import customtkinter as ctk
import tkinter as tk
from banco import conectar
from patrimonio import listar_patrimonios
from busca import buscar_patrimonio
from dashboard import dashboard_patrimonio
from tkinter import ttk

conn = conectar()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Sistema Patrimonial UERGS")
app.geometry("800x500")

def buscar():
    termo = entry_busca.get()
    print("\n--- BUSCA ---")
    buscar_patrimonio(conn, termo)

def abrir_dashboard():
    dashboard_patrimonio(conn)

def listar():
    tabela.delete(*tabela.get_children())

    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.codigo, p.descricao, l.nome, p.status
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
    """)

    for row in cursor.fetchall():
        tabela.insert("", "end", values=row)

def carregar_tabela():
    for item in tabela.get_children():
        tabela.delete(item)

    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.codigo, p.descricao, l.nome, p.status
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
    """)

    for row in cursor.fetchall():
        tabela.insert("", "end", values=row)

label = ctk.CTkLabel(app, text="Sistema Patrimonial", font=("Arial", 20))
label.pack(pady=10)

entry_busca = ctk.CTkEntry(app, placeholder_text="Buscar patrimônio...")
entry_busca.pack(pady=10)

btn_buscar = ctk.CTkButton(app, text="Buscar", command=buscar)
btn_buscar.pack(pady=5)

btn_listar = ctk.CTkButton(app, text="Listar Todos", command=listar)
btn_listar.pack(pady=5)

btn_dashboard = ctk.CTkButton(app, text="Dashboard", command=abrir_dashboard)
btn_dashboard.pack(pady=5)

tabela = ttk.Treeview(app, columns=("codigo", "descricao", "local", "status"), show="headings")

tabela.heading("codigo", text="Código")
tabela.heading("descricao", text="Descrição")
tabela.heading("local", text="Local")
tabela.heading("status", text="Status")

tabela.pack(fill="both", expand=True, pady=20)

btn_tabela = ctk.CTkButton(app, text="Carregar Tabela", command=carregar_tabela)
btn_tabela.pack(pady=5)

app.mainloop()

