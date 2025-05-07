import re, fnmatch

def matches(path: str, pattern: str) -> bool:
    if pattern.startswith('re:'):
        return re.search(pattern[3:], path) is not None
    return fnmatch.fnmatchcase(path, pattern)