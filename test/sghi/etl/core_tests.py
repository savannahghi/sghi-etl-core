"""Tests for the ``sghi.etl.core.config`` module."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from unittest import TestCase

from typing_extensions import override

from sghi.disposable import not_disposed
from sghi.etl.core import Processor, Sink, Source

# =============================================================================
# TESTS HELPERS
# =============================================================================


@dataclass(slots=True)
class IntsSupplier(Source[Iterable[int]]):
    """A simple :class:`Source` that supplies integers."""

    max_ints: int = field(default=10)
    _is_disposed: bool = field(default=False, init=False)

    @not_disposed
    @override
    def draw(self) -> Iterable[int]:
        yield from range(self.max_ints)

    @property
    @override
    def is_disposed(self) -> bool:
        return self._is_disposed

    @override
    def dispose(self) -> None:
        self._is_disposed = True


@dataclass(slots=True)
class IntsToStrings(Processor[Iterable[int], Iterable[str]]):
    """A :class:`Processor` that takes ints and converts them to strings."""

    _is_disposed: bool = field(default=False, init=False)

    @not_disposed
    @override
    def process(self, raw_data: Iterable[int]) -> Iterable[str]:
        yield from map(str, raw_data)

    @property
    @override
    def is_disposed(self) -> bool:
        return self._is_disposed

    @override
    def dispose(self) -> None:
        self._is_disposed = True


@dataclass(slots=True)
class CollectToList(Sink[Iterable[str]]):
    """A :class:`Sink` that collects all the values it receives in a list."""

    collection_target: list[str] = field()
    _is_disposed: bool = field(default=False, init=False)

    @not_disposed
    @override
    def drain(self, processed_data: Iterable[str]) -> None:
        for value in processed_data:
            self.collection_target.append(value)

    @property
    @override
    def is_disposed(self) -> bool:
        return self._is_disposed

    @override
    def dispose(self) -> None:
        self._is_disposed = True


# =============================================================================
# TESTS
# =============================================================================


class TestSource(TestCase):
    """Tests for the :class:`sghi.etl.core.Source` interface.

    Tests for the default method implementations on the `Source` interface.
    """

    def test_invoking_source_as_a_callable_returns_expected_value(
        self,
    ) -> None:
        """:class:`~sghi.etl.core.Source` should return the expected
        value when invoked as a callable.

        In short, ensure that invoking a ``Source`` instance as a callable
        delegates the actual call to :meth:`~sghi.etl.core.Source.draw`.
        """  # noqa: D202, D205

        instance1: IntsSupplier
        instance2: IntsSupplier
        max_ints: int = 4

        with (
            IntsSupplier(max_ints=max_ints) as instance1,
            IntsSupplier(max_ints=max_ints) as instance2,
        ):
            assert list(instance1.draw()) == list(instance2()) == [0, 1, 2, 3]


class TestProcessor(TestCase):
    """Tests for the :class:`sghi.etl.core.Processor` interface.

    Tests for the default method implementations on the `Processor` interface.
    """

    @override
    def setUp(self) -> None:
        super().setUp()
        self._max_ints: int = 5
        self._source: IntsSupplier = IntsSupplier(max_ints=self._max_ints)

    @override
    def tearDown(self) -> None:
        super().tearDown()
        self._source.dispose()

    def test_invoking_processor_as_a_callable_returns_expected_value(
        self,
    ) -> None:
        """:class:`~sghi.etl.core.Processor` should return the expected
        value when invoked as a callable.

        In short, ensure that invoking a ``Processor`` instance as a callable
        delegates the actual call to
        :meth:`~sghi.etl.core.Processor.process`.
        """  # noqa: D202, D205

        raw_values = tuple(self._source())

        instance1: IntsToStrings
        instance2: IntsToStrings

        with IntsToStrings() as instance1, IntsToStrings() as instance2:
            assert (
                tuple(instance1.process(raw_values))
                == tuple(instance2(raw_values))
                == ("0", "1", "2", "3", "4")
            )


class TestSink(TestCase):
    """Tests for the :class:`sghi.etl.core.Processor` interface.

    Tests for the default method implementations on the `Sink` interface.
    """

    @override
    def setUp(self) -> None:
        super().setUp()
        self._max_ints: int = 5
        self._source: IntsSupplier = IntsSupplier(max_ints=self._max_ints)
        self._processor: IntsToStrings = IntsToStrings()

    @override
    def tearDown(self) -> None:
        super().tearDown()
        self._source.dispose()
        self._processor.dispose()

    def test_invoking_sink_as_a_callable_returns_expected_value(self) -> None:
        """:class:`~sghi.etl.core.Sink` should return the expected value
        when invoked as a callable.

        In short, ensure that invoking a ``Sink`` instance as a callable
        delegates the actual call to :meth:`~sghi.etl.core.Sink.drain`.
        """  # noqa: D202, D205

        processed_data: tuple[str, ...]
        processed_data = tuple(self._processor(self._source()))

        instance1: CollectToList
        instance2: CollectToList

        collect1: list[str] = []
        collect2: list[str] = []

        with (
            CollectToList(collection_target=collect1) as instance1,
            CollectToList(collection_target=collect2) as instance2,
        ):
            instance1.drain(processed_data)
            instance2(processed_data)

            assert collect1 == collect2 == ["0", "1", "2", "3", "4"]
