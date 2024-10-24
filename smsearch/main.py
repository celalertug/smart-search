import os
import argparse
import fnmatch
from collections import defaultdict
import pyperclip
from pyparsing import Word, alphanums, infixNotation, opAssoc, ParseResults
from colorama import init, Fore, Style

# ANSI color codes
BLUE = '\033[94m'
RESET = '\033[0m'


class BooleanExpression:
    def __init__(self):
        word = Word(alphanums + '_')
        expr = infixNotation(word,
                             [
                                 ('&', 2, opAssoc.LEFT),
                                 ('|', 2, opAssoc.LEFT),
                             ])
        self.expr = expr

    def evaluate(self, parse_result, content):
        if isinstance(parse_result, str):
            return parse_result.lower() in content.lower()
        elif isinstance(parse_result, ParseResults):
            if len(parse_result) == 1:
                return self.evaluate(parse_result[0], content)
            elif len(parse_result) == 3:
                left = self.evaluate(parse_result[0], content)
                op = parse_result[1]
                right = self.evaluate(parse_result[2], content)
                if op == '&':
                    return left and right
                elif op == '|':
                    return left or right
            else:  # Handle multiple AND operations
                result = True
                for i in range(0, len(parse_result), 2):
                    result = result and self.evaluate(parse_result[i], content)
                return result
        return False

    def parse_and_evaluate(self, expression, content):
        parsed = self.expr.parseString(expression, parseAll=True)
        return self.evaluate(parsed[0], content)


def search_files(directory, expression, include_pattern=None, exclude_pattern=None):
    matching_files = []
    boolean_expr = BooleanExpression()

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
                    if boolean_expr.parse_and_evaluate(expression, content):
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
    colored_examples = f"""
    {Fore.GREEN}Examples:{Style.RESET_ALL}
      {Fore.YELLOW}python main.py /path/to/search "word1 & word2"{Style.RESET_ALL}
        Search for files containing both word1 and word2.

      {Fore.YELLOW}python main.py /path/to/search "(python | java) & code"{Style.RESET_ALL}
        Search for files containing either "python" or "java", and also containing "code".

      {Fore.YELLOW}python main.py /path/to/search "important & (urgent | critical)"{Style.RESET_ALL}
        Search for files containing "important" and either "urgent" or "critical".

      {Fore.YELLOW}python main.py /path/to/search "error | exception" --include "*.log" --exclude "*.gz"{Style.RESET_ALL}
        Search for files containing either "error" or "exception" in .log files, excluding .gz files.

      {Fore.YELLOW}python main.py /path/to/search "confidential & (password | secret)" -c{Style.RESET_ALL}
        Search for files containing "confidential" and either "password" or "secret", 
        and copy the content of matching files to clipboard.
    """

    parser = argparse.ArgumentParser(
        description="Search for words in files recursively with boolean expressions.",
        epilog=colored_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("directory", help="Directory to search in")
    parser.add_argument("expression",
                        help="Boolean expression to search for (use & for AND, | for OR, and parentheses for grouping)")
    parser.add_argument("--include", help="File pattern to include (e.g., '*.txt')")
    parser.add_argument("--exclude", help="File pattern to exclude (e.g., '*.log')")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy matching file contents to clipboard")

    args = parser.parse_args()

    directory = args.directory
    expression = args.expression
    include_pattern = args.include
    exclude_pattern = args.exclude
    copy_to_clipboard = args.copy

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        return

    matching_files = search_files(directory, expression, include_pattern, exclude_pattern)

    if matching_files:
        print(f"Files matching the expression '{expression}':")
        grouped_files = group_files_by_extension(matching_files)
        all_content = []
        for extension, files in sorted(grouped_files.items()):
            print(f"\n{BLUE}{extension} files:{RESET}")
            for file, content in sorted(files):
                print(f"  {file}")
                all_content.append(f"--- {file} ---\n{content}\n")

        if copy_to_clipboard:
            clipboard_content = "\n".join(all_content)
            pyperclip.copy(clipboard_content)
            print("\nContent of matching files has been copied to clipboard.")
    else:
        print(f"No files found matching the expression '{expression}'.")


if __name__ == '__main__':
    main()
