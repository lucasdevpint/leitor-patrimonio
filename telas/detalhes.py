import customtkinter as ctk
from telas.editar import abrir_edicao


def abrir_detalhes(app, conn, tabela, dados):

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

    label = ctk.CTkLabel(
        janela,
        text=texto,
        justify="left"
    )
    label.pack(pady=20)

    btn_editar = ctk.CTkButton(
        janela,
        text="Editar Patrimônio",
        command=lambda: abrir_edicao(
            app,
            conn,
            tabela,
            dados
        )
    )

    btn_editar.pack(pady=10)