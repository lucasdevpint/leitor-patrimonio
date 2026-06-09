import customtkinter as ctk
import tkinter as tk
from banco import conectar
from patrimonio import listar_patrimonios
from patrimonio import buscar_por_codigo
from dashboard import dashboard_patrimonio
from tkinter import ttk

conn = conectar()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Sistema Patrimonial UERGS")
app.geometry("800x500")

def abrir_cadastro():
    janela = ctk.CTkToplevel(app)
    janela.title("Cadastro de Patrimônio")
    janela.geometry("300x200")

    label = ctk.CTkLabel(janela, text="Digite o código do patrimônio:")
    label.pack(pady=10)

    entry_codigo = ctk.CTkEntry(janela)
    entry_codigo.pack(pady=10)

    def verificar():
        codigo = entry_codigo.get()

        dados = buscar_por_codigo(conn, codigo)

        if dados:
            print("\n❌ Já existe esse patrimônio:")
            print(dados)
            janela.destroy()
        else:
            janela.destroy()
            abrir_formulario_cadastro(codigo)

    btn = ctk.CTkButton(janela, text="Verificar", command=verificar)
    btn.pack(pady=10)
    
def abrir_formulario_cadastro(codigo):
    janela = ctk.CTkToplevel(app)
    janela.title("Novo Patrimônio")
    janela.geometry("400x600")

    ctk.CTkLabel(janela, text=f"Código: {codigo}").pack(pady=5)

    entradas = {}

    campos = [
        "codigo_secundario",
        "tipo_patrimonio",
        "descricao",
        "marca",
        "modelo",
        "status",
        "local_id",
        "observacoes"
    ]

    for campo in campos:
        ctk.CTkLabel(janela, text=campo).pack()

        entry = ctk.CTkEntry(janela)
        entry.pack()

        entradas[campo] = entry

def salvar():
    dados = (
        codigo,
        entradas["codigo_secundario"].get(),
        entradas["tipo_patrimonio"].get(),
        entradas["descricao"].get(),
        entradas["marca"].get(),
        entradas["modelo"].get(),
        entradas["status"].get(),
        entradas["local_id"].get(),
        entradas["observacoes"].get()
    )

    cadastrar_patrimonio(conn, dados)

    print("✔ Cadastrado com sucesso!")
    janela.destroy()

    btn_salvar = ctk.CTkButton(janela, text="Salvar", command=salvar)
    btn_salvar.pack(pady=20) 

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

def buscar_tabela():
    termo = entry_busca.get()

    tabela.delete(*tabela.get_children())

    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.codigo, p.descricao, l.nome, p.status
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
        WHERE 
            p.codigo LIKE %s OR
            p.descricao LIKE %s OR
            p.marca LIKE %s OR
            p.modelo LIKE %s OR
            p.tipo_patrimonio LIKE %s
    """, (f"%{termo}%", f"%{termo}%", f"%{termo}%", f"%{termo}%", f"%{termo}%"))

    for row in cursor.fetchall():
        tabela.insert("", "end", values=row)

def ao_clicar_tabela(event):

    item = tabela.selection()

    if not item:
        return

    valores = tabela.item(item, "values")

    codigo = valores[0]

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, l.nome AS local
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
        WHERE p.codigo = %s
    """, (codigo,))

    dados = cursor.fetchone()

    abrir_detalhes(dados)

def abrir_detalhes(dados):
    janela = ctk.CTkToplevel(app)
    janela.title("Detalhes do Patrimônio")
    janela.geometry("400x400")

    texto = f"""


Código: {dados['codigo']}
Descrição: {dados['descricao']}
Marca: {dados['marca']}
Modelo: {dados['modelo']}
Tipo: {dados['tipo_patrimonio']}
Status: {dados['status']}
Local: {dados['local']}
Código Secundário: {dados['codigo_secundario']}
"""

    label = ctk.CTkLabel(janela, text=texto, justify="left")
    label.pack(pady=20)
label = ctk.CTkLabel(app, text="Sistema Patrimonial", font=("Arial", 20))
label.pack(pady=10)

entry_busca = ctk.CTkEntry(app, placeholder_text="Buscar patrimônio...")
entry_busca.pack(pady=10)

btn_cadastro = ctk.CTkButton(app, text="Cadastrar Patrimônio", command=abrir_cadastro)
btn_cadastro.pack(pady=5)

btn_buscar = ctk.CTkButton(app, text="Buscar", command=buscar_tabela)
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

tabela.bind("<<TreeviewSelect>>", ao_clicar_tabela)

app.mainloop()

