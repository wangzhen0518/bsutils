import os
import sys
import threading
import time
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

    def __init__(self, catch_stdout=True, catch_stderr=True):
        """
        Initializes the OutputCatcher instance.

        Args:
            catch_stdout (bool): Whether to capture stdout. Defaults to True.
            catch_stderr (bool): Whether to capture stderr. Defaults to True.
        """
        self.catch_stdout = catch_stdout
        self.catch_stderr = catch_stderr

        self.fd_stdout = StringIO()
        self.fd_stderr = StringIO()

        self.old_fd_stdout = -1
        self.old_fd_stderr = -1

        self.stdout_r, self.stdout_w = -1, -1
        self.stderr_r, self.stderr_w = -1, -1
        self.stdout_thread = None
        self.stderr_thread = None
        self.stop_threads = False

    def _fd_reader(self, fd, buffer):
        """从文件描述符读取数据的线程函数"""
        while not self.stop_threads:
            try:
                data = os.read(fd, 4096)
                if not data:  # EOF
                    break
                buffer.write(data.decode(errors="replace"))
            except (BlockingIOError, OSError):
                time.sleep(0.1)

    def __enter__(self):
        """
        Sets up the redirection of stdout and stderr.

        Returns:
            OutputCatcher: The current instance of OutputCatcher.
        """
        self.old_fd_stdout = os.dup(sys.stdout.fileno())
        self.old_fd_stderr = os.dup(sys.stderr.fileno())
        self.stop_threads = False

        if self.catch_stdout:
            self.stdout_r, self.stdout_w = os.pipe()
            os.dup2(self.stdout_w, sys.stdout.fileno())

            self.stdout_thread = threading.Thread(target=self._fd_reader, args=(self.stdout_r, self.fd_stdout))
            self.stdout_thread.daemon = True
            self.stdout_thread.start()

        if self.catch_stderr:
            self.stderr_r, self.stderr_w = os.pipe()
            os.dup2(self.stderr_w, sys.stderr.fileno())

            self.stderr_thread = threading.Thread(target=self._fd_reader, args=(self.stderr_r, self.fd_stderr))
            self.stderr_thread.daemon = True
            self.stderr_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Restores the original stdout and stderr.

        Args:
            exc_type: Exception type, if any.
            exc_val: Exception value, if any.
            exc_tb: Exception traceback, if any.

        Returns:
            bool: False to propagate exceptions, if any.
        """

        self.stop_threads = True

        if self.catch_stdout:
            os.close(self.stdout_w)
        if self.catch_stderr:
            os.close(self.stderr_w)

        if self.stdout_thread:
            self.stdout_thread.join(timeout=0.1)
        if self.stderr_thread:
            self.stderr_thread.join(timeout=0.1)

        if self.catch_stdout:
            os.close(self.stdout_r)
        if self.catch_stderr:
            os.close(self.stderr_r)

        os.dup2(self.old_fd_stdout, sys.stdout.fileno())
        os.dup2(self.old_fd_stderr, sys.stderr.fileno())

        os.close(self.old_fd_stdout)
        os.close(self.old_fd_stderr)

        return False

    def get_stdout(self):
        """
        Retrieves the captured stdout as a string.

        Returns:
            str: The captured stdout.
        """
        fd_out = self.fd_stdout.getvalue()
        return fd_out

    def get_stderr(self):
        """
        Retrieves the captured stderr as a string.

        Returns:
            str: The captured stderr.
        """
        fd_err = self.fd_stderr.getvalue()
        return fd_err


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
