import datetime
import logging.config
import os.path
import sys
import typing
import warnings

import pydantic


class LoggerConfigurer:
    """ 日志配置器 """
    __logger = logging.getLogger(__name__)

    class Config(pydantic.BaseModel):
        """ 日志配置 """
        # 等级（默认INFO）
        level: str = 'INFO'
        formatter_str: typing.Optional[str] = None
        # %Y %m %d %H %M %S %f {name} {sequence}
        # 年 月  日 时  分 秒 微秒 名称   序号
        path_pattern: typing.Optional[str] = None

    def __init__(self, cfg: Config, logger: logging.Logger = logging.root):
        self._cfg = cfg
        self._formatter = logging.Formatter(cfg.formatter_str)
        self._logger = logger
        logger.setLevel(self._cfg.level.upper())

    def make_formatter(self) -> logging.Formatter:
        return logging.Formatter(self._cfg.formatter_str)

    def make_color_formatter(self) -> logging.Formatter:
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
            raise RuntimeError
        filename = datetime.datetime.now().strftime(self._cfg.path_pattern).format(name=name, sequence='{sequence}')
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        t_filename = filename.format(sequence='')
        if os.path.exists(t_filename):
            if filename == filename.format(sequence='?'):
                raise ValueError(self._cfg.path_pattern)
            seq = 1
            while os.path.exists(t_filename):
                t_filename = filename.format(sequence=f'-{seq}')
                seq += 1
        filename = t_filename
        handler = logging.FileHandler(filename)
        handler.setFormatter(self.make_formatter())
        handler.setLevel(self._cfg.level.upper())
        self._logger.addHandler(handler)
        return handler
