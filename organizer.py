from sys import argv
import os
import shutil
from pathlib import Path
from transliteration import normalize_name
from concurrent.futures import ThreadPoolExecutor, wait


IMAGES = (".jpeg", ".png", ".jpg", ".svg", ".bmp", ".heic")
VIDEOS = (".avi", ".mp4", ".mov", ".mkv")
DOCS = (".doc", ".docx", ".txt", ".pdf", ".xls", ".pptx", ".xlsx")
AUDIO = (".mp3", ".ogg", ".wav", ".amr")
ARCHIVES = (".zip", ".gz", ".tar", ".tar.gz")

IMAGE_DIR = "images"
AUDIO_DIR = "audio"
VIDEO_DIR = "video"
DOCUMENTS_DIR = "documents"
ARCHIVES_DIR = "archives"

ignored_folders = [IMAGE_DIR, VIDEO_DIR, DOCUMENTS_DIR, AUDIO_DIR, ARCHIVES_DIR]


def move_file(f: str, path: str, folder_name: str) -> None:
    """
    Moves the given file into corresponding folder depending on the file extension.
    :param f: path to the file
    :param path: path to the directory where the file is
    :param folder_name: name of a folder to move the file to
    """
    new_path = os.path.join(path, folder_name)
    if os.path.exists(new_path):
        shutil.move(f, os.path.join(new_path, os.path.basename(f)))
    else:
        os.mkdir(os.path.join(path, folder_name))
        shutil.move(f, os.path.join(new_path, os.path.basename(f)))


def move_archive(f: str, path: str) -> None:
    """
    Moves the archive to the "archives" directory, unpacks it into the folder and deletes the original archive.
    :param f: path to the archive
    :param path: path to the directory where the file is
    """
    new_path = os.path.join(path, ARCHIVES_DIR)
    if os.path.exists(new_path):
        new_addr = os.path.join(new_path, os.path.basename(f))
        shutil.move(f, new_addr)
        shutil.unpack_archive(new_addr, os.path.join(new_addr, os.path.splitext(new_addr)[0]))
        os.remove(new_addr)
    else:
        os.mkdir(os.path.join(path, ARCHIVES_DIR))
        new_addr = os.path.join(new_path, os.path.basename(f))
        shutil.move(f, new_addr)
        shutil.unpack_archive(new_addr, os.path.join(new_addr, os.path.splitext(new_addr)[0]))
        os.remove(new_addr)


def is_empty_dir(directory: str) -> bool:
    """
    Checks if the directory is empty.
    :param directory: path to the directory
    :return: True if the directory is empty, False otherwise
    """
    return len(os.listdir(directory)) == 0


def sort_file(path: str) -> None:
    """
    Traverses the given folder, deletes it if empty, sorts the files in it according to their extensions.
    :param path: path to the given folder
    """
    for filename in os.listdir(path):
        f = os.path.join(path, filename)
        if os.path.isdir(f):
            if filename in ignored_folders:
                continue
            if is_empty_dir(f):
                os.rmdir(f)
        else:
            new_path = os.path.join(path, normalize_name(f))
            if not os.path.exists(new_path):
                os.rename(f, new_path)
            extension = Path(new_path).suffix.lower()

            if extension in IMAGES:
                move_file(new_path, path, IMAGE_DIR)
            elif extension in VIDEOS:
                move_file(new_path, path, VIDEO_DIR)
            elif extension in DOCS:
                move_file(new_path, path, DOCUMENTS_DIR)
            elif extension in AUDIO:
                move_file(new_path, path, AUDIO_DIR)
            elif extension in ARCHIVES:
                move_archive(new_path, path)


def find_subfolders(path: str) -> list:
    """
    Traverses the target folder and finds all the subfolders.
    :param path: path to the target folder
    :return: list of paths to the subfolders of the target folder
    """
    subfolders = [folder[0] for folder in os.walk(path) if folder not in ignored_folders]
    return subfolders


def sort_folder():
    """
    Takes subfolders of the target folder and sorts them in different threads.
    """
    if len(argv) != 2:
        print("You have to specify the path to the directory to organize.")
        quit()

    path = argv[1]
    subfolders = find_subfolders(path)

    with ThreadPoolExecutor() as executor:
        for folder in subfolders:
            executor.submit(sort_file, folder)


if __name__ == "__main__":
    sort_folder()
