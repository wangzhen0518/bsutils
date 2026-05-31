import itertools
from collections.abc import Callable, Collection, Iterable
from collections.abc import Iterator as DefaultIterator
from operator import add, mul
from typing import Any, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")
C = TypeVar("C", bound=Collection[Any])


class Iterator(Generic[T]):
    """
    A generic Iterator class for performing operations on iterable objects.

    This class provides utility methods to collect elements into a container,
    join elements using a specified operation, map elements to new values,
    filter elements based on a condition, and create a copy of the iterator.

    Type Parameters:
        T: The type of elements in the iterator.
    """

    def __init__(self, iterable: Iterable[T] | DefaultIterator[T], catch_exception: bool = False):
        """
        Initializes the Iterator object.

        Args:
            iterable (Iterable[T] | DefaultIterator[T]): An iterable or iterator object.

        Raises:
            AssertionError: If the input is not an iterable.
        """
        assert isinstance(iterable, Iterable), "Input must be an iterable"
        self.iter_handler: DefaultIterator[T] = iter(iterable)
        self.catch_exception = catch_exception

    def __iter__(self):
        """
        Returns self as the iterator object.

        Returns:
            Iterator[T]: self, enabling the iterator protocol.
        """
        return self

    def __next__(self) -> T:
        """
        Returns the next item from the iterator.

        Returns:
            T: The next element.

        Raises:
            StopIteration: If the iterator is exhausted.
        """
        item = self._get_next_item()
        if item is None:
            raise StopIteration
        return item

    def _get_next_item(self) -> T | None:
        """
        Retrieves the next item from the underlying iterator handler.

        If catch_exception is enabled, returns None on any exception instead of propagating it.

        Returns:
            T | None: The next element, or None if the iterator is exhausted or an exception occurred.
        """
        if self.catch_exception:
            try:
                item = next(self.iter_handler, None)
            except Exception:
                return None
        else:
            item = next(self.iter_handler, None)
        return item

    def set_catch_exception(self, catch_exception: bool) -> bool:
        """
        Sets the catch_exception flag and returns the previous value.

        This method swaps the current catch_exception state with the provided value,
        allowing temporary changes that can be reverted later.

        Args:
            catch_exception (bool): The new value for the catch_exception flag.

        Returns:
            bool: The previous catch_exception value.
        """
        catch_exception, self.catch_exception = self.catch_exception, catch_exception
        return catch_exception

    def get_catch_exception(self) -> bool:
        """
        Returns the current catch_exception flag value.

        Returns:
            bool: True if exceptions are caught silently, False otherwise.
        """
        return self.catch_exception

    def collect(self, container_type: Callable[[Iterable[T]], C] = list[T]) -> C:
        """
        Collects elements from the iterator into a specified container type.

        Args:
            container_type (Callable[[Iterable[T]], C]): A function to convert the iterator into a container type.
                Defaults to list.

        Returns:
            C: A container holding all elements from the iterator.
        """
        return container_type(self.iter_handler)

    def join(self, join_op: Callable[[T, T], T] = add, catch_exception: bool | None = None) -> T | None:
        """
        Joins all elements in the iterator using a specified operation.

        Args:
            join_op (Callable[[T, T], T]): A function to combine two elements. Defaults to operator.add.

        Returns:
            T | None: The result of joining all elements. Returns None if the iterator is empty.
        """
        if catch_exception is not None:
            catch_exception = self.set_catch_exception(catch_exception)

        res = self._get_next_item()
        if res is not None:
            while item := self._get_next_item():
                res = join_op(res, item)

        if catch_exception is not None:
            self.set_catch_exception(catch_exception)

        return res

    def map(self, map_fn: Callable[[T], U]) -> "Iterator":
        """
        Applies a mapping function to each element in the iterator and returns self.

        Args:
            map_fn (Callable[[T], U]): A function to transform each element.

        Returns:
            Iterator: self with the mapped iterator handler.
        """
        self.iter_handler = map(map_fn, self.iter_handler)  # type: ignore
        return self

    def filter(self, filter_fn: Callable[[T], bool]) -> "Iterator[T]":
        """
        Filters elements in the iterator based on a specified condition and returns self.

        Args:
            filter_fn (Callable[[T], bool]): A function to determine whether an element should be kept.

        Returns:
            Iterator[T]: self with the filtered iterator handler.
        """
        self.iter_handler = filter(filter_fn, self.iter_handler)  # type: ignore
        return self

    def copy(self) -> "Iterator[T]":
        """
        Creates a copy of the current iterator using itertools.tee.

        The tee operation splits the iterator into two, allowing independent iteration.
        Note that tee may need to buffer items if the two copies are advanced at
        different rates. After calling this method, the original iterator still works
        but both share underlying state until fully consumed.

        Returns:
            Iterator[T]: A new iterator containing the same remaining elements.
        """
        self.iter_handler, new_iter_handler = itertools.tee(self.iter_handler)
        return Iterator(new_iter_handler, self.catch_exception)

    def skip(self, n: int) -> "Iterator[T]":
        """
        Skip the first n elements in place and returns self.

        Args:
            n (int): The number of elements to skip. If n is less than or equal to 0, no elements are skipped.

        Returns:
            Iterator[T]: self with the first n elements skipped.
        """
        if n > 0:
            self.iter_handler = itertools.islice(self.iter_handler, n, None)  # type: ignore
        return self

    def take(self, n: int) -> "Iterator[T]":
        """
        Take only the first n elements in place and returns self.

        Args:
            n (int): The number of elements to take.

        Returns:
            Iterator[T]: self with only the first n elements remaining.
        """
        if n > 0:
            self.iter_handler = itertools.islice(self.iter_handler, n)  # type: ignore
        return self

    def count(self) -> int:
        """
        Counts the number of elements in the iterator.

        Returns:
            int: The total number of elements in the iterator.

        Note:
            This operation consumes the iterator. After calling this method,
            the iterator will be exhausted and cannot be used again.
        """
        return sum(1 for _ in self.iter_handler)


def demo():
    """
    Demonstrates the usage of the Iterator class.
    """
    it = Iterator(range(1, 10))
    print("List Collect:", it.copy().collect())
    print("Set Collect:", it.copy().collect(set))
    print("Add Join:", it.copy().join())
    print("Mul Join:", it.copy().join(mul))
    print("Map:", it.copy().map(lambda x: x * x).collect())
    print("Filter:", it.copy().filter(lambda x: x % 2 == 0).collect())
    print("Map & Filter:", it.copy().map(lambda x: x * x).filter(lambda x: x % 2 == 0).collect())
    print("Skip 3:", it.copy().skip(3).collect())
    print("Take 3:", it.copy().take(3).collect())
    print("Skip 2 & Take 3:", it.copy().skip(2).take(3).collect())

    for item in it.copy():
        print(item)


if __name__ == "__main__":
    demo()
