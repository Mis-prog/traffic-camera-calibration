import os

folder_path = 'source'
output_file = 'all_code.txt'

with open(output_file, 'w', encoding='utf-8') as out:
    for root, _, files in os.walk(folder_path):
        for filename in sorted(files):
            if filename.endswith(('.py', '.cpp', '.h', '.c', '.java', '.js')):  # нужные расширения
                filepath = os.path.join(root, filename)
                out.write(f"# ==== {filename} ====\n")
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():  # удаляет пустые строки
                            out.write(line)
