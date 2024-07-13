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
    function_start_regex = re.compile(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^;]*\)\s*(?:\{|$)')
    function_name_regex = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
    opening_brace_regex = re.compile(r'\{')

    modified_lines = []
    inside_function = False
    function_name = None
    brace_count = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        
        if not inside_function:
            # Skip preprocessor directives, struct/array initializations, and single-line statements
            if line.strip().startswith('#') or line.strip().endswith(';') or re.match(r'^\s*{', line):
                modified_lines.append(line)
                i += 1
                continue

            # Check if the line starts a function definition
            if function_start_regex.match(line):
                function_signature = line
                brace_count = line.count('{') - line.count('}')
                i += 1
                while i < len(lines) and brace_count == 0:
                    function_signature += lines[i]
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    i += 1
                
                if brace_count > 0:
                    # Extract function name from the signature
                    function_name_match = function_name_regex.search(function_signature)
                    if function_name_match:
                        function_name = function_name_match.group(1)
                        if function_name not in ["if", "while", "for", "switch", "else"]:
                            inside_function = True
                            modified_lines.append(function_signature)
                            modified_lines.append(f'    pr_info("{function_name} called\\n");\n')
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
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0:
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
