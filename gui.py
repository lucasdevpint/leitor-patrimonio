import customtkinter as ctk
from banco import conectar
from patrimonio import listar_patrimonios
from busca import buscar_patrimonio
from dashboard import dashboard_patrimonio

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
    listar_patrimonios(conn)

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

app.mainloop()