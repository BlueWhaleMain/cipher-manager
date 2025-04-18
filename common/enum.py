from enum import Enum


class DescriptionStrEnum(str, Enum):
    """ 字符串枚举 """
    description: str

    def __new__(cls, value, description=''):
        obj = super().__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj
