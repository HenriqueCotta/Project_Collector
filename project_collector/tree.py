import fnmatch
import os

def build_tree(root, included, ignored_dirs, ignored_files):
    def helper(dir_path):
        items = []
        for name in sorted(os.listdir(dir_path)):
            full = os.path.join(dir_path, name)
            if os.path.isdir(full):
                if name in ignored_dirs: continue
                subtree = helper(full)
                if subtree:
                    items.append((name, subtree))
            else:
                if any(fnmatch.fnmatch(name, pat) for pat in ignored_files): continue
                rel = os.path.relpath(full, root)
                items.append(('>>> ' + name + ' <<<' if rel in included else name, None))
        return items
    return helper(root)