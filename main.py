from abc import ABC, abstractmethod
from typing import List
import os
from pathlib import Path
import re
import shutil
from zipfile import ZipFile
CATEGORIES = {
    "audio": [".mp3", ".wav", ".flac", ".wma"],
    "video": [".mkv", ".avi", ".mov", ".mp4"],
    "images": [".jpeg", ".png", ".jpg", ".svg"],
    "archives": [".zip", ".gz", ".tar"],
    "docs": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx"],
}
file_list = {
    "audio": [],
    "video": [],
    "images": [],
    "archives": [],
    "docs": [],
    "other": [],
}
ext_list = {
    "audio": [],
    "video": [],
    "images": [],
    "archives": [],
    "docs": [],
    "other": [],
}
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = (
    "a",
    "b",
    "v",
    "g",
    "d",
    "e",
    "e",
    "j",
    "z",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "r",
    "s",
    "t",
    "u",
    "f",
    "h",
    "ts",
    "ch",
    "sh",
    "sch",
    "",
    "y",
    "",
    "e",
    "yu",
    "ya",
    "je",
    "i",
    "ji",
    "g",
)
TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()
class FileProcessor(ABC):
    @abstractmethod
    def process_file(self, file_path: Path, category: str, root_dir: Path) -> None:
        pass
class SimpleFileProcessor(FileProcessor):
    def __init__(self, file_list, ext_list):
        self.file_list = file_list
        self.ext_list = ext_list
    def process_file(self, file_path: Path, category: str, root_dir: Path) -> None:
        target_dir = root_dir.joinpath(category)
        if not target_dir.exists():
            target_dir.mkdir()
        new_path = target_dir.joinpath(normalize(file_path))
        file_path.replace(new_path)
        if new_path.name not in self.file_list[category]:
            self.file_list[category].append(new_path.name)
        if new_path.suffix not in self.ext_list[category]:
            self.ext_list[category].append(new_path.suffix)
        if category == "archives":
            self.unpack_archive(target_dir, new_path)
    def unpack_archive(self, directory: Path, archive: Path) -> None:
        dir_name = archive.name.rstrip(archive.suffix)
        unpack_path = directory.joinpath(dir_name)
        if archive.suffix.lower() == ".zip":
            with ZipFile(archive, "r") as zObj:
                zObj.extractall(unpack_path)
        else:
            shutil.unpack_archive(archive, unpack_path, archive.suffix)
class FileSorter:
    def __init__(self, file_processor: FileProcessor):
        self.file_processor = file_processor
    def sort_folder(self, path: Path) -> None:
        for i in path.glob("**/*"):
            if i.is_file():
                category = get_category(i)
                self.file_processor.process_file(i, category, path)
def normalize(file: Path) -> str:
    new_name = file.name.translate(TRANS)
    new_name = re.sub(r"[^a-z0-9A-Z.]", "_", new_name)
    return new_name
def write_in_file(file_list: dict, ext_list: dict, path: Path) -> None:
    for k, v in file_list.items():
        text = "\n".join(v)
        file_path = path.joinpath(k).joinpath(k + ".txt")
        with open(file_path, "w") as fh:
            fh.write(text)
    for k, v in ext_list.items():
        text = "\n".join(v)
        file_path = path.joinpath(k).joinpath(k + "_ext.txt")
        with open(file_path, "w") as fh:
            fh.write(text)
def get_category(file: Path) -> str:
    ext = file.suffix.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "other"
def delete_empty_folders(path: Path) -> None:
    for i in path.rglob("**/*"):
        if i.is_dir() and not os.listdir(i):
            shutil.rmtree(i)
def sort_main() -> str:
    folder = input("Enter path to folder you want to sort: ")
    try:
        path = Path(folder)
    except IndexError:
        return "No path entered"
    if not path.exists():
        return "Path does not exist"
    file_processor = SimpleFileProcessor()
    sorter = FileSorter(file_processor)
    sorter.sort_folder(path)
    delete_empty_folders(path)
    write_in_file(file_list, ext_list, path)
    return "Folder sorted"
if __name__ == "__main__":
    sort_main()