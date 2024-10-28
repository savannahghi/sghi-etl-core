"""Tests for the ``sghi.etl.core.config`` module."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from unittest import TestCase

import pytest
from typing_extensions import override

from sghi.disposable import not_disposed
from sghi.etl.core import Processor, Sink, Source, WorkflowDefinition
from sghi.utils import type_fqn

# =============================================================================
# TESTS HELPERS
# =============================================================================


@dataclass(slots=True)
class IntsSupplier(Source[Iterable[int]]):
    """A  :class:`Source` that supplies integers."""

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
    def apply(self, raw_data: Iterable[int]) -> Iterable[str]:
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

    collection_target: list[str] = field(default_factory=list)
    _is_disposed: bool = field(default=False, init=False)

    @not_disposed
    @override
    def drain(self, processed_data: Iterable[str]) -> None:
        self.collection_target.extend(processed_data)

    @property
    @override
    def is_disposed(self) -> bool:
        return self._is_disposed

    @override
    def dispose(self) -> None:
        self._is_disposed = True


@dataclass(frozen=True, slots=True)
class TestWorkflowDefinition(WorkflowDefinition[Iterable[int], Iterable[str]]):
    """A simple :class:`WorkflowDefinition` implementation."""

    @property
    @override
    def description(self) -> str | None:
        return None

    @property
    @override
    def id(self) -> str:
        return "test"

    @property
    @override
    def name(self) -> str:
        return "Test Workflow"

    @property
    @override
    def processor_factory(
        self,
    ) -> Callable[[], Processor[Iterable[int], Iterable[str]]]:
        return IntsToStrings

    @property
    @override
    def sink_factory(self) -> Callable[[], Sink[Iterable[str]]]:
        return CollectToList

    @property
    @override
    def source_factory(self) -> Callable[[], Source[Iterable[int]]]:
        return IntsSupplier


# =============================================================================
# TESTS
# =============================================================================


class TestSource(TestCase):
    """Tests for the :class:`sghi.etl.core.Source` interface.

    Tests for the default method implementations of the ``Source`` interface.
    """

    def test_invoking_source_as_a_callable_returns_expected_value(
        self,
    ) -> None:
        """:class:`~sghi.etl.core.Source` should return the expected
        value when invoked as a callable.

        In short, ensure that invoking a ``Source`` instance as a callable
        delegates the actual call to :meth:`~sghi.etl.core.Source.draw`.
        """  # noqa: D205
        instance1: IntsSupplier
        instance2: IntsSupplier
        max_ints: int = 4

        with (
            IntsSupplier(max_ints=max_ints) as instance1,
            IntsSupplier(max_ints=max_ints) as instance2,
        ):
            # noinspection PyArgumentList
            assert list(instance1.draw()) == list(instance2()) == [0, 1, 2, 3]


class TestProcessor(TestCase):
    """Tests for the :class:`sghi.etl.core.Processor` interface.

    Tests for the default method implementations of the ``Processor``
    interface.
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
        delegates the actual call to :meth:`~sghi.etl.core.Processor.apply`.
        """  # noqa: D205
        raw_values = tuple(self._source())

        instance1: IntsToStrings
        instance2: IntsToStrings

        with IntsToStrings() as instance1, IntsToStrings() as instance2:
            assert (
                tuple(instance1.apply(raw_values))
                == tuple(instance2(raw_values))
                == ("0", "1", "2", "3", "4")
            )

    def test_invoking_the_process_method_returns_expected_value(self) -> None:
        """:meth:`~sghi.etl.core.Processor.process` should return the expected
        value.

        That is, invoking the ``process`` method of a ``Processor`` instance
        should return the same value as invoking the
        :meth:`~sghi.etl.core.Processor.apply` method of the same instance.
        """  # noqa: D205
        raw_values = tuple(self._source())

        instance1: IntsToStrings
        instance2: IntsToStrings

        with IntsToStrings() as instance1, IntsToStrings() as instance2:
            assert (
                tuple(instance1.apply(raw_values))
                == tuple(instance2.process(raw_values))  # type: ignore
                == ("0", "1", "2", "3", "4")
            )

    def test_invoking_the_process_method_raises_a_deprecation_waring(
        self,
    ) -> None:
        """:meth:`~sghi.etl.core.Processor.process` is deprecated for removal.

        Ensure that invoking the ``process`` method raised a
        ``DeprecationWarning``.
        """
        raw_values = tuple(self._source())
        instance: IntsToStrings = IntsToStrings()
        with pytest.warns(DeprecationWarning, match='Use "apply" instead'):
            instance.process(raw_values)  # type: ignore

        instance.dispose()


class TestSink(TestCase):
    """Tests for the :class:`sghi.etl.core.Processor` interface.

    Tests for the default method implementations of the ``Sink`` interface.
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
        """  # noqa: D205
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


class TestWorkflow(TestCase):
    """Tests for the :class:`sghi.etl.core.WorkflowDefinition` interface.

    Tests for the default method implementations of the ``WorkflowDefinition``
    interface.
    """

    @override
    def setUp(self) -> None:
        super().setUp()
        self._instance: WorkflowDefinition[Iterable[int], Iterable[str]]
        self._instance = TestWorkflowDefinition()

    def test_epilogue_return_value(self) -> None:
        """The default implementation of
        :meth:`~sghi.etl.core.WorkflowDefinition.epilogue` should return a
        callable that does nothing.
        """  # noqa: D205
        epilogue: Callable[[], None] = self._instance.epilogue
        assert callable(epilogue)

        try:
            epilogue()
        except Exception as exp:  # noqa: BLE001
            _fail_reason: str = (
                f"The following unexpected error: '{exp!r}', was raised when "
                "invoking the callable returned by the default implementation "
                f"of the '{type_fqn(WorkflowDefinition)}.epilogue' property. "
                "No errors should be raised by the callable returned by the "
                "default implementation of the said property."
            )
            pytest.fail(reason=_fail_reason)

    def test_prologue_return_value(self) -> None:
        """The default implementation of
        :meth:`~sghi.etl.core.WorkflowDefinition.prologue` should return a
        callable that does nothing.
        """  # noqa: D205
        prologue: Callable[[], None] = self._instance.prologue
        assert callable(prologue)

        try:
            prologue()
        except Exception as exp:  # noqa: BLE001
            _fail_reason: str = (
                f"The following unexpected error: '{exp!r}', was raised when "
                "invoking the callable returned by the default implementation "
                f"of the '{type_fqn(WorkflowDefinition)}.prologue' property. "
                "No errors should be raised by the callable returned by the "
                "default implementation of the said property."
            )
            pytest.fail(reason=_fail_reason)
