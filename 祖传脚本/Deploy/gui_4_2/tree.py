import os

def generate_tree(path, level=0, max_depth=None, is_last=False, prefix=""):
    if max_depth is not None and level >= max_depth:
        return
    items = os.listdir(path)
    for i, item in enumerate(items):
        full_path = os.path.join(path, item)
        is_item_last = (i == len(items) - 1)
        marker = "└── " if is_item_last else "├── "
        print(prefix + marker + item)
        if os.path.isdir(full_path):
            new_prefix = prefix + ("    " if is_item_last else "│   ")
            generate_tree(full_path, level+1, max_depth, is_item_last, new_prefix)

generate_tree(".", max_depth=2)