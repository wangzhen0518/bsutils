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
## Json Utilities
- `get_item_num`: Get the number of items in a JSON or JSONL file.
- `iter_json_file`: Iterate over a JSON or a JSONL file.
- `load_json_file`: Load a JSON or JSONL file.
- `jsonl_to_json`: Convert a JSONL file to a JSON file.
- `json_to_jsonl`: Convert a JSON file to a JSONL file.
- `write_json_file`: Write a JSON or JSONL file.

## File Utilities
- `pure_file_name`: Get the pure file name from a path, e.g., "document" for "/path/to/ducumnet.pdf".