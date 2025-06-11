import os

folder_paths = ['source', 'example']  
output_file = 'all_code.txt'
comment_prefixes = ('#', '//', '/*', '*', '--')

with open(output_file, 'w', encoding='utf-8') as out:
    for folder_path in folder_paths:
        for root, dirs, files in os.walk(folder_path):
            # Исключаем ненужные папки
            dirs[:] = [d for d in dirs if d not in ('pybind11', 'build')]

            for filename in sorted(files):
                if filename.endswith(('.py', '.cpp', '.h', '.c', '.java', '.js')):
                    filepath = os.path.join(root, filename)
                    relative_path = os.path.relpath(filepath, start=folder_path)
                    out.write(f"# ==== {os.path.join(folder_path, relative_path)} ====\n")
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            stripped = line.strip()
                            if stripped and not any(stripped.startswith(prefix) for prefix in comment_prefixes):
                                out.write(line)
