import sys
from io import StringIO


class OutputCapturer:
    """
    A context manager for capturing standard output (stdout) and standard error (stderr).

    Attributes:
        catch_stdout (bool): Whether to capture stdout. Defaults to True.
        catch_stderr (bool): Whether to capture stderr. Defaults to True.
        stdout_buffer (StringIO): Buffer to store captured stdout.
        stderr_buffer (StringIO): Buffer to store captured stderr.
        old_stdout (file-like object): Original stdout before redirection.
        old_stderr (file-like object): Original stderr before redirection.

    Methods:
        write(data): Writes data to the stdout buffer.
        get_stdout(): Retrieves the captured stdout as a string.
        get_stderr(): Retrieves the captured stderr as a string.
        __enter__(): Sets up the redirection of stdout and stderr.
        __exit__(): Restores the original stdout and stderr.
    """

    def __init__(self, catch_stdout: bool = True, catch_stderr: bool = True):
        """
        Initializes the OutputCatcher instance.

        Args:
            catch_stdout (bool): Whether to capture stdout. Defaults to True.
            catch_stderr (bool): Whether to capture stderr. Defaults to True.
        """
        self.stdout_buffer = StringIO()
        self.stderr_buffer = StringIO()
        self.old_stdout = None
        self.old_stderr = None
        self.catch_stdout = catch_stdout
        self.catch_stderr = catch_stderr

    def write(self, data):
        """
        Writes data to the stdout buffer.

        Args:
            data (str): The data to write to the buffer.
        """
        self.stdout_buffer.write(data)

    def get_stdout(self):
        """
        Retrieves the captured stdout as a string.

        Returns:
            str: The captured stdout.
        """
        return self.stdout_buffer.getvalue()

    def get_stderr(self):
        """
        Retrieves the captured stderr as a string.

        Returns:
            str: The captured stderr.
        """
        return self.stderr_buffer.getvalue()

    def __enter__(self):
        """
        Sets up the redirection of stdout and stderr.

        Returns:
            OutputCatcher: The current instance of OutputCatcher.
        """
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        if self.catch_stdout:
            sys.stdout = self.stdout_buffer
        if self.catch_stderr:
            sys.stderr = self.stderr_buffer
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Restores the original stdout and stderr.

        Args:
            exc_type: Exception type, if any.
            exc_val: Exception value, if any.
            exc_tb: Exception traceback, if any.

        Returns:
            bool: False to propagate exceptions, if any.
        """
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        return False


def demo():
    """
    Demonstrates the usage of the OutputCatcher class.

    Captures stdout and stderr, prints the captured output and error messages.
    """
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


if __name__ == "__main__":
    demo()
