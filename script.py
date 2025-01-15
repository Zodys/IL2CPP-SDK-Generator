import os
import re
import time
import shutil
from collections import defaultdict
from colorama import *

init(autoreset=True)

def print_header(title):
    print(Fore.CYAN + '=' * 50)
    print(Fore.CYAN + title.center(50))
    print(Fore.CYAN + '=' * 50)

def print_info(message):
    print(Fore.GREEN + message)

def print_warning(message):
    print(Fore.YELLOW + message)

def print_error(message):
    print(Fore.RED + message)

def create_include_h(directory, output_file='includes.h'):
    output_file = os.path.join(output_directory, f"{output_file}")
    with open(output_file, 'w', encoding="utf-8") as f:
        for filename in os.listdir(directory):
            if filename not in output_file and filename.endswith('.h'):
                f.write(f'#include "{filename}"\n')


def find_cs_files(directory):
    cs_files = {}
    
    print_header(f"Indexing assembly classes {os.path.basename(directory)}")
    for root, _, files in os.walk(directory):
        root_name = os.path.basename(root)
        for file in files:
            if "AssemblyInfo" not in file and file.endswith('.cs'):
                file_name = os.path.join(root, file)
                file_name = os.path.relpath(file_name, directory) 
                file_name = os.path.splitext(file_name)[0].replace('\\','_').replace('.','_')

                cs_files[file_name] = os.path.join(root, file) 
                print_info(f"CSharp file indexed: {os.path.relpath(cs_files[file_name], directory)}")
    print_warning(f"Successfully indexed assembly classes. Class count: {len(cs_files)}")
    
    return cs_files

def distribute_structures(structs_file, category_files, output_directory):
    print_header("Searching for matching structs in il2cpp header")
    try:
        with open(structs_file, 'r') as file:
            content = file.read()
    except Exception as e:
        print_error(f"Error reading file {structs_file}: {e}")
        return

    pattern = re.compile(
        r'struct\s+(\w+)\s*(?::\s*\w+\s*)?\{(?:[^{}]|\{[^{}]*\})*\};',
        re.DOTALL
    )

    structures_dict = defaultdict(list)
    matches = list(pattern.finditer(content))
    total_structs = len(matches)
    extracted_structs = 0

    valid_suffixes = {"_o", "_c", "_Fields", "_VTable"}

    cs_file_suffix_map = defaultdict(set)
    for category, cs_files in category_files.items():
        for cs_name in cs_files:
            for suffix in valid_suffixes:
                cs_file_suffix_map[f"{cs_name}{suffix}"].add(category)

    for match in matches:
        struct_name = match.group(1)
        struct_body = match.group(0)

        if "___c__DisplayClass" in struct_name or "_d__" in struct_name:
            continue

        if struct_name in cs_file_suffix_map:
            for category in cs_file_suffix_map[struct_name]:
                structures_dict[category].append(struct_body)
                extracted_structs += 1

    for category, structures in structures_dict.items():
        output_file = os.path.join(output_directory, f"{category}.h")
        try:
            with open(output_file, 'w', encoding="utf-8") as file:
                file.write(f"// Structures for category: {category}\n")
                file.write('\n'.join(structures))
                file.write('\n\n')
            print_info(f'Output file: "{output_file}"')
        except Exception as e:
            print_error(f"Error writing to file {output_file}: {e}")

    create_include_h(output_directory)
    
    struct_percentage = (extracted_structs / total_structs * 100) if total_structs > 0 else 0
    print_warning(f"Total struct count: {total_structs} (Extracted: {extracted_structs}) [{struct_percentage:.6f}%]")

    total_class_count = sum(len(v) for v in category_files.values())
    
    extracted_class_count = sum(
        1 for structures in structures_dict.values() for struct in structures if struct.split()[1].endswith('_o')
    )
    
    class_percentage = (extracted_class_count / total_class_count * 100) if total_class_count > 0 else 0
    print_warning(f"Total class count: {total_class_count} (Extracted: {extracted_class_count}) [{class_percentage:.6f}%]")


def get_input(prompt):
    return input(prompt).strip()

if __name__ == "__main__":
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        structs_file = get_input("Enter the name of the structs file (il2cpp.h): ")
        root_directory = get_input("Enter the name of the directory containing the .cs files (e.g, dump): ")
        output_directory = "SDK"

        if not os.path.exists(root_directory):
            raise FileNotFoundError(f"The directory '{root_directory}' does not exist.")


        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)

        os.makedirs(output_directory)

        start_time = time.time()

        category_files = {}
        for folder in os.listdir(root_directory):
            folder_path = os.path.join(root_directory, folder)
            if os.path.isdir(folder_path):
                cs_files = find_cs_files(folder_path)
                if cs_files:
                    category_files[folder] = cs_files.keys()
        
        distribute_structures(structs_file, category_files, output_directory)

        end_time = time.time()
        execution_time = end_time - start_time

        print_warning(f"Program execution time: {execution_time:.2f} seconds")
        print_info("Structures successfully written to files.")

    except Exception as e:
        print_error(f"An error occurred: {e}")

input("Press Enter to exit...")
