import customtkinter as ctk


def abrir_dashboard(app, conn):

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patrimonio")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE status = 'Em uso'")
    em_uso = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE status = 'Disponível'")
    disponivel = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE status = 'Em manutenção'")
    manutencao = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE status = 'Defeito'")
    defeito = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE status = 'Descarte'")
    descarte = cursor.fetchone()[0]

    janela = ctk.CTkToplevel(app)
    janela.title("Dashboard Patrimonial")
    janela.geometry("400x350")

    titulo = ctk.CTkLabel(
        janela,
        text="Dashboard Patrimonial",
        font=("Arial", 20, "bold")
    )
    titulo.pack(pady=15)

    ctk.CTkLabel(
        janela,
        text=f"Total de Patrimônios: {total}"
    ).pack(pady=5)

    ctk.CTkLabel(
        janela,
        text=f"Em uso: {em_uso}"
    ).pack(pady=5)

    ctk.CTkLabel(
        janela,
        text=f"Disponível: {disponivel}"
    ).pack(pady=5)

    ctk.CTkLabel(
        janela,
        text=f"Em manutenção: {manutencao}"
    ).pack(pady=5)

    ctk.CTkLabel(
        janela,
        text=f"Defeito: {defeito}"
    ).pack(pady=5)

    ctk.CTkLabel(
        janela,
        text=f"Descarte: {descarte}"
    ).pack(pady=5)