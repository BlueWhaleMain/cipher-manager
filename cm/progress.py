import warnings
from enum import IntEnum
from threading import Event
from typing import Callable, Self, Iterable

from cm.error import CmInterrupt


class CmProgress:
    class Status(IntEnum):
        INACTIVE = 0
        RUNNING = 1
        COMPLETED = 2
        CANCELLED = 3
        HANGING = 4

    def __init__(self, total: int = 0, title: str = None, formatter: Callable[[int], str] = str, unit: str = 'steps'):
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
        return self._active_instance._current

    @property
    def current_str(self) -> str:
        _active_instance = self._active_instance
        return _active_instance._formatter(_active_instance.current)

    @property
    def total(self) -> int:
        return self._active_instance._total

    @property
    def total_str(self) -> str:
        _active_instance = self._active_instance
        return _active_instance._formatter(_active_instance._total)

    @property
    def unit(self) -> str:
        return self._active_instance._unit

    @property
    def title(self) -> str:
        return self._active_instance._title

    @property
    def last_msg(self) -> str:
        return self._active_instance._last_msg

    @property
    def status(self) -> Status:
        return self._status

    @property
    def running(self) -> bool:
        return self.status == self.Status.RUNNING or self.status == self.Status.HANGING

    @property
    def completed(self) -> bool:
        return self.status == self.Status.COMPLETED

    @property
    def canceled(self) -> bool:
        return self._canceled.is_set()

    @property
    def hanging(self) -> bool:
        return self.status == self.Status.HANGING

    @property
    def progresses(self) -> Iterable[Self]:
        if self._sub_progress is None:
            yield self
        else:
            for progress in self._sub_progress.progresses:
                yield progress

    @property
    def _active_instance(self) -> Self:
        return self if self._sub_progress is None else self._sub_progress._active_instance

    def start(self, total: int = 0, formatter: Callable[[int], str] = str, unit: str = 'steps') -> None:
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
        if self._parent is not None and self._parent.hanging:
            self._parent.continue_()

    def continue_(self) -> None:
        if self._status != self.Status.HANGING:
            raise RuntimeError(f'status is {self.status}')
        if not self._sub_progress:
            raise RuntimeError('no progress')
        if self._sub_progress.running:
            raise RuntimeError(f'sub_progress is already running')
        self._sub_progress = None
        self._status = self.Status.RUNNING

    def cancel(self):
        if self._sub_progress:
            self._sub_progress.cancel()
        self._canceled.set()
        if self._status == self.Status.RUNNING:
            self._status = self.Status.CANCELLED
