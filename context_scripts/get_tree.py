#!/usr/bin/env python3
import os
import sys
import argparse

def listar_diretorios(caminho, prefixo="", ignorar_dirs=None):
    """
    Função recursiva para listar diretórios e subdiretórios.
    Ignora diretórios especificados na lista ignorar_dirs, diretórios que começam com '.', e arquivos que começam com '.'.
    """
    if ignorar_dirs is None:
        ignorar_dirs = set()

    try:
        itens = sorted(os.listdir(caminho))
    except PermissionError:
        print(prefixo + "└── [Permissão Negada]")
        return

    for index, item in enumerate(itens):
        caminho_completo = os.path.join(caminho, item)
        is_dir = os.path.isdir(caminho_completo)
        is_hidden = item.startswith('.')

        # Ignorar arquivos que começam com '.'
        if not is_dir and is_hidden:
            continue  # Pula para o próximo item sem imprimir

        # Ignorar diretórios que começam com '.' ou que estão na lista de ignorados
        if is_dir and (is_hidden or item in ignorar_dirs):
            print(prefixo + ("└── " if index == len(itens) - 1 else "├── ") + f"{item} (Ignorado)")
            continue  # Pula para o próximo item sem listar o conteúdo desse diretório

        # Determinar o conector e o novo prefixo
        if index == len(itens) - 1:
            connector = "└── "
            novo_prefixo = prefixo + "    "
        else:
            connector = "├── "
            novo_prefixo = prefixo + "│   "

        print(prefixo + connector + item)

        if is_dir:
            listar_diretorios(caminho_completo, novo_prefixo, ignorar_dirs=ignorar_dirs)

def main():
    """
    Função principal que inicia a listagem a partir do diretório atual.
    """
    parser = argparse.ArgumentParser(
        description="Gerar estrutura de diretórios do projeto, ignorando pastas e arquivos especificados."
    )
    parser.add_argument(
        "-i", "--ignore", nargs='*', default=['node_modules'],
        help="Listar diretórios a serem ignorados (separados por espaço). Ex: --ignore node_modules .git"
    )
    args = parser.parse_args()

    # Atualizar o conjunto de diretórios a serem ignorados com os argumentos fornecidos
    ignorar_dirs = set(args.ignore)

    nome_projeto = os.path.basename(os.getcwd())
    print(nome_projeto)
    listar_diretorios(os.getcwd(), ignorar_dirs=ignorar_dirs)

if __name__ == "__main__":
    main()
