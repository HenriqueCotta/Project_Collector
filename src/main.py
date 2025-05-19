import sys
from pathlib import Path

from .parser import get_user_args
from .config import (
    choose_config,
    load_config,
    read_default_config,
    write_default_config,
    clear_default_config,
    list_configs,
    init_config,
)
from .collector import collect_file_content
from .tree import build_tree, print_tree


def resolve_directory(arg_dir: Path) -> Path:
    """Converte '.' ou caminho relativo/absoluto num Path expandido."""
    return (arg_dir if arg_dir.is_absolute() else Path.cwd() / arg_dir).expanduser()


def handle_config_commands(args) -> bool:
    """
    Trata os comandos de configuração (--list-configs, --init-config,
    --get-config, --clear-config, --set-config). Retorna True se
    executou alguma ação e deve sair ali mesmo.
    """
    if args.list_configs:
        current = read_default_config()
        print("Available configs:")
        for cfg in list_configs():
            mark = "*" if cfg == current else " "
            print(f"{mark} {cfg}")
        return True

    if args.init_config:
        init_config(args.init_config)
        return True

    if args.show_config:
        cur = read_default_config()
        print(cur or "No default config set.")
        return True

    if args.clear_config:
        clear_default_config()
        print("Default config cleared.")
        return True

    if args.set_config:
        write_default_config(args.set_config)
        print(f"Default config set to: {args.set_config}")
        return True

    return False

def run_collection(project_dir: Path, config_name: str, args):
    """Executa load_config → collect_file_content → build_tree → escreve pj_output.txt."""
    try:
        cfg = load_config(project=config_name, no_defaults=args.no_defaults)
    except Exception as e:
        print(f"Error loading config '{config_name}': {e}", file=sys.stderr)
        sys.exit(1)

    content, included = collect_file_content(
        directory=str(project_dir),
        cfg=cfg,
        only_tree=args.only_tree,
        verbose=args.verbose
    )

    tree = build_tree(project_dir, set(included))
    tree_str = project_dir.name + "\n" + print_tree(tree)

    out = Path('pj_output.txt')
    try:
        with out.open('w', encoding='utf-8', newline='\n') as f:
            f.write(tree_str)
            if not args.only_tree:
                f.write("\n\n")
                f.write(content)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Coleta completa. Saída salva em '{out}'")


def main():
    args = get_user_args()

    # 1) Gerenciamento de configs via funções de config.py
    if handle_config_commands(args):
        return

    # 2) Execução normal: precisa de directory
    if not args.directory:
        print("Error: directory not specified.", file=sys.stderr)
        sys.exit(1)

    project_dir = resolve_directory(args.directory)
    if not project_dir.is_dir():
        print(f"Error: '{project_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # 3) Escolhe qual config usar e executa a coleta
    config_name = choose_config(args)
    run_collection(project_dir, config_name, args)


def run():
    main()


if __name__ == '__main__':
    run()
