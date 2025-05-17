import sys
from pathlib import Path
from .parser import get_user_args
from .config import load_config
from .collector import collect_file_content
from .tree import build_tree, print_tree

# Local para armazenar config padrão (perfil)
_DEFAULT_CONFIG_FILE = Path.home() / '.projcol_config'


def _read_default_config() -> str:
    if _DEFAULT_CONFIG_FILE.exists():
        return _DEFAULT_CONFIG_FILE.read_text(encoding='utf-8').strip()
    return ''


def _write_default_config(name: str):
    _DEFAULT_CONFIG_FILE.write_text(name, encoding='utf-8')


def _clear_default_config():
    if _DEFAULT_CONFIG_FILE.exists():
        _DEFAULT_CONFIG_FILE.unlink()


def main():
    args = get_user_args()

    # 1) Gerenciamento de config
    if args.get_config:
        current = _read_default_config()
        if current:
            print(f"Current default config: {current}")
        else:
            print("No default config set.")
        sys.exit(0)
    if args.clear_config:
        _clear_default_config()
        print("Default config cleared.")
        sys.exit(0)
    if args.set_config:
        _write_default_config(args.set_config)
        print(f"Default config set to: {args.set_config}")
        sys.exit(0)

    # 2) Verifica diretório informado
    if not args.directory:
        print("Error: directory not specified.", file=sys.stderr)
        sys.exit(1)

    project_dir = args.directory.resolve()
    if not project_dir.exists():
        print(f"Error: '{project_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # 3) Determina config a usar: override (--use-config) ou default salvo
    project = args.use_config or _read_default_config()
    if not project:
        print("Error: config not specified. Use --use-config or set default with --set-config.", file=sys.stderr)
        sys.exit(1)

    # 4) Carrega configuração
    try:
        cfg = load_config(project=project, no_defaults=args.no_defaults)
    except Exception as e:
        print(f"Error loading configuration for '{project}': {e}", file=sys.stderr)
        sys.exit(1)

    # 5) Coleta conteúdo e lista de arquivos incluídos
    content, included = collect_file_content(
        directory=str(project_dir),
        cfg=cfg,
        only_tree=args.only_tree,
        verbose=args.verbose
    )

    # 6) Monta árvore de diretórios
    included_set = set(included)
    tree = build_tree(project_dir, included_set)
    tree_str = project_dir.name + "\n" + print_tree(tree)

    # 7) Salva saída em pj_output.txt
    output_path = Path('pj_output.txt')
    try:
        with output_path.open('w', encoding='utf-8') as out_file:
            out_file.write(tree_str)
            if not args.only_tree:
                out_file.write("\n\n" + content)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Coleta completa. Saída salva em '{output_path}'")


def run():
    main()


if __name__ == '__main__':
    run()
