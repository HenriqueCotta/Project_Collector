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
    def __init__(self, cfg: FilterConfig):
        # Combina defaults + additional para exclusão\        
        self.exclude_dirs = PatternGroup(
            globs=cfg.default_ignored_dirs.globs + cfg.additional_ignored_dirs.globs,
            regex=cfg.default_ignored_dirs.regex + cfg.additional_ignored_dirs.regex,
            substrings=cfg.default_ignored_dirs.substrings + cfg.additional_ignored_dirs.substrings
        )
        self.exclude_files = PatternGroup(
            globs=cfg.default_ignored_files.globs + cfg.additional_ignored_files.globs,
            regex=cfg.default_ignored_files.regex + cfg.additional_ignored_files.regex,
            substrings=cfg.default_ignored_files.substrings + cfg.additional_ignored_files.substrings
        )
        # Includes
        self.include_folder = cfg.include_folder
        self.include_file = cfg.include_file
        self.include_content = PatternGroup(
            globs=[],
            regex=cfg.include_content.regex,
            substrings=cfg.include_content.substrings
        )
        # Flags
        self._has_folder_inc = bool(
            self.include_folder.globs
            or self.include_folder.regex
            or self.include_folder.substrings
        )
        self._has_file_inc = bool(
            self.include_file.globs
            or self.include_file.regex
            or self.include_file.substrings
        )
        self._has_content_inc = bool(
            self.include_content.regex
            or self.include_content.substrings
        )

    def _match(self, name: str, group: PatternGroup) -> bool:
        # Glob
        for pat in group.globs:
            if fnmatch.fnmatch(name, pat):
                return True
        # Regex
        for pat in group.regex_patterns:
            if pat.search(name):
                return True
        # Substrings
        for sub in group.substrings:
            if sub in name:
                return True
        return False

    def is_excluded_dir(self, path: Path, relpath: str) -> bool:
        """
        True se algum segmento de relpath OU o próprio relpath casar com exclude_dirs.
        """
        if relpath:
            segments = relpath.split('/')
            for seg in segments:
                if self._match(seg, self.exclude_dirs):
                    return True
            # multi-segment match
            if self._match(relpath, self.exclude_dirs):
                return True
        return False

    def is_excluded_file(self, filename: str) -> bool:
        return self._match(filename, self.exclude_files)

    def matches_include_folder(self, rel_dir: str, parent_segments: List[str]) -> bool:
        """
        True se não há include_folder ativo OU
        algum segmento casar OU rel_dir casar como multi-segmento.
        """
        if not self._has_folder_inc:
            return True
        for seg in parent_segments:
            if self._match(seg, self.include_folder):
                return True
        if self._match(rel_dir, self.include_folder):
            return True
        return False

    def matches_include_file(self, filename: str) -> bool:
        if not self._has_file_inc:
            return True
        return self._match(filename, self.include_file)

    def matches_include_content(self, path: Path) -> bool:
        if not self._has_content_inc:
            return True
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return False
        for pat in self.include_content.regex_patterns:
            if pat.search(text):
                return True
        for sub in self.include_content.substrings:
            if sub in text:
                return True
        return False

    def should_include(self, path: Path, relpath: str) -> bool:
        # 1) Exclude dirs
        rel_dir = Path(relpath).parent.as_posix()
        if rel_dir == ".":
            rel_dir = ""
        if self.is_excluded_dir(path.parent, rel_dir):
            return False
        # 2) Exclude files
        if path.is_file() and self.is_excluded_file(path.name):
            return False
        # 3) Sem includes → inclui tudo não excluído
        if not (self._has_folder_inc or self._has_file_inc or self._has_content_inc):
            return True
        # 4) Include folder
        parent_segments = rel_dir.split('/') if rel_dir else []
        if not self.matches_include_folder(rel_dir, parent_segments):
            return False
        # 5) Include file
        if path.is_file() and not self.matches_include_file(path.name):
            return False
        # 6) Include content
        if path.is_file() and not self.matches_include_content(path):
            return False
        # 7) Passou em tudo
        return True