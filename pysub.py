from pathlib import Path
import magic
import errno

def sub(path: Path, encoding):
    print(f"substituting text file - {path}")
    try:
        with path.open("r+", encoding=encoding) as file:
            text = file.read()
            new_text = text.replace("old", "new")
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

def sub_rec(path: Path):
    if path.is_dir():
        for subpath in path.iterdir():
            sub_rec(subpath)
    elif path.is_file():
        magic_text = magic.from_file(str(path.resolve()))
        if magic_text.startswith("ASCII"):
            sub(path, "ASCII")
        elif magic_text.startswith("UTF-8"):
            sub(path, "UTF-8")

def main():
    path = Path("test")
    if path.exists():
        sub_rec(path)

if __name__ == "__main__":
    main()
