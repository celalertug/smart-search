import os
import argparse
import fnmatch
from collections import defaultdict
import pyperclip

# ANSI color codes
BLUE = '\033[94m'
RESET = '\033[0m'

def search_files(directory, search_words, include_pattern=None, exclude_pattern=None, ignore_case=False):
    matching_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if include_pattern and not fnmatch.fnmatch(file, include_pattern):
                continue
            if exclude_pattern and fnmatch.fnmatch(file, exclude_pattern):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if ignore_case:
                        content = content.lower()
                        words = [word.lower() for word in search_words]
                    else:
                        words = search_words
                    if all(word in content for word in words):
                        matching_files.append((file_path, content))
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

    return matching_files

def group_files_by_extension(files):
    grouped_files = defaultdict(list)
    for file, content in files:
        _, extension = os.path.splitext(file)
        extension = extension.lower()
        grouped_files[extension].append((file, content))
    return grouped_files

def main():
    parser = argparse.ArgumentParser(description="Search for words in files recursively.")
    parser.add_argument("directory", help="Directory to search in")
    parser.add_argument("words", nargs='+', help="Words to search for")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Ignore case when searching")
    parser.add_argument("--include", help="File pattern to include (e.g., '*.txt')")
    parser.add_argument("--exclude", help="File pattern to exclude (e.g., '*.log')")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy matching file contents to clipboard")
    args = parser.parse_args()

    directory = args.directory
    search_words = args.words
    ignore_case = args.ignore_case
    include_pattern = args.include
    exclude_pattern = args.exclude
    copy_to_clipboard = args.copy

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        return

    matching_files = search_files(directory, search_words, include_pattern, exclude_pattern, ignore_case)

    if matching_files:
        print(f"Files containing the word(s) {', '.join(search_words)}:")
        grouped_files = group_files_by_extension(matching_files)
        all_content = []
        for extension, files in sorted(grouped_files.items()):
            print(f"\n{BLUE}{extension} files:{RESET}")
            for file, content in sorted(files):
                print(f"  {file}")
                all_content.append(f"--- {file} ---\n``` \n {content}\n``` \n")

        if copy_to_clipboard:
            clipboard_content = "\n".join(all_content)
            pyperclip.copy(clipboard_content)
            print("\nContent of matching files has been copied to clipboard.")
    else:
        print(f"No files found containing the word(s) {', '.join(search_words)}.")

if __name__ == '__main__':
    main()
