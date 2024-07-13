import os
import re

def add_pr_info_statement(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    function_regex = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*\s+)+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{')
    call_chain_variable_declared = False

    for line in lines:
        new_lines.append(line)
        match = function_regex.match(line)
        if match:
            function_name = match.groups()[-1]
            indent = re.match(r'\s*', line).group()

            # Declare call chain variable at the beginning of the first function
            if not call_chain_variable_declared:
                new_lines.insert(0, f'{indent}char call_chain[1024] = "";\n')
                call_chain_variable_declared = True

            # Update call chain and print statement
            new_lines.append(f'{indent}strcat(call_chain, "{function_name} -> ");\n')
            new_lines.append(f'{indent}pr_info("Call chain: %s\\n", call_chain);\n')

    with open(file_path, 'w') as file:
        file.writelines(new_lines)

def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.c'):
                file_path = os.path.join(root, file)
                add_pr_info_statement(file_path)

folder_path = '/path/to/your/folder'  # Replace with the path to your folder
process_folder(folder_path)
