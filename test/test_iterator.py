"""Unit tests for bsutils.iterator."""

import unittest
from operator import mul

from bsutils.iterator import Iterator


class TestIteratorInit(unittest.TestCase):
    """Tests for Iterator initialization."""

    def test_init_with_list(self):
        it = Iterator([1, 2, 3])
        self.assertIsNotNone(it)

    def test_init_with_range(self):
        it = Iterator(range(10))
        self.assertIsNotNone(it)

    def test_init_with_generator(self):
        def gen():
            yield 1
            yield 2

        it = Iterator(gen())
        self.assertIsNotNone(it)

    def test_init_with_tuple(self):
        it = Iterator((1, 2, 3))
        self.assertIsNotNone(it)

    def test_init_with_set(self):
        it = Iterator({1, 2, 3})
        self.assertIsNotNone(it)

    def test_init_with_string(self):
        it = Iterator("hello")
        self.assertIsNotNone(it)

    def test_init_with_non_iterable_raises(self):
        with self.assertRaises(AssertionError):
            Iterator(42)  # type: ignore

    def test_init_catch_exception_default(self):
        it = Iterator([1, 2, 3])
        self.assertFalse(it.get_catch_exception())

    def test_init_catch_exception_true(self):
        it = Iterator([1, 2, 3], catch_exception=True)
        self.assertTrue(it.get_catch_exception())


class TestIteratorProtocol(unittest.TestCase):
    """Tests for __iter__ and __next__."""

    def test_iter_returns_self(self):
        it = Iterator([1, 2, 3])
        self.assertIs(iter(it), it)

    def test_next_returns_elements(self):
        it = Iterator([1, 2, 3])
        self.assertEqual(next(it), 1)
        self.assertEqual(next(it), 2)
        self.assertEqual(next(it), 3)

    def test_next_raises_stop_iteration(self):
        it = Iterator([1])
        next(it)
        with self.assertRaises(StopIteration):
            next(it)

    def test_next_empty_iterator(self):
        it = Iterator([])
        with self.assertRaises(StopIteration):
            next(it)

    def test_for_loop(self):
        it = Iterator([1, 2, 3])
        result = []
        for item in it:
            result.append(item)
        self.assertEqual(result, [1, 2, 3])

    def test_for_loop_empty(self):
        it = Iterator([])
        result = []
        for item in it:
            result.append(item)
        self.assertEqual(result, [])


class TestCollect(unittest.TestCase):
    """Tests for collect()."""

    def test_collect_list_default(self):
        it = Iterator(range(5))
        self.assertEqual(it.collect(), [0, 1, 2, 3, 4])

    def test_collect_set(self):
        it = Iterator([1, 2, 2, 3, 3, 3])
        self.assertEqual(it.collect(set), {1, 2, 3})

    def test_collect_tuple(self):
        it = Iterator([1, 2, 3])
        self.assertEqual(it.collect(tuple), (1, 2, 3))

    def test_collect_empty(self):
        it = Iterator([])
        self.assertEqual(it.collect(), [])

    def test_collect_after_consumed(self):
        it = Iterator([1, 2])
        next(it)
        next(it)
        self.assertEqual(it.collect(), [])


class TestJoin(unittest.TestCase):
    """Tests for join()."""

    def test_join_add_default(self):
        it = Iterator([1, 2, 3, 4])
        self.assertEqual(it.join(), 10)

    def test_join_mul(self):
        it = Iterator([1, 2, 3, 4])
        self.assertEqual(it.join(mul), 24)

    def test_join_strings(self):
        it = Iterator(["a", "b", "c"])
        self.assertEqual(it.join(), "abc")

    def test_join_empty_returns_none(self):
        it = Iterator([])
        self.assertIsNone(it.join())

    def test_join_single_element(self):
        it = Iterator([42])
        self.assertEqual(it.join(), 42)

    def test_join_consumes_iterator(self):
        it = Iterator([1, 2, 3])
        it.join()
        self.assertEqual(it.collect(), [])


class TestMap(unittest.TestCase):
    """Tests for map()."""

    def test_map_square(self):
        it = Iterator(range(5))
        result = it.map(lambda x: x * x).collect()
        self.assertEqual(result, [0, 1, 4, 9, 16])

    def test_map_string(self):
        it = Iterator([1, 2, 3])
        result = it.map(str).collect()
        self.assertEqual(result, ["1", "2", "3"])

    def test_map_returns_self(self):
        it = Iterator([1, 2, 3])
        returned = it.map(lambda x: x * 2)
        self.assertIs(returned, it)

    def test_map_empty(self):
        it = Iterator([])
        result = it.map(lambda x: x * 2).collect()
        self.assertEqual(result, [])

    def test_map_then_join(self):
        it = Iterator([1, 2, 3])
        result = it.map(lambda x: x * 10).join()
        self.assertEqual(result, 60)


