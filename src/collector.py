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
        # 1) Filtra subpastas para não descer nas ignoradas
        kept_dirs = []
        for d in dirnames:
            p = current / d
            if flt.include_path(p, check_content=False):
                kept_dirs.append(d)
            elif verbose:
                print(f"Ignoring directory: {p}")
        dirnames[:] = kept_dirs

        # 2) Processa arquivos
        for fname in filenames:
            p = current / fname
            if flt.include_path(p, check_content=only_tree):
                rel = p.relative_to(root)
                included.append(rel)
                if not only_tree:
                    try:
                        if verbose:
                            print(f"Reading file: {p}")
                        text = p.read_text(encoding='utf-8', errors='ignore')
                        block = (
                            f"\n--- {rel}:START ---\n"
                            + text
                            + f"\n--- {rel}:END ---\n"
                        )
                        content_blocks.append(block)
                    except Exception as e:
                        if verbose:
                            print(f"Error reading file {p}: {e}")
            elif verbose:
                print(f"Ignoring file: {p}")

    full_content = "".join(content_blocks)
    return full_content, included
