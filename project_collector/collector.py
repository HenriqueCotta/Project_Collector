import os
from .matcher import matches

def should_include(filepath, cfg):
    # folder patterns
    if cfg['INCLUDE_FOLDER_PATTERNS']:
        parts = filepath.split(os.sep)
        if not any(matches(p, pat) for pat in cfg['INCLUDE_FOLDER_PATTERNS'] for p in parts):
            return False
    # file patterns
    if cfg['INCLUDE_FILE_PATTERNS']:
        name = os.path.basename(filepath)
        if not any(matches(name, pat) for pat in cfg['INCLUDE_FILE_PATTERNS']):
            return False
    # content patterns
    if cfg['INCLUDE_CONTENT_PATTERNS']:
        try:
            text = open(filepath, 'r', encoding='utf-8').read()
        except:
            return False
        if not any(p in text for p in cfg['INCLUDE_CONTENT_PATTERNS']):
            return False
    return True