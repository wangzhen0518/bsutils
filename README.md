# bsutils: Basic Python Utilities

![Downloads](https://img.shields.io/pypi/dm/bsutils.svg?style=flat)

A collection of basic python utilities.

# Installation

```python
# With pip.
pip install bsutils

# Or pipx.
pipx install bsutils

# Or uv
uv pip install bsutils
```

# Features
## Json Utilities (`bsutils.json`)
- `get_item_num`: Get the number of items in a JSON or JSONL file.
- `iter_json_file`: Iterate over a JSON or a JSONL file.
- `load_json_file`: Load a JSON or JSONL file.
- `jsonl_to_json`: Convert a JSONL file to a JSON file.
- `json_to_jsonl`: Convert a JSON file to a JSONL file.
- `write_json_file`: Write a JSON or JSONL file.

## File Utilities (`bsutils.file`)
- `pure_file_name`: Get the pure file name from a path, e.g., "document" for "/path/to/ducumnet.pdf".

## Result (`bsutils.result`)
Use `Result` to get the result of a function rather than exceptions, similar to [result](https://github.com/rustedpy/result).
- `Result`: A class to get the result of a function and handle exceptions.
- `Ok`: Contain the return value when functions success.
- `Err`: Contain the error information when functions fail.

## Option (`bsutils.option`)
Use `Option` to express variable which may not contain value rather than `None` and `Any`.
- `Option`: A class to express variable which may not contain value.
- `Some`: A class to express variable which contains value.
- `None`: Python default None.