class TestFilter(unittest.TestCase):
    """Tests for filter()."""

    def test_filter_even(self):
        it = Iterator(range(10))
        result = it.filter(lambda x: x % 2 == 0).collect()
        self.assertEqual(result, [0, 2, 4, 6, 8])

    def test_filter_greater_than(self):
        it = Iterator([1, 5, 2, 8, 3])
        result = it.filter(lambda x: x > 3).collect()
        self.assertEqual(result, [5, 8])

    def test_filter_returns_self(self):
        it = Iterator([1, 2, 3])
        returned = it.filter(lambda x: True)
        self.assertIs(returned, it)

    def test_filter_all_false(self):
        it = Iterator([1, 2, 3])
        result = it.filter(lambda x: x > 10).collect()
        self.assertEqual(result, [])

    def test_filter_all_true(self):
        it = Iterator([1, 2, 3])
        result = it.filter(lambda x: x > 0).collect()
        self.assertEqual(result, [1, 2, 3])

    def test_filter_empty(self):
        it = Iterator([])
        result = it.filter(lambda x: x % 2 == 0).collect()
        self.assertEqual(result, [])

    def test_map_then_filter(self):
        it = Iterator(range(10))
        result = it.map(lambda x: x * x).filter(lambda x: x % 2 == 0).collect()
        self.assertEqual(result, [0, 4, 16, 36, 64])

    def test_filter_then_map(self):
        it = Iterator(range(10))
        result = it.filter(lambda x: x % 2 == 0).map(lambda x: x * 10).collect()
        self.assertEqual(result, [0, 20, 40, 60, 80])


class TestCopy(unittest.TestCase):
    """Tests for copy()."""

    def test_copy_returns_new_iterator(self):
        it = Iterator([1, 2, 3])
        copy_it = it.copy()
        self.assertIsNot(copy_it, it)

    def test_copy_independent_iteration(self):
        it = Iterator([1, 2, 3, 4, 5])
        copy_it = it.copy()
        self.assertEqual(next(it), 1)
        self.assertEqual(next(it), 2)
        self.assertEqual(next(copy_it), 1)  # copy starts from beginning
        self.assertEqual(next(it), 3)

    def test_copy_catch_exception_propagated(self):
        it = Iterator([1, 2, 3], catch_exception=True)
        copy_it = it.copy()
        self.assertTrue(copy_it.get_catch_exception())

    def test_copy_empty(self):
        it = Iterator([])
        copy_it = it.copy()
        self.assertEqual(copy_it.collect(), [])

    def test_copy_then_collect_match(self):
        it = Iterator(range(5))
        copy_it = it.copy()
        self.assertEqual(it.collect(), copy_it.collect())


class TestSkip(unittest.TestCase):
    """Tests for skip()."""

    def test_skip_two(self):
        it = Iterator([1, 2, 3, 4, 5])
        result = it.skip(2).collect()
        self.assertEqual(result, [3, 4, 5])

    def test_skip_zero(self):
        it = Iterator([1, 2, 3])
        result = it.skip(0).collect()
        self.assertEqual(result, [1, 2, 3])

    def test_skip_all(self):
        it = Iterator([1, 2, 3])
        result = it.skip(3).collect()
        self.assertEqual(result, [])

    def test_skip_more_than_length(self):
        it = Iterator([1, 2, 3])
        result = it.skip(10).collect()
        self.assertEqual(result, [])

    def test_skip_returns_self(self):
        it = Iterator([1, 2, 3])
        returned = it.skip(1)
        self.assertIs(returned, it)

    def test_skip_empty(self):
        it = Iterator([])
        result = it.skip(5).collect()
        self.assertEqual(result, [])

    def test_skip_then_take(self):
        it = Iterator([1, 2, 3, 4, 5])
        result = it.skip(1).take(3).collect()
        self.assertEqual(result, [2, 3, 4])


class TestTake(unittest.TestCase):
    """Tests for take()."""

    def test_take_three(self):
        it = Iterator([1, 2, 3, 4, 5])
        result = it.take(3).collect()
        self.assertEqual(result, [1, 2, 3])

    def test_take_zero(self):
        it = Iterator([1, 2, 3])
        result = it.take(0).collect()
        self.assertEqual(result, [1, 2, 3])

    def test_take_all(self):
        it = Iterator([1, 2, 3])
        result = it.take(3).collect()
        self.assertEqual(result, [1, 2, 3])

    def test_take_more_than_length(self):
        it = Iterator([1, 2, 3])
        result = it.take(10).collect()
        self.assertEqual(result, [1, 2, 3])

    def test_take_returns_self(self):
        it = Iterator([1, 2, 3])
        returned = it.take(2)
        self.assertIs(returned, it)

    def test_take_empty(self):
        it = Iterator([])
        result = it.take(5).collect()
        self.assertEqual(result, [])

    def test_take_then_skip(self):
        it = Iterator([1, 2, 3, 4, 5])
        result = it.take(4).skip(1).collect()
        self.assertEqual(result, [2, 3, 4])


