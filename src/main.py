import sys
import json
from pathlib import Path

from .parser import get_user_args
from .config import load_config, manage_config_commands
from .collector import collect_file_content
from .tree import build_tree, print_tree

# Onde vivem os JSON de configs no pacote
_CONFIGS_BASE      = Path(__file__).parent / 'configs'
_DEFAULTS_DIR     = _CONFIGS_BASE / 'defaults'
_REQUESTS_DIR     = _CONFIGS_BASE / 'requests'
# Arquivo que guarda o config padrão do usuário
_DEFAULT_CONFIG_FILE = Path.home() / '.projcol_config'


def read_default_config() -> str:
    if _DEFAULT_CONFIG_FILE.exists():
        return _DEFAULT_CONFIG_FILE.read_text(encoding='utf-8').strip()
    return ""


def write_default_config(name: str):
    _DEFAULT_CONFIG_FILE.write_text(name, encoding='utf-8')


def clear_default_config():
    if _DEFAULT_CONFIG_FILE.exists():
        _DEFAULT_CONFIG_FILE.unlink()


def list_configs():
    """Mostra todos os configs disponíveis, marcando o atual."""
    defs = {p.stem for p in _DEFAULTS_DIR.glob('*.json')}
    reqs = {p.stem for p in _REQUESTS_DIR.glob('*.json')}
    all_cfgs = sorted(defs.union(reqs))
    current = read_default_config()
    print("Available configs:")
    for cfg in all_cfgs:
        mark = "*" if cfg == current else " "
        print(f"{mark} {cfg}")





def resolve_directory(arg_dir: Path) -> Path:
    """Converte '.' ou caminho relativo/absoluto num Path expandido."""
    return (arg_dir if arg_dir.is_absolute() else Path.cwd() / arg_dir).expanduser()


def choose_config(args) -> str:
    """Retorna o config a usar: override ou o default salvo, ou sai com erro."""
    if args.use_config:
        return args.use_config
    default = read_default_config()
    if default:
        return default
    print("Error: config not specified. Use --use-config or --set-config.", file=sys.stderr)
    sys.exit(1)


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

    # 1) Gerenciamento de configs: list, init, show, clear, set
    if manage_config_commands(args):
        return

    # 2) Execução normal: precisa de directory
    if not args.directory:
        print("Error: directory not specified.", file=sys.stderr)
        sys.exit(1)

    project_dir = resolve_directory(args.directory)
    if not project_dir.is_dir():
        print(f"Error: '{project_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # 3) Escolhe qual config usar
    config_name = choose_config(args)

    # 4) Executa coleta e gera saída
    run_collection(project_dir, config_name, args)


def run():
    main()


if __name__ == '__main__':
    run()
