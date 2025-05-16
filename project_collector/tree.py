from pathlib import Path
from typing import Dict, Any, Set


def build_tree(root: Path, included_set: Set[Path]) -> Dict[str, Any]:
    """
    Constrói um dicionário aninhado representando a árvore de diretórios,
    marcando arquivos e pastas ignorados.

    Args:
        root: Path absoluto para o diretório raiz.
        included_set: conjunto de Paths relativos ao root dos arquivos incluídos.

    Retorna:
        Um dict onde chaves são nomes de arquivos/pastas (com sufixos)
        e valores são sub-dicts (para pastas) ou None (para arquivos).
    """
    def _build(current_dir: Path) -> Dict[str, Any]:
        tree: Dict[str, Any] = {}
        # Ordena por nome para saída consistente
        for item in sorted(current_dir.iterdir(), key=lambda p: p.name):
            rel = item.relative_to(root)
            if item.is_dir():
                # Verifica se algum arquivo incluído vive abaixo desta pasta
                has_child = False
                for inc in included_set:
                    child_path = root / inc
                    try:
                        child_path.relative_to(item)
                        has_child = True
                        break
                    except ValueError:
                        continue
                if not has_child:
                    # Nenhum filho incluído: marca como ignorado e não expande
                    tree[f"{item.name} (ignored)"] = {}
                else:
                    # Há filhos incluídos: expande recursivamente
                    tree[item.name] = _build(item)
            else:
                # Arquivo: destaca se incluído, senão ignora
                if rel in included_set:
                    tree[f">>> {item.name} <<<"] = None
                else:
                    tree[f"{item.name} (ignored)"] = None
        return tree

    return _build(root)


def print_tree(tree: Dict[str, Any], prefix: str = "") -> str:
    """
    Gera uma representação em texto ASCII da árvore construída.

    Args:
        tree: dict gerado por build_tree
        prefix: prefixo de indentação para chamadas recursivas

    Retorna:
        Uma string com linhas contendo ├── e └── para conexões.
    """
    result = ""
    items = list(tree.items())
    for idx, (name, subtree) in enumerate(items):
        connector = "├── " if idx < len(items) - 1 else "└── "
        result += prefix + connector + name + "\n"
        if subtree:
            extension = "│   " if idx < len(items) - 1 else "    "
            result += print_tree(subtree, prefix + extension)
    return result