class TestCount(unittest.TestCase):
    """Tests for count()."""

    def test_count_positive(self):
        it = Iterator([1, 2, 3, 4, 5])
        self.assertEqual(it.count(), 5)

    def test_count_empty(self):
        it = Iterator([])
        self.assertEqual(it.count(), 0)

    def test_count_consumes_iterator(self):
        it = Iterator([1, 2, 3])
        it.count()
        self.assertEqual(it.collect(), [])

    def test_count_after_map(self):
        it = Iterator(range(10))
        self.assertEqual(it.map(lambda x: x * 2).count(), 10)


class TestCatchException(unittest.TestCase):
    """Tests for catch_exception feature."""

    def test_catch_exception_default_false(self):
        it = Iterator([1, 2, 3])
        self.assertFalse(it.get_catch_exception())

    def test_set_catch_exception_returns_old(self):
        it = Iterator([1, 2, 3], catch_exception=False)
        old = it.set_catch_exception(True)
        self.assertFalse(old)
        self.assertTrue(it.get_catch_exception())

    def test_set_catch_exception_roundtrip(self):
        it = Iterator([1, 2, 3])
        it.set_catch_exception(True)
        old = it.set_catch_exception(False)
        self.assertTrue(old)
        self.assertFalse(it.get_catch_exception())

    def test_join_with_catch_exception_true(self):
        def broken_iter():
            yield 1
            raise RuntimeError("oops")
            yield 2

        it = Iterator(broken_iter(), catch_exception=True)
        result = it.join()
        self.assertEqual(result, 1)

    def test_join_temporary_catch_exception(self):
        def broken_iter():
            yield 1
            yield 2
            raise RuntimeError("oops")

        it = Iterator(broken_iter(), catch_exception=False)
        result = it.join(catch_exception=True)
        self.assertEqual(result, 3)
        self.assertFalse(it.get_catch_exception())  # restored


class TestChaining(unittest.TestCase):
    """Tests for method chaining."""

    def test_map_filter_chain(self):
        it = Iterator(range(10))
        result = it.map(lambda x: x * 2).filter(lambda x: x > 5).skip(1).take(3).collect()
        self.assertEqual(result, [8, 10, 12])

    def test_filter_map_chain(self):
        it = Iterator([1, 2, 3, 4, 5])
        result = it.filter(lambda x: x % 2 == 0).map(str).collect()
        self.assertEqual(result, ["2", "4"])

    def test_skip_take_chain(self):
        it = Iterator([1, 2, 3, 4, 5, 6, 7, 8, 9])
        result = it.skip(2).take(4).skip(1).take(2).collect()
        # skip 2 -> [3,4,5,6,7,8,9], take 4 -> [3,4,5,6], skip 1 -> [4,5,6], take 2 -> [4,5]
        self.assertEqual(result, [4, 5])

    def test_copy_after_chaining(self):
        it = Iterator(range(5))
        mapped = it.map(lambda x: x * 10)
        copy_it = mapped.copy()
        self.assertEqual(mapped.collect(), copy_it.collect())


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases."""

    def test_empty_iterator_all_ops(self):
        it = Iterator([])
        self.assertEqual(it.collect(), [])
        self.assertIsNone(it.join())
        self.assertEqual(it.map(lambda x: x).collect(), [])
        self.assertEqual(it.filter(lambda x: True).collect(), [])
        self.assertEqual(it.skip(1).collect(), [])
        self.assertEqual(it.take(1).collect(), [])
        self.assertEqual(it.count(), 0)

    def test_single_element(self):
        it = Iterator([42])
        self.assertEqual(it.copy().collect(), [42])
        self.assertEqual(it.copy().join(), 42)
        self.assertEqual(it.copy().map(lambda x: x * 2).collect(), [84])
        self.assertEqual(it.copy().skip(0).collect(), [42])
        self.assertEqual(it.copy().skip(1).collect(), [])
        self.assertEqual(it.copy().take(1).collect(), [42])

    def test_generator_exhaustion(self):
        def gen():
            for i in range(3):
                yield i

        it = Iterator(gen())
        self.assertEqual(it.collect(), [0, 1, 2])
        self.assertEqual(it.collect(), [])  # already exhausted

    def test_string_elements(self):
        it = Iterator(["hello", "world"])
        result = it.map(str.upper).collect()
        self.assertEqual(result, ["HELLO", "WORLD"])

    def test_mixed_negative_n(self):
        it = Iterator([1, 2, 3, 4, 5])
        result = it.skip(-1).collect()
        self.assertEqual(result, [1, 2, 3, 4, 5])

        it2 = Iterator([1, 2, 3])
        result2 = it2.take(-1).collect()
        self.assertEqual(result2, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
