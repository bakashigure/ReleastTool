import os
import logging
import httpx
import time
import zipfile


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
    """Create directory if not exists

    Args:
        * ``path (str)`` : directory path
    """
    if os.path.exists(path):
        logging.info(f"Directory {path} already exists, skip creating")
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