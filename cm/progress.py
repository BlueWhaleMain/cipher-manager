from enum import IntEnum
from threading import Event
from typing import Callable

from cm.error import CmInterrupt


class CmProgress:
    class Status(IntEnum):
        INACTIVE = 0
        RUNNING = 1
        COMPLETED = 2
        CANCELLED = 3

    def __init__(self, total: int = 0, title: str = None, formatter: Callable[[int], str] = str, unit: str = 'steps'):
        self._current = 0
        self._total = total
        self._title = title
        self._formatter = formatter
        self._unit = unit
        self._status = self.Status.INACTIVE
        self._canceled = Event()
        self._last_msg: str = ''

    @property
    def current(self) -> int:
        return self._current

    @property
    def current_str(self) -> str:
        return self._formatter(self.current)

    @property
    def total(self) -> int:
        return self._total

    @property
    def total_str(self) -> str:
        return self._formatter(self._total)

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def title(self) -> str:
        return self._title

    @property
    def last_msg(self) -> str:
        return self._last_msg

    @property
    def status(self) -> Status:
        return self._status

    @property
    def running(self) -> bool:
        return self.status == self.Status.RUNNING

    @property
    def completed(self) -> bool:
        return self.status == self.Status.COMPLETED

    @property
    def canceled(self) -> bool:
        return self._canceled.is_set()

    def start(self, total: int = 0, formatter: Callable[[int], str] = str, unit: str = 'steps') -> None:
        if self._status != self.Status.INACTIVE:
            raise RuntimeError(f'status is {self.status}')
        self._canceled.clear()
        self._current = 0
        self._total = total
        self._formatter = formatter
        self._unit = unit
        self._status = self.Status.RUNNING

    def step(self, amount: int = 1, last_msg: str = '') -> None:
        if self.canceled:
            raise CmInterrupt
        if self._status != self.Status.RUNNING:
            raise RuntimeError(f'status is {self.status}')
        self._current += amount
        self._last_msg = last_msg

    def reset(self) -> None:
        if self._status != self.Status.RUNNING:
            raise RuntimeError(f'status is {self.status}')
        self._current = 0
        self._status = self.Status.INACTIVE

    def restart(self, total: int = 0, formatter: Callable[[int], str] = str, unit: str = 'steps') -> None:
        self.reset()
        self.start(total, formatter, unit)

    def complete(self) -> None:
        if self._status != self.Status.RUNNING:
            raise RuntimeError(f'status is {self.status}')
        self._status = self.Status.COMPLETED

    def cancel(self):
        self._canceled.set()
        if self._status == self.Status.RUNNING:
            self._status = self.Status.CANCELLED
