import re
import fnmatch
from pathlib import Path
from dataclasses import dataclass
from typing import List, Pattern

@dataclass
class PatternGroup:
    globs: List[str]
    regex: List[str]
    substrings: List[str]

    @property
    def regex_patterns(self) -> List[Pattern]:
        return [re.compile(r) for r in self.regex]

@dataclass
class FilterConfig:
    default_ignored_dirs: PatternGroup
    default_ignored_files: PatternGroup
    additional_ignored_dirs: PatternGroup
    additional_ignored_files: PatternGroup
    include_folder: PatternGroup
    include_file: PatternGroup
    include_content: PatternGroup

class Filter:
    """
    Filtra arquivos e pastas com base num FilterConfig já validado.
    """
    def __init__(self, cfg: FilterConfig):
        # Combina defaults + additional para exclusão de diretórios
        self.exclude_dirs = PatternGroup(
            globs=cfg.default_ignored_dirs.globs + cfg.additional_ignored_dirs.globs,
            regex=cfg.default_ignored_dirs.regex + cfg.additional_ignored_dirs.regex,
            substrings=cfg.default_ignored_dirs.substrings + cfg.additional_ignored_dirs.substrings
        )
        # Combina defaults + additional para exclusão de arquivos
        self.exclude_files = PatternGroup(
            globs=cfg.default_ignored_files.globs + cfg.additional_ignored_files.globs,
            regex=cfg.default_ignored_files.regex + cfg.additional_ignored_files.regex,
            substrings=cfg.default_ignored_files.substrings + cfg.additional_ignored_files.substrings
        )
        # Includes diretos para pastas e arquivos
        self.include_folder = cfg.include_folder
        self.include_file = cfg.include_file
        # Conteúdo só usa regex e substrings, ignorando qualquer globs
        self.include_content = PatternGroup(
            globs=[],
            regex=cfg.include_content.regex,
            substrings=cfg.include_content.substrings
        )

    def _match(self, name: str, group: PatternGroup) -> bool:
        # Glob patterns
        for pat in group.globs:
            if fnmatch.fnmatch(name, pat):
                return True
        # Regex patterns
        for pat in group.regex_patterns:
            if pat.search(name):
                return True
        # Substring patterns
        for sub in group.substrings:
            if sub in name:
                return True
        return False

    def include_path(self, path: Path, *, check_content: bool = False) -> bool:
        # 0) Exclui diretórios com base em segmentos do caminho
        for seg in path.parts:
            if self._match(seg, self.exclude_dirs):
                return False
        # 1) Exclui arquivos cujo nome bate em padrões de exclusão
        if path.is_file() and self._match(path.name, self.exclude_files):
            return False
        # 2) Se há padrões de pasta para incluir, exige batida em algum segmento
        if (self.include_folder.globs or self.include_folder.regex or self.include_folder.substrings):
            if not any(self._match(seg, self.include_folder) for seg in path.parts):
                return False
        # 3) Se há padrões de arquivo para incluir, exige batida no nome
        if path.is_file() and (self.include_file.globs or self.include_file.regex or self.include_file.substrings):
            if not self._match(path.name, self.include_file):
                return False
        # 4) Checagem de conteúdo: só regex e substrings, sem glob
        if check_content and (self.include_content.regex or self.include_content.substrings):
            try:
                text = path.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                return False
            # Regex content
            if any(p.search(text) for p in self.include_content.regex_patterns):
                return True
            # Substrings content
            if any(sub in text for sub in self.include_content.substrings):
                return True
            return False
        return True
