from typing import Sequence


def filesize_convert(value: int, units: Sequence[str] = ("B", "KB", "MB", "GB",), unit: float = 1000.0) -> str:
    """
    文件大小格式化

    Args:
        value: 字节数
        units: 用到的单位序列
        unit: 单位长度

    Returns:
        格式化文本
    """
    size = abs(value)
    index = 0

    while size >= unit and index < len(units) - 1:
        size /= unit
        index += 1

    return f"{"-" if value < 0 else ""}{size:.2f} {units[index]}"
