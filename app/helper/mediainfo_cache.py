import pickle
import random
import time
import traceback
from pathlib import Path
from threading import RLock
from typing import Optional

from app.core.config import settings
from app.log import logger
from app.utils.singleton import Singleton

lock = RLock()

class MediaInfoCache(metaclass=Singleton):
    """
    本地媒体库 nfo 和 图片更新时记录，下次更新内容一致时不再更新。

    图片 filepath:url 
    nfo filepath:nfo
    {
        'path':''
    }
    """
    _meta_data: dict = {}
    # 缓存文件路径
    _meta_path: Path = None
    

    def __init__(self):
        self._meta_path = settings.TEMP_PATH / "__media_info_cache__.text"
        self._meta_data = self.__load(self._meta_path)

    def clear(self):
        """
        清空缓存
        """
        with lock:
            self._meta_data = {}

    def get(self, filepath: str):
        """
        根据 filepath 获取值
        """
        with lock:
            info: str = self._meta_data.get(filepath)
            return info or ""

    def delete(self, key: str) -> dict:
        """
        删除缓存信息
        @param key: 缓存 filepath
        @return: 被删除的缓存内容
        """
        with lock:
            value = self._meta_data.pop(key, None)
            return value


    def modify(self, key: str, value: str) -> dict:
        """
        修改缓存信息
        @param key: 缓存 filepath
        @return: 被删除的缓存内容
        """
        with lock:
            self._meta_data[key] = value

    @staticmethod
    def __load(path: Path) -> dict:
        """
        从文件中加载缓存
        """
        try:
            if path.exists():
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                return data
            return {}
        except Exception as e:
            logger.error(f'加载缓存失败：{str(e)} - {traceback.format_exc()}')
            return {}

    def save(self) -> None:
        """
        保存缓存数据到文件
        """
        with lock:
            new_meta_data = self._meta_data

        with open(self._meta_path, 'wb') as f:
            pickle.dump(new_meta_data, f, pickle.HIGHEST_PROTOCOL)

    
