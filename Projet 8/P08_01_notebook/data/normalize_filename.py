import os

from numpy import full

def process_directory(root):
    print(">", root)
    for item in os.listdir(root):
        full_path = os.path.join(root, item)
        if os.path.isdir(full_path):
            print("d", full_path)
            new_full_path = os.path.join(root, item.replace(" ", "_").lower())
            if new_full_path != full_path:
                os.renames(full_path, new_full_path)
                process_directory(new_full_path)
            else:
                process_directory(full_path)
        else:
            print("f", full_path)
            new_full_path = os.path.join(root, item.replace(" ", "_").lower())
            if new_full_path != full_path:
                os.renames(full_path, new_full_path)

process_directory(os.getcwd())