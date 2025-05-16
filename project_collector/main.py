import sys
from pathlib import Path
from .parser import get_user_args
from .config import load_config
from .collector import collect_file_content
from .tree import build_tree, print_tree


def main():
    args = get_user_args()
    project_dir = Path(args.directory)

    # 1) Verifica existência do diretório
    if not project_dir.exists():
        print(f"Error: '{project_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # 2) Carrega configuração
    try:
        cfg = load_config(
            project=args.project,
            no_defaults=args.no_defaults
        )
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # 3) Coleta conteúdo e lista de arquivos incluídos
    content, included = collect_file_content(
        directory=str(project_dir),
        cfg=cfg,
        only_tree=args.only_tree,
        verbose=args.verbose
    )

    # 4) Monta árvore de diretórios
    included_set = set(included)
    tree = build_tree(project_dir, included_set)
    tree_str = project_dir.name + "\n" + print_tree(tree)

    # 5) Define caminho de saída fixo
    output_path = Path('pj_output.txt')

    # 6) Escreve no arquivo
    try:
        with output_path.open('w', encoding='utf-8') as out_file:
            # Sempre começa com a árvore
            out_file.write(tree_str)
            # Se não for somente árvore, adiciona o conteúdo
            if not args.only_tree:
                out_file.write("\n\n")
                out_file.write(content)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Coleta completa. Saída salva em '{output_path}'")