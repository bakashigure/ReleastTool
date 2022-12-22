import os
import logging
from typing import Optional, Union
from github import Github
from .utils import Singleton, create_dir, download_file, get_all_files, extract_archive

@Singleton
class GH:
    """gh agent
    """
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.ui_repo = 'MaaAssistantArknights/MaaAsstElectronUI'
        self.release_repo = 'bakashigure/ReleastTool'
        self.dist_path = os.getcwd() + '/dist'
        self.release_path = os.getcwd() + '/target_tag'
        self.temp_path = os.getcwd() + '/temp'
        self.download_path = os.getcwd() + '/download'
        self.tags = []
        self.target_tag = None

    def verify(self) -> bool:
        try:
            self.g = Github(login_or_token=self.access_token)
            user_name = self.g.get_user().login
            logging.info(f"Login as github user: {user_name}")
            return True
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return False
    
    def get_latest_release(self) -> str:
        repo = self.g.get_repo(self.ui_repo)
        return repo.get_latest_release().tag_name
    
    def set_target_release(self, tag_name: Union[str, None] = None) -> None:
        if not tag_name:
            tag_name = self.get_latest_release()
        self.target_tag = tag_name
        
    def create_dirs(self) -> None:
        create_dir(self.dist_path)
        create_dir(self.release_path)
        create_dir(self.download_path)
        
    def download_releases(self, limit: int):
        releases = self.g.get_repo(self.ui_repo).get_releases().get_page(0)
        for release in releases:
            if limit == 0:
                break
            limit -= 1
            assets = release.get_assets().get_page(0)
            for asset in assets:
                # todo: 文件名匹配规则
                if asset.name.endswith('.zip'):
                    logging.info(f"Downloading {asset.name}")
                    download_file(asset.browser_download_url, self.download_path + '/' + asset.name)
                    logging.info(f"Downloaded {asset.name}")
                    break
    
    def extract_target_tag_release(self):
        files = get_all_files(self.download_path)
        target_path = None
        for file in files:
            if file.find(self.target_tag):
                target_path = file
                break
        if not target_path:
            logging.error(f"Can't find target tag release: {self.target_tag}")
            return False
        logging.info(f"Extracting {target_path}")
        extract_archive(target_path, self.release_path)
        