from banco import conectar
from inventario import iniciar_inventario

from patrimonio import (
    consultar_patrimonio,
    listar_patrimonios,
    alterar_status
)

from movimentacao import (
    movimentar_patrimonio,
    historico_patrimonio
)


while True:

    print("\n==========================")
    print("SISTEMA PATRIMONIAL UERGS")
    print("==========================")
    print("1 - Consultar patrimônio")
    print("2 - Listar patrimônios")
    print("3 - Alterar status")
    print("4 - Movimentar patrimônio")
    print("5 - Histórico do patrimônio")
    print("6 - Inventário")
    print("0 - Sair")

    opcao = input("\nEscolha: ")

    if opcao == "1":
        consultar_patrimonio()

    elif opcao == "2":
        listar_patrimonios()

    elif opcao == "3":
        alterar_status()

    elif opcao == "4":
        movimentar_patrimonio()
    
    elif opcao == "5":
        historico_patrimonio()
    
    elif opcao == "6":
        iniciar_inventario()

    elif opcao == "0":
        print("\nEncerrando...")
        break

    else:
        print("\nOpção inválida.")