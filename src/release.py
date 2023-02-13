from typing import Union
from .gh import GH

def Generate(access_token:str, limit:int, force_regenerate:bool, target_tag: Union[str, None] = None):
    gh = GH(access_token = access_token)
    if not gh.verify():
        return

    # 拉取指定的release tag, 没有设置则为最新的release
    target_tag = target_tag if target_tag else gh.get_latest_release()

    # 设置目标release tag
    gh.set_target_release(target_tag)

    # 创建目录
    gh.create_dirs()

    # 下载release
    gh.download_releases(limit)

    # 解压目标版本的release
   # gh.extract_target_tag_release()

    # 整理ota
    gh.make_ota()

    # 上传
    gh.make_release()
