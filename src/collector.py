import os
from pathlib import Path
from typing import List, Tuple
from .filter import Filter
from .config import FilterConfig


def collect_file_content(
    directory: str,
    cfg: FilterConfig,
    only_tree: bool = False,
    verbose: bool = False
) -> Tuple[str, List[Path]]:
    """
    Percorre recursivamente `directory`, aplica filtros e:
      - Se only_tree=True: apenas determina quais arquivos ficam na árvore, sem coletar conteúdo.
      - Se only_tree=False: lê e concatena conteúdo dos arquivos incluídos.

    Args:
        directory: caminho da raiz a processar.
        cfg: FilterConfig já populado.
        only_tree: se True, ativa checagem de conteúdo para incluir na árvore.
        verbose: se True, imprime logs de inclusão/ignoração.

    Returns:
        content: string com blocos "--- path:START ---...---:END ---" para cada arquivo (vazio se only_tree=True).
        included: lista de Paths relativos (Path objects) dos arquivos incluídos.
    """
    root = Path(directory)
    flt = Filter(cfg)
    included: List[Path] = []
    content_blocks: List[str] = []

    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        # caminho relativo da pasta atual (string sem ".")
        rel = current.relative_to(root)
        rel_dir = rel.as_posix() if str(rel) != "." else ""

        # 1) Poda de subpastas
        pruned = []
        for d in dirnames:
            sub_rel = f"{rel_dir}/{d}" if rel_dir else d
            if not flt.is_excluded_dir(current / d, sub_rel):
                pruned.append(d)
        dirnames[:] = pruned

        # 2) Processa arquivos
        for fname in filenames:
            sub_rel = f"{rel_dir}/{fname}" if rel_dir else fname
            full_path = current / fname
            if flt.should_include(full_path, sub_rel, check_content=only_tree):
                rel_path = Path(sub_rel)
                included.append(rel_path)
                if not only_tree:
                    if verbose:
                        print(f"Reading file: {full_path}")
                    try:
                        text = full_path.read_text(encoding='utf-8', errors='ignore')
                        block = (
                            f"\n--- {rel_path}:START ---\n"
                            + text
                            + f"\n--- {rel_path}:END ---\n"
                        )
                        content_blocks.append(block)
                    except Exception as e:
                        if verbose:
                            print(f"Error reading file {full_path}: {e}")
            elif verbose:
                print(f"Ignoring file: {full_path}")

    full_content = "".join(content_blocks)
    return full_content, included
