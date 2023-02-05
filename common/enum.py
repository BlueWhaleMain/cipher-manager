import enum


class DescriptionIntEnum(int, enum.Enum):
    """ 数字枚举 """

    def __new__(cls, value, description=''):
        obj = super().__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    def __hash__(self):
        return hash(self._name_)

    @classmethod
    def get_member_list(cls, fix_size: int = 0):
        member_index_list = [*cls._value2member_map_]
        member_index_list.sort()
        member_list = []
        if not member_index_list:
            return member_list
        if fix_size:
            for i in range(fix_size):
                if i in member_index_list:
                    member_list.append(cls._value2member_map_[i])
                else:
                    member_list.append(None)
        else:
            for i in member_index_list:
                member_list.append(cls._value2member_map_[i])
        return frozenset(member_list)


class DescriptionStrEnum(str, enum.Enum):
    """ 字符串枚举 """

    def __new__(cls, value, description=''):
        obj = super().__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    def __hash__(self):
        return hash(self._name_)
