import pyjson5
from typing import Generator


def check_json_file_type(filename: str) -> str:
    """
    Check if the given filename has a valid JSON or JSONL extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        str: The file extension (either 'json' or 'jsonl').

    Raises:
        ValueError: If the file extension is neither 'json' nor 'jsonl'.
    """
    ext = filename.split(".")[-1]
    if ext not in {"json", "jsonl"}:
        raise ValueError(f"Unknown file type .{ext}: {filename}")
    else:
        return ext


def iter_json_file(filename: str, ignore_exception: bool = True) -> Generator[dict, None, None]:
    """
    Iterate over items in a JSON or JSONL file.

    This generator reads the given file and yields each item (dictionary) from a JSON array
    or JSONL lines. If the file is a JSON file but parsing fails, it attempts to read it
    as a JSONL file. For JSON files, if the content is not a list and `ignore_exception` is False,
    an exception is raised.

    Args:
        filename (str): The name of the file to read.
        ignore_exception (bool, optional): Whether to ignore parsing errors and continue.
            Defaults to True.

    Yields:
        dict: A dictionary representing the parsed JSON item.

    Raises:
        ValueError: If the file extension is invalid (raised by `check_json_file_type`).
        Exception: If `ignore_exception` is False and a parsing error occurs or the JSON content
            is not a list.
    """

    def _iter_jsonl(f, ignore_exception: bool):
        for line in f:
            try:
                item = pyjson5.loads(line)
            except Exception as e:
                if ignore_exception:
                    print(f"Error: {e}\ncontent: {line}")
                else:
                    raise e
            else:
                yield item

    ext = check_json_file_type(filename)
    with open(filename, "r", encoding="utf8") as f:
        if ext == "json":
            try:
                content = pyjson5.load(f)  # type: ignore
            except Exception:
                f.seek(0)
                yield from _iter_jsonl(f, ignore_exception)
            else:
                if isinstance(content, list):
                    for item in content:
                        yield item
                elif not ignore_exception:
                    raise ValueError(f"Type of content of file {filename} should be list, but now it is {type(content)}.")
        else:  # jsonl
            yield from _iter_jsonl(f, ignore_exception)


def get_item_num(filename: str, ignore_exception: bool = True) -> int:
    """
    Get the number of items in a JSON or JSONL file.

    For a JSON file, returns the length of the top-level array. If parsing fails, falls back
    to counting lines as a JSONL file. For a JSONL file, returns the number of lines.

    Args:
        filename (str): The name of the file to count items from.
        ignore_exception (bool, optional): Whether to ignore exceptions and return 0 on error.
            Defaults to True.

    Returns:
        int: The number of items in the file.

    Raises:
        Exception: If `ignore_exception` is False and an error occurs during parsing.
    """

    def __jsonl_num(f, ignore_exception: bool):
        try:
            num = sum(1 for line in f)
        except Exception as e:
            if ignore_exception:
                print(f"File: {filename}\nError: {e}")
                num = 0
            else:
                raise e
        return num

    ext = check_json_file_type(filename)
    with open(filename) as f:
        if ext == "json":
            try:
                dataset = pyjson5.load(f)  # type: ignore
            except Exception:
                num = __jsonl_num(f, ignore_exception)
            else:
                num = len(dataset)
        else:  # jsonl
            num = __jsonl_num(f, ignore_exception)

    return num
