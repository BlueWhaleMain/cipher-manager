import os
import sys
import traceback
import typing

import psutil


class Console:
    """ 控制台 """
    _IS_NATIVE_CONSOLE: typing.Final[bool] = psutil.Process(os.getppid()).name() != 'idea64.exe'

    def __init__(self):
        self._prompt = ''

    def write(self, val):
        print(val)
        self.flush()

    def flush(self):
        sys.stdout.write(f'{self._prompt}\r')
        sys.stdout.flush()

    @classmethod
    def clear(cls) -> None:
        if cls._IS_NATIVE_CONSOLE:
            if os.name == 'posix':
                os.system('clear')
                return
            if os.name == 'nt':
                os.system('cls')
                return
        print('\n' * 150)

    def input(self, prompt: str = '', mask: str = '') -> str:
        if mask:
            if self._IS_NATIVE_CONSOLE:
                if os.name == 'nt':
                    self._prompt = prompt
                    try:
                        import msvcrt
                    except ImportError:
                        msvcrt = None
                    if msvcrt:
                        return self._win_input(msvcrt.getwch, mask)
                else:
                    try:
                        import getpass
                    except ImportError:
                        getpass = None
                    if getpass:
                        return getpass.getpass(prompt)
            print('输入隐藏无效')
            r = input(prompt)
            self.clear()
            return r
        return input(prompt)

    @classmethod
    def protect_show(cls, pwd: str):
        if cls._IS_NATIVE_CONSOLE:
            if os.name == 'nt':
                try:
                    import msvcrt
                except ImportError:
                    msvcrt = None
                if msvcrt:
                    sys.stdout.write(pwd + '\r')
                    sys.stdout.flush()
                    msvcrt.getwch()
                    sys.stdout.write(' ' * len(pwd) + '\r')
                    sys.stdout.flush()
                    return
        print(pwd)
        input()
        cls.clear()

    def _win_input(self, gch: typing.Callable[[], typing.AnyStr], mask: str = ''):
        result = ''
        self.flush()
        raw = self._prompt
        max_len = len(raw)
        while 1:
            c = gch()
            if c == '\r' or c == '\n':
                break
            if c == '\003':
                raise KeyboardInterrupt
            if c == '\b':
                result = result[:-1]
            else:
                result = result + c
            if mask:
                self._prompt = raw + mask * len(result)
            else:
                self._prompt = raw + result
            max_len = max(len(self._prompt) + len(raw), max_len)
            sys.stdout.write(' ' * max_len + '\r')
            sys.stdout.flush()
            self.flush()
        sys.stdout.write('\r\n')
        sys.stdout.flush()
        return result

    def get_input(self, prompt: str = '输入：', mask: str = '', v_callback=None, v_args: tuple = None) -> str:
        custom_input = ''
        try:
            _input = ''
            while not _input or str.isspace(_input):
                _input = self.input(prompt, mask)
                if v_callback and not v_callback(_input, *v_args):
                    _input = ''
            custom_input = _input
        except (KeyboardInterrupt, EOFError):
            print('放弃输入')
        finally:
            if custom_input:
                return custom_input
            raise KeyboardInterrupt('输入未完成')

    def verify_input(self, _input, mask):
        try:
            while True:
                if self.input('再次输入确认：', mask) == _input:
                    return True
                else:
                    print('两次输入的值不一致')
        except (KeyboardInterrupt, EOFError):
            return False

    def choice(self, prompt: str = '', item: tuple = None, verify: bool = False, v_prompt: str = '确定选择：',
               default: str = '', retry: int = 3, match_case: bool = False) -> int:
        """ 选择列表
        :param match_case:匹配大小写
        :param prompt:输入提示
        :param item: 选择列表，默认YN
        :param verify:确认选择
        :param v_prompt:确认选择的提示
        :param default:输入默认值
        :param retry:容错次数
        :return: 注意此函数返回的都是从零开始的下标！
        """
        if item is None:
            item = ('N', 'Y')
        elif not len(item):
            raise ValueError('待选择列表不能为空！')
        _item = list()
        for i in item:
            i = str(i)
            if not match_case:
                i = i.upper()
            if i not in _item:
                _item.append(i)
        if len(item) != len(_item):
            raise ValueError('含有重复参数')
        cin = None
        if default:
            cin = default
        for i in range(retry):
            if not cin:
                cin = self.input(prompt + f'[{",".join(_item)}]?')
                if not match_case:
                    cin = cin.upper()
            if cin in _item:
                if not verify or self.choice(f'{v_prompt}{cin}'):
                    return _item.index(cin)
            else:
                print('不规范的输入，请检查匹配列表')
            cin = None
        else:
            raise KeyboardInterrupt('选择次数过多！')

    @classmethod
    def get_error(cls, exc_info) -> str:
        exc_type, exc_value, exc_traceback = ('', '', '')
        if isinstance(exc_info, BaseException):
            exc_type, exc_value, exc_traceback = (type(exc_info), exc_info, exc_info.__traceback__)
        elif not isinstance(exc_info, tuple):
            exc_type, exc_value, exc_traceback = sys.exc_info()
        return ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
