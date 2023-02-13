import os
import logging
import httpx
import time
import zipfile
import zlib
import shutil


def Singleton(cls):
    """Singleton decorator

    Args :
        * ``cls (object)`` : class to decorate

    Returns :
        * ``object`` : decorated class
    """
    def wrapper(*args, **kwargs):
        if not hasattr(cls, '__instance'):
            setattr(cls, '__instance', cls(*args, **kwargs))
        return getattr(cls, '__instance')
    return wrapper

def create_dir(path: str):
    """create a directory if not exists

    Args:
        * ``path (str)`` : directory path
    """
    if os.path.exists(path):
        logging.info(f"Directory {path} already exists, skip create")
    else:
        os.makedirs(path)
        logging.info(f"Directory {path} created")
        
def download_file(url: str, path: str):
    """Download file from url

    Args:
        * ``url (str)`` : url to download
        * ``path (str)`` : path to save file
    """
    def download_progress(num_bytes_downloaded: int, total: int, record: int, interval: int):
        if time.time() < record + interval:
            return record
        record = int(time.time())
        progress = int(num_bytes_downloaded / total * 100)    
        logging.info(f"Download progress: {progress}%, num_bytes_downloaded: {num_bytes_downloaded}, total: {total}")
        return record

    with httpx.stream("GET", url, follow_redirects=True) as response:
        total = int(response.headers.get("content-length", 0))
        record = 0
        with open(path, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
                num_bytes_downloaded = response.num_bytes_downloaded
                record = download_progress(num_bytes_downloaded, total, record, 5)
                

def extract_archive(path: str, target: str):
    """Extract archive file

    Args:
        * ``path (str)`` : archive file path
        * ``target (str)`` : target directory
    """
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(target)
        
def zip_dir(path: str, target: str):
    """Zip directory

    Args:
        * ``path (str)`` : directory to zip
        * ``target (str)`` : target archive file
    """
    with zipfile.ZipFile(target, 'w') as zip_ref:
        for root, dirs, files in os.walk(path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, path)
                zip_ref.write(os.path.join(root, file), rel_path)

        
def get_all_files(path: str):
    """Get all files in path

    Args:
        * ``path (str)`` : path to get files

    Returns:
        * ``list[str]`` : all files in path
    """
    all_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            target: str = os.path.join(root, file)
            all_files.append(target)
    return all_files

def crc(fileName):
    prev = 0
    for eachLine in open(fileName, "rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def delete_dir(path: str):
    if not os.path.exists(path):
        logging.warning(f"Path {path} not exists, skip delete")
        return
    return shutil.rmtree(path)

def get_all_dirs(path: str):
    """Get all directories in path

    Args:
        * ``path (str)`` : path to get directories

    Returns:
        * ``list[str]`` : all directories in path
    """
    all_dirs = []
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            target: str = os.path.join(root, dir)
            all_dirs.append(target)
    return all_dirs


def empty_dir(path: str):
    if not os.path.exists(path):
        create_dir(path)
    else:
        delete_dir(path)
        create_dir(path)
