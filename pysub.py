from argparse import ArgumentParser
from pathlib import Path
import magic
import errno

def sub(path: Path, old: str, new: str, encoding: str):
    print(f"substituting text file - {path}")
    try:
        with path.open("r+", encoding=encoding) as file:
            text = file.read()
            new_text = text.replace(old, new)
            file.seek(0)
            file.write(new_text)
            file.truncate()
    except IOError as e:
        if e.errno == errno.ENOENT:
            print(f"File does not exist - {path}")
        elif e.errno == errno.EACCES:
            print(f"Do not have permission to read/write file - {path}")
        else:
            print(f"Failed to read file (error: {e}) - {path}")

def sub_rec(path: Path, old: str, new: str):
    if path.is_dir():
        for subpath in path.iterdir():
            sub_rec(subpath, old, new)
    elif path.is_file():
        magic_text = magic.from_file(str(path.resolve()))
        if magic_text.startswith("ASCII"):
            sub(path, old, new, "ASCII")
        elif magic_text.startswith("UTF-8"):
            sub(path, old, new, "UTF-8")

def main():
    parser = ArgumentParser(description="Substitute text within files")
    parser.add_argument("-o", "--old", required=True, help="old text to be replaced")
    parser.add_argument("-n", "--new", required=True, help="new text to use in replacement")
    parser.add_argument("-i", "--input", default=".", help="input path to search for files")

    args = parser.parse_args()
    
    input_path = Path(args.input)
    if input_path.exists():
        sub_rec(input_path, args.old, args.new)
    else:
        parser.error("input path does not exist")

if __name__ == "__main__":
    main()
