from argparse import ArgumentParser, Namespace
from pathlib import Path
import errno
import magic
import re

class PySubOpts(Namespace):
    old: str
    new: str
    count: int
    line: bool
    regex: bool
    ignorecase: bool
    multiline: bool
    dotall: bool
    whitelist: list[str]
    blacklist: list[str]
    path: Path
    
def get_regex_flags(opts: PySubOpts) -> int:
    flags = 0
    if opts.ignorecase:
        flags |= re.IGNORECASE
    if opts.multiline:
        flags |= re.MULTILINE
    if opts.dotall:
        flags |= re.DOTALL
    return flags

def sub_text(opts: PySubOpts, text: str) -> str:
    if opts.regex:
        return re.sub(opts.old, opts.new, text, 0 if opts.count == -1 else opts.count, get_regex_flags(opts))
    else:
        return text.replace(opts.old, opts.new, opts.count)

def sub_file(opts: PySubOpts, path: Path, encoding: str):
    print(f"substituting text file - {path}")
    try:
        with path.open("r+", encoding=encoding) as file:
            if opts.line:
                lines = file.readlines()
                new_lines = [sub_text(opts, line) for line in lines]
                file.seek(0)
                file.writelines(new_lines)
                file.truncate()
            else:
                text = file.read()
                new_text = sub_text(opts, text)
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

def sub_rec(opts: PySubOpts, path: Path):
    if path.is_dir():
        for subpath in path.iterdir():
            sub_rec(opts, subpath)
    elif path.is_file():
        matched = False
        if opts.whitelist is not None:
            for ext in opts.whitelist:
                if path.suffix == f".{ext}":
                    matched = True
                    break
        else:
            matched = True
        if opts.blacklist is not None:
            for ext in opts.blacklist:
                if path.suffix == f".{ext}":
                    matched = False
                    break
        if matched:
            magic_text = magic.from_file(str(path.resolve()))
            if magic_text.startswith("ASCII"):
                sub_file(opts, path, "ASCII")
            elif magic_text.startswith("UTF-8"):
                sub_file(opts, path, "UTF-8")

def parse_extension_list(x: str) -> list[str]:
    return x.replace(".", "").split(",")

def main():
    parser = ArgumentParser(description="Substitute text within files")
    parser.add_argument("-o", "--old", required=True, help="old text to be substituted")
    parser.add_argument("-n", "--new", required=True, help="new text to use in substitution")
    parser.add_argument("-c", "--count", default=-1, type=int, help="number of substitutions to make")
    parser.add_argument("-l", "--line", action="store_true", help="switch to line by line substitutions")
    parser.add_argument("-r", "--regex", action="store_true", help="use regex substitutions")
    parser.add_argument("-i", "--ignorecase", action="store_true", help="use regex case insensitive flag")
    parser.add_argument("-m", "--multiline", action="store_true", help="use regex multi line flag")
    parser.add_argument("-d", "--dotall", action="store_true", help="use regex dot all flag")
    parser.add_argument("-w", "--whitelist", type=parse_extension_list, help="file extensions to whitelist")
    parser.add_argument("-b", "--blacklist", type=parse_extension_list, help="file extensions to blacklist")
    parser.add_argument("-p", "--path", default=Path("."), type=Path, help="input path to search for files")

    opts: PySubOpts = parser.parse_args()
    
    if opts.path.exists():
        sub_rec(opts, opts.path)
    else:
        parser.error("input path does not exist")

if __name__ == "__main__":
    main()
