def filesize_convert(value, units=("B", "KB", "MB", "GB",), unit=1000.0):
    size = abs(value)
    index = 0

    while size >= unit and index < len(units) - 1:
        size /= unit
        index += 1

    return f"{"-" if value < 0 else ""}{size:.2f} {units[index]}"
