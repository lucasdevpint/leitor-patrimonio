import customtkinter as ctk

from patrimonio import editar_patrimonio


def abrir_edicao(app, conn, dados):

    janela = ctk.CTkToplevel(app)
    janela.title("Editar Patrimônio")
    janela.geometry("500x500")

    entradas = {}

    campos = [
        "descricao",
        "marca",
        "modelo",
        "tipo_patrimonio",
        "status"
    ]

    for campo in campos:

        ctk.CTkLabel(
            janela,
            text=campo
        ).pack()

        if campo == "status":

            entry = ctk.CTkComboBox(
                janela,
                values=[
                    "Em uso",
                    "Disponível",
                    "Em manutenção",
                    "Defeito",
                    "Descarte"
                ]
            )

        else:

            entry = ctk.CTkEntry(janela)

        valor = dados.get(campo)

        if valor:

            if campo == "status":
                entry.set(str(valor))
            else:
                entry.insert(0, str(valor))

        entry.pack()

        entradas[campo] = entry

    def salvar():

        novos_dados = {
            "descricao": entradas["descricao"].get(),
            "marca": entradas["marca"].get(),
            "modelo": entradas["modelo"].get(),
            "tipo_patrimonio": entradas["tipo_patrimonio"].get(),
            "status": entradas["status"].get()
        }

        editar_patrimonio(
            conn,
            dados["codigo"],
            novos_dados
        )

        print("✔ Patrimônio atualizado!")

        janela.destroy()

    btn_salvar = ctk.CTkButton(
        janela,
        text="Salvar Alterações",
        command=salvar
    )

    btn_salvar.pack(pady=20)