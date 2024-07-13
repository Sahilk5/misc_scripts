#!/usr/bin/env python3

import os
import re
import sys

def find_c_files(directory):
    c_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.c'):
                c_files.append(os.path.join(root, file))
    return c_files

def add_pr_info_to_functions(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Regular expression to match the beginning of a function definition
    function_regex = re.compile(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*{')
    modified_lines = []
    inside_function = False
    function_name = None

    for line in lines:
        if not inside_function:
            # Check if the line starts a function definition
            match = function_regex.match(line)
            if match:
                inside_function = True
                # Extract function name
                function_signature = match.group(0)
                function_name = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\(', function_signature)[-1][:-1].strip()
                modified_lines.append(line)
                modified_lines.append(f'    pr_info("{function_name} called\\n");\n')
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)
            if '}' in line:
                inside_function = False

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

def process_directory(directory):
    c_files = find_c_files(directory)
    for c_file in c_files:
        add_pr_info_to_functions(c_file)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python add_pr_info.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"{directory} is not a valid directory")
        sys.exit(1)

    process_directory(directory)
