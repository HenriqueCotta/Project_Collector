import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, List, Optional
from .filter import PatternGroup, FilterConfig

# Base dos JSONs no pacote
_BASE = Path(__file__).parent.parent  / 'configs'
_DEFAULTS_DIR = _BASE / 'defaults'
_REQUESTS_DIR = _BASE / 'requests'
# Arquivo do default salvo pelo usuário
_DEFAULT_CONFIG_FILE = Path.home() / '.projcol_config'

def load_config(
    project: str,
    no_defaults: bool = False
) -> FilterConfig:
    """
    Carrega configurações para o perfil `project` a partir dos arquivos:
      - configs/defaults/<project>.json  (padrões de ignore)
      - configs/requests/<project>.json  (overrides e includes)

    Cada JSON deve ter seções aninhadas como:
      "DEFAULT_IGNORED_DIRS": {"GLOBS": [...], "REGEX": [...], "SUBSTRINGS": [...]}
      "DEFAULT_IGNORED_FILES": {...}
      "ADDITIONAL_IGNORED_DIRS": {...}
      "ADDITIONAL_IGNORED_FILES": {...}
      "INCLUDE_FOLDER_PATTERNS": {...}
      "INCLUDE_FILE_PATTERNS": {...}
      "INCLUDE_CONTENT_PATTERNS": {"REGEX": [...], "SUBSTRINGS": [...]}  # globs não usados

    Args:
        project: nome do perfil de configuração.
        no_defaults: se True, pula leitura de defaults.
    Returns:
        FilterConfig contendo todos os PatternGroup carregados.
    """
    # Paths dos diretórios de configuração
    base = Path(__file__).parent.parent / 'configs'
    def_file = base / 'defaults' / f'{project}.json'
    req_file = base / 'requests' / f'{project}.json'

    # Helper: parsing de PatternGroup
    def parse_group(obj: Any, allow_globs: bool = True) -> PatternGroup:
        if not isinstance(obj, dict):
            # se não for dict, assume vazio
            obj = {}
        globs      = obj.get('GLOBS', []) if allow_globs else []
        regex      = obj.get('REGEX', [])
        substrings = obj.get('SUBSTRINGS', [])
        return PatternGroup(globs=globs, regex=regex, substrings=substrings)

    # 1) Defaults
    if not no_defaults:
        if not def_file.exists():
            raise FileNotFoundError(f"Default config not found for project '{project}': {def_file}")
        try:
            raw_def = json.loads(def_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in defaults file {def_file}: {e}")
    else:
        raw_def = {}

    default_dirs_group  = parse_group(raw_def.get('DEFAULT_IGNORED_DIRS', {}))
    default_files_group = parse_group(raw_def.get('DEFAULT_IGNORED_FILES', {}))

    # 2) Requests
    if not req_file.exists():
        raise FileNotFoundError(f"Request config not found for project '{project}': {req_file}")
    try:
        raw_req = json.loads(req_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in request file {req_file}: {e}")

    additional_dirs_group  = parse_group(raw_req.get('ADDITIONAL_IGNORED_DIRS', {}))
    additional_files_group = parse_group(raw_req.get('ADDITIONAL_IGNORED_FILES', {}))
    include_folder_group   = parse_group(raw_req.get('INCLUDE_FOLDER_PATTERNS', {}))
    include_file_group     = parse_group(raw_req.get('INCLUDE_FILE_PATTERNS', {}))
    include_content_group  = parse_group(raw_req.get('INCLUDE_CONTENT_PATTERNS', {}), allow_globs=False)

    # 3) Monta e retorna FilterConfig
    return FilterConfig(
        default_ignored_dirs      = default_dirs_group,
        default_ignored_files     = default_files_group,
        additional_ignored_dirs   = additional_dirs_group,
        additional_ignored_files  = additional_files_group,
        include_folder            = include_folder_group,
        include_file              = include_file_group,
        include_content           = include_content_group,
    )
    
def read_default_config() -> str:
    if _DEFAULT_CONFIG_FILE.exists():
        return _DEFAULT_CONFIG_FILE.read_text(encoding='utf-8').strip()
    return "No default config set."


def write_default_config(name: str):
    _DEFAULT_CONFIG_FILE.write_text(name, encoding='utf-8')


def clear_default_config():
    if _DEFAULT_CONFIG_FILE.exists():
        _DEFAULT_CONFIG_FILE.unlink()


def list_configs() -> List[str]:
    """Retorna lista de todos os configs disponíveis (defaults ∪ requests)."""
    defs = {p.stem for p in _DEFAULTS_DIR.glob('*.json')}
    reqs = {p.stem for p in _REQUESTS_DIR.glob('*.json')}
    return sorted(defs.union(reqs))


def init_config(name: str):
    """Cria skeletons em defaults/ e requests/ para o config `name`."""
    skeleton_def = {
        "DEFAULT_IGNORED_DIRS":  {"GLOBS": [], "REGEX": [], "SUBSTRINGS": []},
        "DEFAULT_IGNORED_FILES": {"GLOBS": [], "REGEX": [], "SUBSTRINGS": []}
    }
    skeleton_req = {
        "ADDITIONAL_IGNORED_DIRS":  {"GLOBS": [], "REGEX": [], "SUBSTRINGS": []},
        "ADDITIONAL_IGNORED_FILES": {"GLOBS": [], "REGEX": [], "SUBSTRINGS": []},
        "INCLUDE_FOLDER_PATTERNS":  {"GLOBS": [], "REGEX": [], "SUBSTRINGS": []},
        "INCLUDE_FILE_PATTERNS":    {"GLOBS": [], "REGEX": [], "SUBSTRINGS": []},
        "INCLUDE_CONTENT_PATTERNS": {"REGEX": [], "SUBSTRINGS": []}
    }
    def_file = _DEFAULTS_DIR / f"{name}.json"
    req_file = _REQUESTS_DIR / f"{name}.json"

    if not def_file.exists():
        def_file.parent.mkdir(parents=True, exist_ok=True)
        def_file.write_text(json.dumps(skeleton_def, indent=4), encoding='utf-8')
    if not req_file.exists():
        req_file.parent.mkdir(parents=True, exist_ok=True)
        req_file.write_text(json.dumps(skeleton_req, indent=4), encoding='utf-8')


def choose_config(args) -> str:
    """Retorna o config a usar: override ou o default salvo; ou sai com erro."""
    if args.use_config:
        return args.use_config
    default = read_default_config()
    if default:
        return default
    print("Error: config not specified. Use --use-config or --set-config.", file=sys.stderr)
    sys.exit(1)


def open_config_in_editor(name: Optional[str] = None) -> None:
    """
    Abre no VSCode os arquivos defaults/<name>.json e requests/<name>.json.
    Se name for None ou vazio, usa o padrão salvo em _DEFAULT_CFG_FILE.
    Lança ValueError se algum não existir, ou FileNotFoundError se 'code' não estiver no PATH.
    """
    # determina o nome
    if not name:
        name = read_default_config()
    if not name:
        raise ValueError("Nenhum config padrão definido e nenhum CONFIG informado.")

    def_path = _DEFAULTS_DIR  / f"{name}.json"
    req_path = _REQUESTS_DIR  / f"{name}.json"

    faltantes = [p for p in (def_path, req_path) if not p.exists()]
    if faltantes:
        raise ValueError(f"Arquivos não encontrados: {', '.join(str(p) for p in faltantes)}")

    # chama o VSCode CLI
    try:
        subprocess.run(['code', str(def_path), str(req_path)], check=True)
    except FileNotFoundError:
        # fallback: abre com o app padrão de .json no Windows
        os.startfile(str(def_path))
        os.startfile(str(req_path))
        return
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Falha ao abrir VSCode: {e}")