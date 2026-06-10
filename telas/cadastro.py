import customtkinter as ctk
from banco import conectar
from patrimonio import (
    buscar_por_codigo,
    cadastrar_patrimonio
)

def abrir_cadastro(app, conn):
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
            janela.destroy()
            mostrar_patrimonio_existente(app,dados)
        else:
            janela.destroy()
            abrir_formulario_cadastro(app, conn, codigo)
            
    btn = ctk.CTkButton(janela, text="Verificar", command=verificar)
    btn.pack(pady=10)


def mostrar_patrimonio_existente(app,dados):
    janela = ctk.CTkToplevel(app)
    janela.title("Patrimônio já cadastrado")
    janela.geometry("500x350")

    texto = f"""
  Código: {dados['codigo']}

Código Secundário: {dados.get('codigo_secundario')}

Descrição: {dados.get('descricao')}

Marca: {dados.get('marca')}

Modelo: {dados.get('modelo')}

Tipo: {dados.get('tipo_patrimonio')}

Status: {dados.get('status')}
"""

    label = ctk.CTkLabel(
        janela,
        text=texto,
        justify="left"
    )
    label.pack(padx=20, pady=20)

    btn = ctk.CTkButton(
        janela,
        text="Fechar",
        command=janela.destroy
    )
    btn.pack(pady=10)



def abrir_formulario_cadastro(app, conn, codigo):
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
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nome
        FROM locais
        WHERE tipo IN ('setor', 'laboratorio')
        ORDER BY nome
    """)

    locais = cursor.fetchall()

    locais_dict = {}

    for local in locais:
        locais_dict[local["nome"]] = local["id"]
    for campo in campos:

        ctk.CTkLabel(janela, text=campo).pack()

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

            entry.set("Em uso")
       
        elif campo == "tipo_patrimonio":

            entry = ctk.CTkComboBox(
                janela,
                values=[
                    "UERGS",
                    "Estado RS",
                    "UERGS + Estado RS",
                    "Doação",
                    "Outro"
                ]
            )

            entry.set("UERGS") 
        elif campo == "local_id":

            entry = ctk.CTkComboBox(
                janela,
                values=list(locais_dict.keys())
            )

            entry.set(list(locais_dict.keys())[0])    
        else:

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
           locais_dict[
           entradas["local_id"].get()
           ],
           entradas["observacoes"].get()
        )

        cadastrar_patrimonio(conn, dados)

        print("✔ Cadastrado com sucesso!")
        janela.destroy()


    btn_salvar = ctk.CTkButton(
        janela,
        text="Salvar",
        command=salvar
    )

    btn_salvar.pack(pady=20)
