# Project: Automated Missing Translation Finder
# Author: Dino Paulo R. Gomez
# Date: March 16, 2023
# Version: 0.1

# [Imports]
# I/O
import os

# Memory Mapping
import mmap

# Time Library
import time

# XML Library
import xml.etree.ElementTree as ET

# Pretty Print
from pprint import pprint

# Date Time
from datetime import datetime

# [Constants]
CSV = "csv"

# [Variables]
# Base Addr
module_path = r""
# Resource Addr
resource_directories = {}
# Resource Addr Pattern
resource_path = r""
# Resources XML List
module_files_path_list = []

# Sanitized Word Lists
word_list = []
# Matched Strings List
match_list = []
# XML Key-Value List
xml_generated_list = []

# [Util Functions]

# Clean CSV Input Data
def sanitize(input):
    return input.replace('"', "").strip()


# UNUSED needs rewrite
def get_file_paths_dir(dir_oath):
    files = os.listdir(dir_oath)
    for file in files:
        path = dir_oath + "\\" + file
        if os.path.isdir(path) == False:
            module_files_path_list.append(path)


# handle_csv()-args[csv: String]
# parses through the csv file for each search 
# string# uses the sanitize() func to remove 
# unwanted charachters
def handle_csv(csv):
    with open(CSV + "\\" + csv) as csv_file:
        for line in csv_file:
            if line != "N/A":
                word_list.append(sanitize(line))


# build_file_tree()-args[Module Path: String]
# traverses through the given [Module Path] and gets
# all the directories and its subdirectories to build
# the file tree.
# populates [resource_directories] and [module_files_path_list] 
def build_file_tree():

    # Get Resource/Resources Directory from UIPatterns
    for (dirpath, dirnames, filenames) in os.walk(module_path):
        for dir in dirnames:
            # Case Check due to folders being inconsistent
            if dir.endswith("resource") or dir.endswith("resources"):
                resource_directories[dirpath] = os.sep.join([dirpath, dir])
    # Filter Directories to store only v11.1.0 resources
    for key, value in list(resource_directories.items()):
        if "11.1.0" not in key:
            del resource_directories[key]
    # Iterate through Resources List
    for key, path in list(resource_directories.items()):
        for dirpath, dirs, files in os.walk(path):
            for filename in files:
                file = os.path.join(dirpath, filename)
                module_files_path_list.append(file)


# find_keyword_in_tree()-args[input: String]
# searches the file tree for the given string
# uses memory map to find the byte subsequence
# transfers the file to the handle_xml() for parsing
def find_keyword_in_tree(input):
    print('\nSearching [ "' + input + '" ] in File Tree\n')
    for file_path in module_files_path_list:
        # Iterate through Files in Tree
        # memory mapping since the directory tree is 4-5 levels deep [UIPatterns\Module\11.1.0\resource\SubModule\Resource.XML]
        # this will increase the search efficiency since we are finding via byte subsequence
        with open(file_path, "rb", 0) as file, mmap.mmap(
            file.fileno(), 0, access=mmap.ACCESS_READ
        ) as s:
            # Find returns the index of the first occurence
            # Returns -1 if not found
            if s.find(bytes(input, encoding="utf8")) != -1:
                # print("Found in [ "+file_path+" ]")
                # If matched with Search input then store in Match_list
                match_list.append(file_path)
                # Passed to handle XML for parsing the matched XML
                handle_xml(file_path, input)



def print_json_locale():
    start_time = time.time()
    day = datetime.now().day
    month = datetime.now().month
    year = datetime.now().year
    file_name = f"gen\en-US-{month}-{day}-{year}.json"
    with open(file_name, "a") as local_file:
        local_file.write("{\n")
        for count, item in enumerate(set(xml_generated_list)):
            if count != len(set(xml_generated_list)) - 1:
                local_file.write(f"{item},\n")
            else:
                local_file.write(f"{item}\n")
        local_file.write("}")
    end_time = round(time.time() - start_time, 2)
    print(f"\nGenerated  {file_name} in {end_time}s / {round(end_time/60,2)}mins.")


def handle_xml(file, find_str):
    # Parse XML passed by keyword search func
    tree = ET.parse(file)
    # Get Root
    root = tree.getroot()
    # Get Root-attr Key Value
    root_code = str(root.attrib["code"])
    # loop through the <mapping> tags
    for map_tag in root.iter("mapping"):
        # down 1 level towards the <map> tag
        for map_item in map_tag:
            # get tag
            root_tag = str(map_tag.attrib["name"])
            # get tag-value
            root_item = str(map_item.text)
            # Search Condition
            if find_str == root_item:
                # print(f"\"{root_code}.{root_tag}\" : \"{root_item}\"")
                xml_generated_list.append(f'"{root_code}.{root_tag}" : "{root_item}"')



def generate():
    start_time = time.time()
    word_set = set(word_list)
    for word in word_set:
        find_keyword_in_tree(word)
    end_time = round(time.time() - start_time, 2)
    print(
        f"\nFound {len(match_list)} matches and generated key-value pairs in {end_time}s / {round(end_time/60,2)}mins."
    )


def main():

    handle_csv("CMMain.csv")
    build_file_tree()
    generate()
    print_json_locale()


if __name__ == "__main__":
    main()
