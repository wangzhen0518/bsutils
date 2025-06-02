# bsutils: Basic Python Utilities

![Downloads](https://img.shields.io/pypi/dm/bsutils.svg?style=flat)

A collection of basic Python utilities designed to simplify common tasks.

# Installation

```bash
# Install using pip.
pip install bsutils

# Install using pipx.
pipx install bsutils

# Install using uv.
uv pip install bsutils
```

# Features

## Json Utilities (`bsutils.json`)

Utilities for working with JSON and JSONL files.

### Features:

-   `get_item_num`: Get the number of items in a JSON or JSONL file.
-   `iter_json_file`: Iterate over a JSON or a JSONL file.
-   `load_json_file`: Load a JSON or JSONL file.
-   `jsonl_to_json`: Convert a JSONL file to a JSON file.
-   `json_to_jsonl`: Convert a JSON file to a JSONL file.
-   `write_json_file`: Write a JSON or JSONL file.

### Example Usage:

```python
from bsutils.json import load_json_file

data = load_json_file("example.json")
print(data)

for item in iter_json_file("example.jsonl"):
    print(item)
```

---

## File Utilities (`bsutils.file`)

Utilities for working with file paths.

### Features:

-   `pure_file_name`: Get the pure file name from a path, e.g., "document" for "/path/to/document.pdf".

### Example Usage:

```python
from bsutils.file import pure_file_name

file_name = pure_file_name("/path/to/document.pdf")
print(file_name)  # Output: "document"
```

---

## Result (`bsutils.result`)

Use `Result` to handle function results without raising exceptions, inspired by [result](https://github.com/rustedpy/result).

### Features:

-   `Result`: A class to encapsulate the result of a function and handle exceptions.
-   `Ok`: Represents a successful function result.
-   `Err`: Represents an error or exception.

### Example Usage:

```python
from bsutils.result import Result, Ok, Err

def divide(a, b):
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

result = divide(10, 2)
if result.is_ok():
    print("Success:", result.value)
elif result.is_err():
    print("Error:", result.error)
```

---

## Option (`bsutils.option`)

Use `Option` to represent variables that may or may not contain values, avoiding `None` and `Any`.

### Features:

-   `Option`: A class to represent optional values.
-   `Some`: Represents a variable that contains a value.
-   `None`: Represents the absence of a value.

### Example Usage:

```python
from bsutils.option import Option, Some, Null

value = Some(42)
if value.is_some():
    print("Value exists:", value.value)
else:
    print("No value")

null_value = Null()
print(null_value.is_null())  # Output: True
```

---

## Iterator (`bsutils.iterator`)

A generic `Iterator` class for performing operations on iterable objects.

### Features:

-   `collect`: Collect elements from the iterator into a specified container type (e.g., `list`, `set`).
-   `join`: Join all elements in the iterator using a specified operation (e.g., addition, multiplication).
-   `map`: Apply a mapping function to each element in the iterator and return a new iterator.
-   `filter`: Filter elements in the iterator based on a specified condition and return a new iterator.
-   `copy`: Create a copy of the current iterator.

### Example Usage:

```python
from bsutils.iterator import Iterator

it = Iterator(range(1, 10))
print("List Collect:", it.copy().collect())  # Collect elements into a list
print("Set Collect:", it.copy().collect(set))  # Collect elements into a set
print("Add Join:", it.copy().join())  # Join elements using addition
print("Mul Join:", it.copy().join(mul))  # Join elements using multiplication
print("Map:", it.copy().map(lambda x: x * x).collect())  # Map elements to their squares
print("Filter:", it.copy().filter(lambda x: x % 2 == 0).collect())  # Filter even numbers
```

---

## IO (`bsutils.io`)

The IO module provides utilities for capturing standard output (stdout) and standard error (stderr) using the OutputCatcher class.

### Features:

-   `OutputCatcher`: A context manager for capturing stdout and stderr.
-   `write(data)`: Writes data to the stdout buffer.
-   `get_stdout()`: Retrieves the captured stdout as a string.
-   `get_stderr()`: Retrieves the captured stderr as a string.

### Example Usage:

```python
from bsutils.io import OutputCapturer

with OutputCapturer() as capturer:
    print("Hello world!")
    print("This goes to stdout")
    import sys
    sys.stderr.write("This goes to stderr\n")

# Get the captured stdout
output = capturer.get_stdout()
print("Captured output:")
print(output)

# Get the captured stderr
error = capturer.get_stderr()
print("Captured error:")
print(error)
```
