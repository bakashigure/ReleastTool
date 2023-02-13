import os
import logging
from typing import Optional, Union, Dict, Literal, List
from github import Github
from pathlib import Path
import shutil
import re
from .utils import Singleton, create_dir, download_file, get_all_files, extract_archive, delete_dir, get_all_dirs, crc, zip_dir, empty_dir

ReleaseObject = List[Dict[Literal['os', 'arch', 'version', 'path'], str]]


@Singleton
class GH:
    """gh agent
    """

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.ui_repo = 'MaaAssistantArknights/MaaAsstElectronUI'
        self.release_repo = 'bakashigure/ReleastTool'
        self.dist_path = os.getcwd() + r'\dist'
        self.release_path = os.getcwd() + r'\target_tag'
        self.temp_path = os.getcwd() + r'\temp'
        self.download_path = os.getcwd() + r'\download'
        self.upload_path = os.getcwd() + r'\upload'
        self.tags: ReleaseObject = []
        self.ota_path = os.getcwd() + r'\ota'
        self.target_tag = None

        self.release_regex = re.compile(r'MaaAssistantArknights-(\w*)-(\w*)-([\.\w-]*).zip')

    def verify(self) -> bool:
        try:
            self.g = Github(login_or_token=self.access_token)
            user_name = self.g.get_user().login
            logging.info(f"Login as github user: {user_name}")
            return True
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return False

    def add_release(self, os, arch, version, path) -> None:
        self.tags.append({"os": os, "arch": arch, "version": version, "path": path})

    @staticmethod
    def filename_template(full: bool, cur_tag: str, target_tag: str, os: str, arch: str) -> str:
        if full:
            return f"MaaElectronUI_FULL-{os}-{arch}-{cur_tag}.zip"
        else:
            return f"MaaElectronUI_OTA-{os}-{arch}-{cur_tag}..{target_tag}.zip"

    def get_latest_release(self) -> str:
        repo = self.g.get_repo(self.ui_repo)
        return repo.get_latest_release().tag_name

    def set_target_release(self, tag_name: Union[str, None] = None) -> None:
        if not tag_name:
            tag_name = self.get_latest_release()
        self.target_tag = tag_name[1:]  # v2.0.0-alpha.17 -> 2.0.0-alpha.17
        logging.info(f"Target tag: {self.target_tag}")

    def create_dirs(self) -> None:
        create_dir(self.dist_path)
        create_dir(self.release_path)
        create_dir(self.download_path)
        create_dir(self.temp_path)
        create_dir(self.upload_path)
        create_dir(self.ota_path)

    def download_releases(self, limit: int) -> None:
        releases = self.g.get_repo(self.ui_repo).get_releases().get_page(0)
        for release in releases:
            if limit == 0:
                break
            limit -= 1
            assets = release.get_assets().get_page(0)
            for asset in assets:
                if asset.name.endswith('.zip'):
                    file_path = self.download_path + '/' + asset.name
                    if not os.path.exists(file_path):
                        logging.info(f"Downloading {asset.name}")
                        download_file(asset.browser_download_url, file_path)
                    else:
                        logging.info(f"File exists: {file_path}")
                    logging.info(f"Downloaded {asset.name}")
                    release_regex_res = self.release_regex.match(asset.name)
                    try:
                        if not release_regex_res:
                            logging.error(f"Release name not match: {asset.name}")
                            continue
                        r = release_regex_res.group
                        _os, _arch, _version = r(1), r(2), r(3)
                        self.add_release(_os, _arch, _version, file_path)

                    except Exception as e:
                        logging.error(f"Release name not match: {asset.name}")

    # @deprecated
    # def extract_target_tag_release(self, path):
    #     if not self.target_tag:
    #         logging.error("Target tag is None")
    #         return False
    #     if self.target_tag not in self.tags:
    #         logging.error(f"Can't find target tag release: {self.target_tag}")
    #         return False
    #     target_path = self.tags[self.target_tag]
    #     logging.info(f"Extracting {target_path}")
    #     #extract_archive(target_path, self.release_path)
    #     #extract_archive(target_path, self.temp_path)
    #     return True

    def make_ota(self):
        """比对target_tag与其他版本的差异, 生成ota包

        """
        empty_dir(self.upload_path)
        target_releases = [item for item in self.tags if item['version'] == self.target_tag]  # target_tag的所有版本
        for item in target_releases:
            # 先传全包
            full_file_name = self.filename_template(True, item['version'], item['version'], item['os'], item['arch'])
            shutil.copyfile(item['path'], self.upload_path + '/' + full_file_name)
            empty_dir(self.release_path)  # 清空路径内容
            extract_archive(item['path'], self.release_path)  # 解压对应版本的全包
            ota_list = [obj for obj in self.tags if item['version'] != obj['version'] and item['os'] == obj['os'] and item['arch'] == obj['arch']]  # 所有同架构os但是版本不同的包

            for obj in ota_list:
                ota_file_name = self.filename_template(False, obj['version'], item['version'], item['os'], item['arch'])
                logging.info("Making ota: " + ota_file_name)
                empty_dir(self.temp_path)  # OTA版本解压
                empty_dir(self.ota_path)   # 增量文件

                extract_archive(obj['path'], self.temp_path)

                temp_prefix = len(self.temp_path) + 1
                release_prefix = len(self.release_path) + 1

                target_path = Path(self.release_path)
                for new_file_path in target_path.rglob('*'):
                    if new_file_path.is_file():
                        new_path = new_file_path.parent
                        new_releative_path = new_path.__str__()[release_prefix:]
                        new_file_releative_path = new_file_path.__str__()[release_prefix:]
                        old_file_path = Path.joinpath(Path(self.temp_path), new_file_releative_path)
                        old_path = old_file_path.parent

                        ota_file_path = Path.joinpath(Path(self.ota_path), new_file_releative_path)
                        ota_path = ota_file_path.parent
                        if not old_file_path.exists():
                            if not old_path.exists():
                                ota_releative_path = Path.joinpath(Path(self.ota_path), new_releative_path)
                                os.makedirs(ota_releative_path, exist_ok = True)
                            os.makedirs(ota_path, exist_ok=True)
                            shutil.copyfile(new_file_path, ota_file_path)
                        else:
                            old_crc = crc(old_file_path)
                            new_crc = crc(new_file_path)
                            if old_crc != new_crc:
                                os.makedirs(ota_path, exist_ok = True)
                                shutil.copyfile(new_file_path, ota_file_path)

                zip_dir(self.ota_path, self.upload_path + '/' + ota_file_name)

        return True

    def make_release(self):
        repo = self.g.get_repo(self.release_repo)

        release = repo.create_git_release(
            tag = 'v' + str(self.target_tag),
            message = 'Release v' + str(self.target_tag),
            name = 'v' + str(self.target_tag),
            draft = False,
            prerelease = False,
        )

        for f in Path(self.upload_path).glob('*'):
            if f.is_file():
                asset = release.upload_asset(
                    path = f.__str__(),
                    label = f.name,
                )
                logging.info(f'Uploaded asset {f.name}')