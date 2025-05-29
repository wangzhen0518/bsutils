import itertools
from operator import add, mul
from typing import Callable, Generic, Iterable, TypeVar, Collection, Any, Iterator as TypeIterator

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

    def __init__(self, iterable: Iterable[T] | TypeIterator[T]):
        """
        Initializes the Iterator object.

        Args:
            iterable (Iterable[T] | TypeIterator[T]): An iterable or iterator object.

        Raises:
            AssertionError: If the input is not an iterable.
        """
        assert isinstance(iterable, Iterable), "Input must be an iterable"
        self.iter_handler = iter(iterable)
        self.index = 0

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

    def join(self, join_op: Callable[[T, T], T] = add) -> T | None:
        """
        Joins all elements in the iterator using a specified operation.

        Args:
            join_op (Callable[[T, T], T]): A function to combine two elements. Defaults to operator.add.

        Returns:
            T | None: The result of joining all elements. Returns None if the iterator is empty.
        """
        res: T | None = next(self.iter_handler, None)  # type: ignore
        if res is not None:
            while item := next(self.iter_handler, None):
                res = join_op(res, item)
        return res

    def map(self, map_fn: Callable[[T], U]) -> "Iterator[U]":
        """
        Applies a mapping function to each element in the iterator and returns a new Iterator.

        Args:
            map_fn (Callable[[T], U]): A function to transform each element.

        Returns:
            Iterator[U]: A new iterator containing the mapped elements.
        """
        return Iterator(map(map_fn, self.iter_handler))

    def filter(self, filter_fn: Callable[[T], bool]) -> "Iterator[T]":
        """
        Filters elements in the iterator based on a specified condition and returns a new Iterator.

        Args:
            filter_fn (Callable[[T], bool]): A function to determine whether an element should be kept.

        Returns:
            Iterator[T]: A new iterator containing the filtered elements.
        """
        return Iterator(filter(filter_fn, self.iter_handler))

    def copy(self) -> "Iterator[T]":
        """
        Creates a copy of the current iterator and returns a new Iterator.

        Returns:
            Iterator[T]: A new iterator containing the same elements as the original.
        """
        self.iter_handler, new_iter_handler = itertools.tee(self.iter_handler)
        return Iterator(new_iter_handler)


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


if __name__ == "__main__":
    demo()
