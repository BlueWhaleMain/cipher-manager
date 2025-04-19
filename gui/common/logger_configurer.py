import datetime
import logging.config
import os.path
import sys
import typing
import warnings
from logging.handlers import RotatingFileHandler

import pydantic


class LoggerConfigurer:
    """ 日志配置器 """
    __logger: logging.Logger = logging.getLogger(__name__)

    class Config(pydantic.BaseModel):
        """ 日志配置 """
        # 等级（默认INFO）
        level: str = 'INFO'
        formatter_str: typing.Optional[str] = None
        # %Y %m %d %H %M %S %f {name}
        # 年 月  日 时  分 秒 微秒 名称
        path_pattern: typing.Optional[str] = None

    def __init__(self, cfg: Config, logger: logging.Logger = logging.root):
        self._cfg = cfg
        self._formatter = logging.Formatter(cfg.formatter_str)
        self._logger = logger
        logger.setLevel(self._cfg.level.upper())

    def make_formatter(self) -> logging.Formatter:
        return logging.Formatter(self._cfg.formatter_str)

    def make_color_formatter(self) -> logging.Formatter:
        # noinspection PyPackageRequirements
        import colorlog
        return colorlog.ColoredFormatter(f'%(log_color)s{self._cfg.formatter_str}')

    def enable_console_handler(self, color: bool = False) -> logging.StreamHandler:
        """ 启动控制台输出 """
        handler = logging.StreamHandler(sys.stdout)
        formatter = None
        if color:
            try:
                formatter = self.make_color_formatter()
            except ImportError as e:
                warnings.warn(ImportWarning(e))
        if not formatter:
            formatter = self.make_formatter()
        handler.setFormatter(formatter)
        handler.setLevel(self._cfg.level.upper())
        self._logger.addHandler(handler)
        return handler

    def enable_file_handler(self, name: str) -> logging.FileHandler:
        """ 启动文件输出 """
        if not self._cfg.path_pattern:
            raise RuntimeError('must set path_pattern')
        filename = datetime.datetime.now().strftime(self._cfg.path_pattern).format(name=name)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        handler = RotatingFileHandler(filename, maxBytes=1024 * 1024 * 10, backupCount=10, encoding='utf-8')
        handler.setFormatter(self.make_formatter())
        handler.setLevel(self._cfg.level.upper())
        self._logger.addHandler(handler)
        return handler
