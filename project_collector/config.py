import os, json
from pathlib import Path

def load_config(project_root: str, no_defaults=False):
    base = Path(__file__).parent.parent
    defaults_path = base / 'config_defaults.json'
    cfg = {}
    if not no_defaults and defaults_path.exists():
        cfg.update(json.loads(defaults_path.read_text()))
    project_cfg = Path(project_root) / 'config.json'
    if project_cfg.exists():
        cfg.update(json.loads(project_cfg.read_text()))
    return cfg