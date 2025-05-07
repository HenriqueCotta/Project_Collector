import argparse, os
from .config import load_config
from .collector import should_include
from .tree import build_tree

def main():
    p = argparse.ArgumentParser()
    p.add_argument('directory')
    p.add_argument('--no-defaults', action='store_true')
    p.add_argument('--only-tree', action='store_true')
    args = p.parse_args()
    cfg = load_config(args.directory, args.no_defaults)

    included = []
    for root, dirs, files in os.walk(args.directory):
        dirs[:] = [d for d in dirs if d not in cfg['DEFAULT_IGNORED_DIRS']]
        for f in files:
            if f in cfg['DEFAULT_IGNORED_FILES']: continue
            full = os.path.join(root, f)
            if should_include(full, cfg):
                included.append(os.path.relpath(full, args.directory))
    tree = build_tree(args.directory, set(included), cfg['DEFAULT_IGNORED_DIRS'], cfg['DEFAULT_IGNORED_FILES'])
    if args.only_tree:
        print_tree(tree)
    else:
        # collect content omitted
        print_tree(tree)