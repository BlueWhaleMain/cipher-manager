#  MIT License
#
#  Copyright (c) 2022-2025 BlueWhaleMain
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
import warnings
from enum import IntEnum
from threading import Event
from typing import Callable, Self, Iterable

from cm.error import CmInterrupt


class CmProgress:
    """进度管理器"""

    class Status(IntEnum):
        """状态"""
        INACTIVE = 0
        RUNNING = 1
        COMPLETED = 2
        CANCELLED = 3
        HANGING = 4

    def __init__(self, total: int = 0, title: str = None, formatter: Callable[[int], str] = str, unit: str = 'steps'):
        """
        Args:
            total: 进度总量，为0视作无限
            title: 进度标题
            formatter: 进度格式化器，默认转为字符串
            unit: 进度单位表述，默认为步骤数
        """
        self._current = 0
        self._total = total
        self._title = title
        self._formatter = formatter
        self._unit = unit
        self._status = self.Status.INACTIVE
        self._canceled = Event()
        self._last_msg: str = ''
        self._sub_progress: Self = None
        self._parent: Self = None

    def __del__(self):
        if self.running:
            warnings.warn('progress already running')

    @property
    def current(self) -> int:
        """
        Returns:
            当前进度
        """
        return self._active_instance._current

    @property
    def current_str(self) -> str:
        """
        Returns:
            当前进度的字符串表述
        """
        _active_instance = self._active_instance
        return _active_instance._formatter(_active_instance.current)

    @property
    def total(self) -> int:
        """
        Returns:
            总体进度
        """
        return self._active_instance._total

    @property
    def total_str(self) -> str:
        """
        Returns:
            总体进度的字符串表述
        """
        _active_instance = self._active_instance
        return _active_instance._formatter(_active_instance._total)

    @property
    def unit(self) -> str:
        """
        Returns:
            单位
        """
        return self._active_instance._unit

    @property
    def title(self) -> str:
        """
        Returns:
            标题
        """
        return self._active_instance._title

    @property
    def last_msg(self) -> str:
        """
        Returns:
            最后一条步骤信息
        """
        return self._active_instance._last_msg

    @property
    def status(self) -> Status:
        """
        Returns:
            当前状态
        """
        return self._status

    @property
    def running(self) -> bool:
        """
        Returns:
            当前是否运行中
        """
        return self.status == self.Status.RUNNING or self.status == self.Status.HANGING

    @property
    def completed(self) -> bool:
        """
        Returns:
            当前是否已完成
        """
        return self.status == self.Status.COMPLETED

    @property
    def canceled(self) -> bool:
        """
        Returns:
            当前是否已取消
        """
        return self._canceled.is_set()

    @property
    def hanging(self) -> bool:
        """
        Returns:
            当前是否被挂起
        """
        return self.status == self.Status.HANGING

    @property
    def progresses(self) -> Iterable[Self]:
        """
        Returns:
            所有进度

        按嵌套关系排列
        """
        if self._sub_progress is None:
            yield self
        else:
            for progress in self._sub_progress.progresses:
                yield progress

    @property
    def _active_instance(self) -> Self:
        """活动中的实例"""
        return self if self._sub_progress is None else self._sub_progress._active_instance

    def start(self, total: int = 0, formatter: Callable[[int], str] = str, unit: str = 'steps') -> None:
        """
        启动一个进度

        Args:
            total: 进度总量，为0视作无限
            formatter: 进度格式化器，默认转为字符串
            unit: 进度单位表述，默认为步骤数
        """
        if self._status != self.Status.INACTIVE:
            raise RuntimeError(f'status is {self.status}')
        self._canceled.clear()
        self._current = 0
        self._total = total
        self._formatter = formatter
        self._unit = unit
        self._status = self.Status.RUNNING

    def start_or_sub(self, total: int = 0, title: str = None, formatter: Callable[[int], str] = str,
                     unit: str = 'steps') -> Self:
        """
        启动或创建一个子进度
        Args:
            total: 进度总量，为0视作无限
            title: 进度标题
            formatter: 进度格式化器，默认转为字符串
            unit: 进度单位表述，默认为步骤数

        Returns:
            当前进度或子进度
        """
        if self._status == self.Status.INACTIVE:
            self.start(total, formatter, unit)
            return self
        if self._status != self.Status.RUNNING:
            raise RuntimeError(f'status is {self.status}')
        self._status = self.Status.HANGING
        sub_progress = CmProgress(title=title if title else self._title)
        sub_progress.start(total=total, formatter=formatter, unit=unit)
        sub_progress._parent = self
        self._sub_progress = sub_progress
        return sub_progress

    def step(self, amount: int = 1, last_msg: str = '') -> None:
        """
        执行一步

        Args:
            amount: 进步量
            last_msg: 当前步骤额外消息
        """
        if self.canceled:
            raise CmInterrupt
        if self._status != self.Status.RUNNING:
            raise RuntimeError(f'status is {self.status}')
        self._current += amount
        self._last_msg = last_msg

    def reset(self) -> None:
        """重置进度"""
        if self._status != self.Status.RUNNING:
            raise RuntimeError(f'status is {self.status}')
        self._current = 0
        self._status = self.Status.INACTIVE

    def restart(self, total: int = 0, formatter: Callable[[int], str] = str, unit: str = 'steps') -> None:
        """
        重启进度

        Args:
            total: 进度总量，为0视作无限
            formatter: 进度格式化器，默认转为字符串
            unit: 进度单位表述，默认为步骤数
        """
        self.reset()
        self.start(total, formatter, unit)

    def complete(self) -> None:
        """完成任务"""
        if self._status != self.Status.RUNNING:
            raise RuntimeError(f'status is {self.status}')
        self._status = self.Status.COMPLETED
        if self._parent is not None and self._parent.hanging:
            self._parent.continue_()

    def continue_(self) -> None:
        """恢复步骤的挂起状态"""
        if self._status != self.Status.HANGING:
            raise RuntimeError(f'status is {self.status}')
        if not self._sub_progress:
            raise RuntimeError('no progress')
        if self._sub_progress.running:
            raise RuntimeError(f'sub_progress is already running')
        self._sub_progress = None
        self._status = self.Status.RUNNING

    def cancel(self):
        """取消任务"""
        if self._sub_progress:
            self._sub_progress.cancel()
        self._canceled.set()
        if self._status == self.Status.RUNNING:
            self._status = self.Status.CANCELLED
