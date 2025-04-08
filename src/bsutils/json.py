import enum
import json
import os
from typing import Callable, Generator, Iterable, Literal, Optional

import pyjson5

from .file import pure_file_name


class JsonType(enum.Enum):
    """
    Represents valid JSON file types.

    Values:
        Json (str): "json" extension.
        Jsonl (str): "jsonl" (JSON Lines) extension.
    """

    Json = "json"
    Jsonl = "jsonl"


def check_json_file_type(filename: str) -> JsonType:
    """
    Checks if a filename has a valid JSON or JSONL extension.

    Args:
        filename (str): Input filename (e.g., "data.json").

    Returns:
        JsonType: Enum member (JsonType.Json or JsonType.Jsonl).

    Raises:
        ValueError: If the extension is not "json" or "jsonl".

    Example:
        >>> check_json_file_type("data.json")
        <JsonType.Json: 'json'>
        >>> check_json_file_type("invalid.txt")
        ValueError: Unknown file type .txt: invalid.txt
    """
    ext = filename.split(".")[-1]
    if ext not in {"json", "jsonl"}:
        raise ValueError(f"Unknown file type .{ext}: {filename}")
    else:
        return JsonType(ext)


def iter_json_file(filename: str, ignore_exception: bool = True) -> Generator[dict, None, None]:
    """
    Iterates over items in a JSON/JSONL file, yielding one dictionary at a time.

    Args:
        filename (str): File to read.
        ignore_exception (bool, optional): Skip errors if True. Defaults to True.

    Yields:
        dict: Parsed JSON object from each line (JSONL) or array element (JSON).

    Raises:
        ValueError: Invalid file extension or non-list JSON content (if ignore_exception=False).

    Example:
        >>> for item in iter_json_file("data.jsonl"):
        ...     print(item)
        {"id": 1, "name": "Alice"}
        {"id": 2, "name": "Bob"}
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
    Counts items in a JSON/JSONL file.

    Args:
        filename (str): File to count items from.
        ignore_exception (bool, optional): Return 0 on error if True. Defaults to True.

    Returns:
        int: Number of items (JSON array length or JSONL line count).

    Raises:
        Exception: If parsing fails and ignore_exception=False.

    Example:
        >>> get_item_num("data.json")
        100
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
        if ext is JsonType.Json:
            try:
                dataset = pyjson5.load(f)  # type: ignore
            except Exception:
                f.seek(0)
                num = __jsonl_num(f, ignore_exception)
            else:
                num = len(dataset)
        else:  # jsonl
            num = __jsonl_num(f, ignore_exception)

    return num


def load_json_file(filename: str, ignore_exception: bool = True, sort: bool = False, sort_key: Optional[Callable] = None):
    """Load and parse JSON or JSONL file with optional sorting and error handling.

    Args:
        filename (str): Path to the JSON or JSONL file to be loaded.
        ignore_exception (bool): If True, skips malformed lines in JSONL files and continues parsing.
                                 If False, raises exceptions when encountering parsing errors.
                                 Defaults to True.
        sort (bool): If True, sorts the loaded content using the provided sort_key.
              Requires sort_key to be specified. Defaults to False.
        sort_key (Callable): A callable function to be used as the key for sorting when sort=True.
                             Must be provided if sort=True. Defaults to None.

    Returns:
        list: Parsed data (JSON array or aggregated JSONL lines).

    Raises:
        ValueError: If sort=True but sort_key is None.
        Exception: Various JSON parsing errors if ignore_exception=False.
        FileNotFoundError: If the specified file doesn't exist.

    Notes:
        - The function automatically detects whether the input is JSON or JSONL format.
        - For JSONL files, line numbers are reported when errors occur (if ignore_exception=True).
        - Uses pyjson5 for parsing, which supports extended JSON syntax including comments.
        - When sorting, the original list is replaced with a new sorted list.

    Examples:
        >>> # Load a JSON file, ignoring any parsing errors
        >>> data = load_json_file('data.json')

        >>> # Load and sort a JSONL file
        >>> data = load_json_file('data.jsonl', sort=True, sort_key=lambda x: x['id'])
    """

    def __load_jsonl(f, ignore_exception: bool):
        all_content = []
        for line_id, line in enumerate(f):
            try:
                content = pyjson5.loads(line)
            except Exception as e:
                if ignore_exception:
                    print(f"File: {filename}\nError in line {line_id}: {e}\nContent:{line}")
                    continue
                else:
                    raise e
            all_content.append(content)
        return all_content

    ext = check_json_file_type(filename)
    with open(filename) as f:
        if ext is JsonType.Json:
            try:
                all_content = pyjson5.load(f)  # type: ignore
            except Exception:
                f.seek(0)
                all_content = __load_jsonl(f, ignore_exception)
        else:  # jsonl
            all_content = __load_jsonl(f, ignore_exception)

    if sort:
        if sort_key is None:
            raise ValueError("Using sort but sort_key is None.")
        all_content = sorted(all_content, key=sort_key)

    return all_content


def write_json_file(
    data: Iterable,
    filename: str,
    transfrom: Optional[Callable] = None,
    sort: bool = False,
    sort_key: Optional[Callable] = None,
    write_type: Optional[Literal["json", "jsonl"]] = None,
):
    """
    Writes data to a JSON/JSONL file with optional transformations and sorting.

    Args:
        data (Iterable): Data to write (e.g., list of dicts).
        filename (str): Output file path.
        transfrom (Callable, optional): Function to modify items before writing.
        sort (bool): Sort data before writing. Defaults to False.
        sort_key (Callable): Key function for sorting (required if sort=True).
        write_type (str, optional): Override output format ("json" or "jsonl").

    Raises:
        ValueError: If sort=True without sort_key or data is not iterable.

    Note:
        Creates parent directories if they don't exist.
        For JSON format, uses pretty printing (indent=4).
        For JSONL format, writes one JSON object per line.

    Example:
        >>> write_json_file(
        ...     data=[{"id": 2}, {"id": 1}],
        ...     filename="sorted.json",
        ...     sort=True,
        ...     sort_key=lambda x: x["id"]
        ... )
    """
    if transfrom is not None:
        data = [transfrom(item) for item in data]

    if sort:
        if sort_key is not None:
            if not isinstance(data, Iterable):
                raise ValueError(f"data must be iterable when using sort, but now its type is {type(data)}")
            data = sorted(data, key=sort_key)
        else:
            raise ValueError("Using sort but sort_key is None.")

    if write_type is None:
        ext = check_json_file_type(filename)
    else:
        ext = JsonType(write_type)

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if ext is JsonType.Json:
        with open(filename, "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        with open(filename, "w", encoding="utf8") as f:
            for item in data:
                json.dump(item, f, ensure_ascii=False)
                f.write("\n")


def json_to_jsonl(src_file: str, tgt_file: Optional[str]):
    """Convert JSON file to JSONL format.

    Args:
        src_file (str): Source JSON file path.
        tgt_file (str, optional): Target JSONL path. If None, uses the same directory as src_file with .jsonl extension.


    Note:
        Uses load_json_file and write_json_file internally.
        Preserves all data content during conversion.

    Example:
        >>> json_to_jsonl("input.json", "output.jsonl")
    """

    content = load_json_file(src_file)
    if tgt_file is None:
        tgt_file = os.path.join(os.path.dirname(src_file), pure_file_name(src_file) + ".jsonl")
    write_json_file(content, tgt_file, write_type="jsonl")


def jsonl_to_json(src_file: str, tgt_file: Optional[str]):
    """Convert JSONL file to JSON format.

    Args:
        src_file (str): Source JSONL file path.
        tgt_file (str, optional): Target JSON path. If None, uses the same directory as src_file with .json extension.


    Note:
        Uses load_json_file and write_json_file internally.
        Preserves all data content during conversion.

    Example:
        >>> jsonl_to_json("input.jsonl", "output.json")
    """

    content = load_json_file(src_file)
    if tgt_file is None:
        tgt_file = os.path.join(os.path.dirname(src_file), pure_file_name(src_file) + ".json")
    write_json_file(content, tgt_file, write_type="json")
