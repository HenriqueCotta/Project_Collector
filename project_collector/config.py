import json
from pathlib import Path
from typing import Dict, Any
from .filter import FilterConfig, PatternGroup


def load_config(project_dir: Path, no_defaults: bool = False) -> FilterConfig:
    """
    Carrega configuração aninhada em três camadas:
      - config_defaults.json (DEFAULT_IGNORED_DIRS, DEFAULT_IGNORED_FILES)
      - config.json do projeto (ADDITIONAL_IGNORED_DIRS, ADDITIONAL_IGNORED_FILES,
        INCLUDE_FOLDER_PATTERNS, INCLUDE_FILE_PATTERNS, INCLUDE_CONTENT_PATTERNS)
    Todos no formato:
      "KEY": {"GLOBS": […], "REGEX": […], "SUBSTRINGS": […]}

    Parâmetros:
      project_dir: raiz do projeto
      no_defaults: ignora defaults se True
    Retorna:
      FilterConfig preenchido com PatternGroups
    """
    # Helper de parsing de PatternGroup
    def parse_group(obj: Any, allow_globs: bool = True) -> PatternGroup:
        if not isinstance(obj, dict):
            raise ValueError(f"Expected dict for pattern group, got {type(obj)}")
        globs = obj.get('GLOBS', []) if allow_globs else []
        regex = obj.get('REGEX', [])
        substrings = obj.get('SUBSTRINGS', [])
        return PatternGroup(globs=globs, regex=regex, substrings=substrings)

    # 1) Defaults
    default_path = Path(__file__).parent / 'config_defaults.json'
    if not no_defaults:
        try:
            defaults_raw = json.loads(default_path.read_text(encoding='utf-8'))
        except FileNotFoundError:
            raise FileNotFoundError(f"Defaults not found: {default_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid defaults JSON: {e}")
        default_dirs_group = parse_group(defaults_raw.get('DEFAULT_IGNORED_DIRS', {}))
        default_files_group = parse_group(defaults_raw.get('DEFAULT_IGNORED_FILES', {}))
    else:
        default_dirs_group = parse_group({})
        default_files_group = parse_group({})

    # 2) Request model
    project_cfg = project_dir / 'config.json'
    if project_cfg.exists():
        try:
            req_raw = json.loads(project_cfg.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid project config JSON: {e}")
    else:
        req_raw = {}

    additional_dirs_group   = parse_group(req_raw.get('ADDITIONAL_IGNORED_DIRS', {}))
    additional_files_group  = parse_group(req_raw.get('ADDITIONAL_IGNORED_FILES', {}))
    include_folder_group    = parse_group(req_raw.get('INCLUDE_FOLDER_PATTERNS', {}))
    include_file_group      = parse_group(req_raw.get('INCLUDE_FILE_PATTERNS', {}))
    # Conteúdo não admite globs
    content_raw = req_raw.get('INCLUDE_CONTENT_PATTERNS', {})
    include_content_group   = parse_group(content_raw, allow_globs=False)

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
