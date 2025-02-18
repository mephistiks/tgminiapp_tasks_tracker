import os
import argparse
from pathlib import Path

DEFAULT_BLACKLIST = {
    "substrings": [
        "bootstrap.min",
        "venv",
        ".vscode",
        "node_modules",
        ".svg",
        ".lock",
        '.gitignore',
        'git',
        'sqlite',
        'r.in',
        'r.txt',
        'dist',
        'concat.py',
        'pyc'
    ],  # Новый параметр для подстрок в путях
    "dirs": ["node_modules", "venv", "dist", "git"],  # Новый параметр для директорий
}


def is_blacklisted(file_path, blacklist):
    path = Path(file_path)
    path_str = str(path).lower()
    print(path_str)
    for s in blacklist["substrings"]:
        if s in str(file_path):
            return True

    return False


def process_directory(root_dir, output_file, blacklist):
    root_path = Path(root_dir).resolve()

    with open(output_file, "w", encoding="utf-8") as out_f:
        for root, dirs, files in os.walk(root_path):
            # Фильтрация директорий
            dirs[:] = [d for d in dirs if d not in blacklist["dirs"]]

            for file in sorted(files):
                full_path = Path(root) / file
                relative_path = full_path.relative_to(root_path)

                if not is_blacklisted(relative_path, blacklist):
                    try:
                        content = full_path.read_text(encoding="utf-8")

                        out_f.write(f">>> {relative_path}\n{content}")
                        if not content.endswith("\n"):
                            out_f.write("\n")
                        out_f.write(f"<<< {relative_path}|\n\n")
                    except UnicodeDecodeError:
                        print(f"Skipping binary file: {relative_path}")
                    except Exception as e:
                        print(f"Error {relative_path}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Combine files for LLM processing")
    parser.add_argument("root_dir", help="Root directory to process")
    parser.add_argument("output_file", help="Output file path")
    args = parser.parse_args()

    print(f"Processing: {args.root_dir}")
    process_directory(args.root_dir, args.output_file, DEFAULT_BLACKLIST)
    print(f"Done! Output: {args.output_file}")


if __name__ == "__main__":
    main()
