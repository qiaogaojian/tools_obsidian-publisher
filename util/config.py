import os
import sys
from environs import Env

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from singleton import Singleton

ENV_LOCAL = "local"
ENV_DEV = "dev"
ENV_BETA = "beta"
ENV_PROD = "prod"


class LoadConfig(Singleton):
    def __init__(self, env='dev', path_real2config="/../../config/.env"):
        """ 读取配置文件的类.
        env: config 环境
        path_real2config: config_class.py的相对路径 (这样设计是因为 config_class.py 的项目位置是固定的)
        """
        root_path = os.path.dirname(__file__) + path_real2config
        config_path = os.path.abspath(root_path + '.' + env)
        self.env_config = Env()
        self.env_config.read_env(path=root_path, override=True)
        self.env_config.read_env(path=config_path, override=True)

    def init(self, env='dev', path_real2config="/../../config/.env"):
        """ 读取配置文件的类.
        env: config 环境
        path_real2config: config_class.py的相对路径 (这样设计是因为 config_class.py 的项目位置是固定的)
        """
        root_path = os.path.dirname(__file__) + path_real2config
        config_path = os.path.abspath(root_path + '.' + env)
        self.env_config = Env()
        self.env_config.read_env(path=root_path, override=True)
        self.env_config.read_env(path=config_path, override=True)

    def get(self, param):
        value = self.env_config.str(param)
        return value

    def int(self, param):
        value = self.env_config.int(param)
        return value

    def str(self, param):
        value = self.env_config.str(param)
        return value

    def bool(self, param):
        value = self.env_config.bool(param)
        return value

    def list(self, param):
        value = self.env_config.list(param)
        return value

    def json(self, param):
        value = self.env_config.json(param)
        return value

    def datetime(self, param):
        value = self.env_config.datetime(param)
        return value

    def path(self, param):
        value = self.env_config.path(param)
        return value
