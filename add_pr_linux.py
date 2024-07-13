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

    # Regex patterns to identify function definitions
    function_start_regex = re.compile(r'^\s*[\w\s\*\(\)]+\s+\w+\s*\([^;]*$')
    opening_brace_regex = re.compile(r'^\s*\{')
    array_or_struct_regex = re.compile(r'^\s*(static\s+)?(const\s+)?(struct\s+\w+\s*|[\w\*\s]+\[\s*\]|\w+\s*\[\s*\])\s*=\s*\{')

    modified_lines = []
    inside_function = False
    inside_define = False
    inside_struct = False
    inside_array_or_struct = False

    i = 0
    while i < len(lines):
        line = lines[i]
        if not inside_function:
            # Check if inside a multi-line #define or struct
            if inside_define:
                modified_lines.append(line)
                if not line.strip().endswith('\\'):
                    inside_define = False
                i += 1
                continue

            if inside_struct:
                modified_lines.append(line)
                if line.strip().endswith('};'):
                    inside_struct = False
                i += 1
                continue

            if inside_array_or_struct:
                modified_lines.append(line)
                if line.strip().endswith('};'):
                    inside_array_or_struct = False
                i += 1
                continue

            # Check if the line starts a #define statement
            if line.strip().startswith('#define') and line.strip().endswith
