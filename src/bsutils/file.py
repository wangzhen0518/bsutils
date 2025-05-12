'''
Author       : wangzhen0518 wangzhen0518@126.com
Date         : 2025-04-03 16:25 +0800
LastEditors  : wangzhen0518 wangzhen0518@126.com
LastEditTime : 2025-05-09 19:26 +0800
FilePath     : file.py
Description  : 

'''
import os


def pure_file_name(filename: str, keep_extension: bool = False) -> str:
    """Extracts the pure file name without path and extension.

    This function takes a file path or full file name and returns only the base name
    without the directory path and file extension.

    Args:
        filename: Input file path or full file name (e.g. '/path/to/file.txt' or 'file.txt')

    Returns:
        The pure file name without path and extension (e.g. 'file' for '/path/to/file.txt')

    Examples:
        >>> pure_file_name('/path/to/document.pdf')
        'document'
        >>> pure_file_name('data.json')
        'data'
        >>> pure_file_name('archive.tar.gz')
        'archive.tar'
    """

    filename = os.path.basename(filename)
    if not keep_extension:
        filename = ".".join(filename.split(".")[:-1])
    return filename
