import pandas as pd

def exportar_para_excel(conn):
    """
    Exporta tabela de patrimônios para um arquivo Excel.
    conn = conexão com banco de dados
    """

    cursor = conn.cursor()

    query = """
    SELECT codigo, descricao, local, status
    FROM patrimonio
    """

    cursor.execute(query)
    dados = cursor.fetchall()

    colunas = ["Código", "Descrição", "Local", "Status"]

    df = pd.DataFrame(dados, columns=colunas)

    nome_arquivo = "patrimonios.xlsx"
    df.to_excel(nome_arquivo, index=False)

    print(f"\n✔ Exportação concluída: {nome_arquivo}")