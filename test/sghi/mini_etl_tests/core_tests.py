"""Tests for the ``sghi.miniETL.core.config`` module."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from unittest import TestCase

from typing_extensions import override

from sghi.disposable import not_disposed
from sghi.miniETL.core import Processor, Sink, Source

# =============================================================================
# TESTS HELPERS
# =============================================================================


@dataclass(slots=True)
class IntsSupplier(Source):
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
    """Tests for the :class:`sghi.miniETL.core.Source` interface."""

    @override
    def setUp(self) -> None:
        super().setUp()
        self._max_ints: int = 5
        self._instance: IntsSupplier = IntsSupplier(max_ints=self._max_ints)

    @override
    def tearDown(self) -> None:
        super().tearDown()
        self._instance.dispose()

    def test_invoking_source_as_a_callable_returns_expected_value(
        self,
    ) -> None:
        """:class:`~sghi.miniETL.core.Source` should return the expected
        value when invoked as a callable.

        In short, ensure that invoking a ``Source`` instance as a callable
        delegates the actual call to :meth:`~sghi.miniETL.core.Source.draw`.
        """  # noqa: D202, D205

        assert tuple(self._instance()) == (0, 1, 2, 3, 4)


class TestProcessor(TestCase):
    """Tests for the :class:`sghi.miniETL.core.Processor` interface."""

    @override
    def setUp(self) -> None:
        super().setUp()
        self._max_ints: int = 5
        self._source: IntsSupplier = IntsSupplier(max_ints=self._max_ints)
        self._instance: IntsToStrings = IntsToStrings()

    @override
    def tearDown(self) -> None:
        super().tearDown()
        self._source.dispose()
        self._instance.dispose()

    def test_invoking_processor_as_a_callable_returns_expected_value(
        self,
    ) -> None:
        """:class:`~sghi.miniETL.core.Processor` should return the expected
        value when invoked as a callable.

        In short, ensure that invoking a ``Processor`` instance as a callable
        delegates the actual call to
        :meth:`~sghi.miniETL.core.Processor.process`.
        """  # noqa: D202, D205

        raw_values = self._source()
        assert tuple(self._instance(raw_values)) == ("0", "1", "2", "3", "4")


class TestSink(TestCase):
    """Tests for the :class:`sghi.miniETL.core.Processor` interface."""

    @override
    def setUp(self) -> None:
        super().setUp()
        self._max_ints: int = 5
        self._source: IntsSupplier = IntsSupplier(max_ints=self._max_ints)
        self._processor: IntsToStrings = IntsToStrings()
        self._collection_target: list[str] = []
        self._instance: CollectToList = CollectToList(self._collection_target)

    @override
    def tearDown(self) -> None:
        super().tearDown()
        self._source.dispose()
        self._processor.dispose()
        self._instance.dispose()

    def test_invoking_sink_as_a_callable_returns_expected_value(self) -> None:
        """:class:`~sghi.miniETL.core.Sink` should return the expected value
        when invoked as a callable.

        In short, ensure that invoking a ``Sink`` instance as a callable
        delegates the actual call to :meth:`~sghi.miniETL.core.Sink.drain`.
        """  # noqa: D202, D205

        self._instance(self._processor(self._source()))

        assert self._collection_target == ["0", "1", "2", "3", "4"]
