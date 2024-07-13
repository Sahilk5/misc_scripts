#!/usr/bin/env python3

import os
import re
import argparse

def add_pr_info_statement(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    function_regex = re.compile(r'\b(?:static|extern)?\s*[\w\s*]+\s+(\w+)\s*\([^)]*\)\s*{')

    call_chain_declared = False
    inside_function = False

    for line in lines:
        if not inside_function:
            match = function_regex.search(line)
            if match:
                function_name = match.group(1)
                indent = re.match(r'\s*', line).group()

                if not call_chain_declared:
                    new_lines.append('#include <linux/kernel.h>\n#include <linux/string.h>\n\n')
                    new_lines.append('char call_chain[1024] = "";\n\n')
                    call_chain_declared = True

                new_lines.append(f'{line.rstrip()}\n')
                new_lines.append(f'{indent}strcat(call_chain, "{function_name} -> ");\n')
                new_lines.append(f'{indent}pr_info("Call chain: %s\\n", call_chain);\n')
                inside_function = True
                continue

        if inside_function:
            new_lines.append(line)
            if line.strip() == '{':
                inside_function = False

    with open(file_path, 'w') as file:
        file.writelines(new_lines)

def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.c') or file.endswith('.h'):
                file_path = os.path.join(root, file)
                add_pr_info_statement(file_path)

def main():
    parser = argparse.ArgumentParser(description="Add pr_info call chain logging to C files in a folder.")
    parser.add_argument("folder_path", help="Path to the folder containing C files.")
    args = parser.parse_args()
    
    process_folder(args.folder_path)

if __name__ == "__main__":
    main()
