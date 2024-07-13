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

def is_macro(line):
    return line.strip().startswith('#define') and line.strip().endswith('\\')

def is_struct(line):
    return 'struct' in line and line.strip().endswith('{')

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
            # Check if inside a multi-line #define
            if inside_define:
                modified_lines.append(line)
                if not line.strip().endswith('\\'):
                    inside_define = False
                i += 1
                continue

            # Check if inside a struct definition
            if inside_struct:
                modified_lines.append(line)
                if line.strip().endswith('};'):
                    inside_struct = False
                i += 1
                continue

            # Check if inside an array or struct initializer
            if inside_array_or_struct:
                modified_lines.append(line)
                if line.strip().endswith('};'):
                    inside_array_or_struct = False
                i += 1
                continue

            # Check if the line starts a #define statement
            if is_macro(line):
                inside_define = True
                modified_lines.append(line)
                i += 1
                continue

            # Check if the line starts a struct definition
            if is_struct(line):
                inside_struct = True
                modified_lines.append(line)
                i += 1
                continue

            # Check if the line starts an array or struct initializer
            if array_or_struct_regex.match(line):
                inside_array_or_struct = True
                modified_lines.append(line)
                i += 1
                continue

            # Check if the line starts a function definition
            if function_start_regex.match(line) and not re.match(r'^\s*#', line):
                function_signature = line
                i += 1
                while i < len(lines) and not opening_brace_regex.match(lines[i]):
                    function_signature += lines[i]
                    i += 1
                if i < len(lines) and opening_brace_regex.match(lines[i]):
                    function_signature += lines[i]
                    # Extract function name from the signature
                    function_name_match = re.search(r'\b(\w+)\s*\(', function_signature)
                    if function_name_match:
                        function_name = function_name_match.group(1)
                        if function_name not in ["if", "while", "for", "switch", "else"]:
                            inside_function = True
                            modified_lines.append(function_signature)
                            modified_lines.append('    pr_info("%s called\\n", __func__);\n')
                        else:
                            modified_lines.append(function_signature)
                    else:
                        modified_lines.append(function_signature)
                else:
                    modified_lines.append(function_signature)
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)
            if '}' in line:
                inside_function = False
        i += 1

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
