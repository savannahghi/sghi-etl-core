"""The API specification for components of the SGHI ETL workflow."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from sghi.disposable import Disposable

if TYPE_CHECKING:
    from collections.abc import Callable

# =============================================================================
# TYPES
# =============================================================================


_PDT = TypeVar("_PDT")
"""Processed Data Type."""

_RDT = TypeVar("_RDT")
"""Raw Data Type."""


# =============================================================================
# BASE INTERFACES
# =============================================================================


class Source(Disposable, Generic[_RDT], metaclass=ABCMeta):
    """An entity that contains or provides data of interest.

    This class defines the interface of a data source, which is a provider of
    raw data. Subclasses implementing this interface should override the
    :meth:`draw` method to specify how the data is obtained.

    In a typical ETL workflow, the `Extract` phase corresponds to the ``draw``
    method of this class. Consequently, a ``Source`` forms the initial step of
    an SGHI ETL workflow and is thus executed first. The obtained data is then
    passed to a :class:`~sghi.miniETL.core.Processor` for further processing.

    .. tip::

        This class implements the :class:`~sghi.disposable.Disposable`
        interface allowing for easy resource(s) management and clean up.
    """

    __slots__ = ()

    def __call__(self) -> _RDT:
        """Obtain raw data from this :class:`data source<Source>`.

        Call this ``Source`` instance as a callable. Delegate actual call
        to :meth:`draw`.

        :return: The raw data from this `Source`.
        """
        return self.draw()

    @abstractmethod
    def draw(self) -> _RDT:
        """Obtain raw data from this :class:`data source<Source>`.

        :return: The raw data from this `Source`.
        """
        ...


class Processor(Disposable, Generic[_RDT, _PDT], metaclass=ABCMeta):
    """The post-extraction transformation(s)/ops performed on raw data.

    This class defines a blueprint for processing raw data and converting it
    into processed data ready for further consumption downstream. Subclasses
    implementing this interface should override the :meth:`process` method to
    specify how the data processing occurs.

    In a typical ETL workflow, the `Transform` phase is functionally equivalent
    to the ``process`` method of this class. Accordingly, a ``Processor`` is
    thus executed immediately after the :class:`~sghi.miniETL.core.Source`
    finishes in an SGHI ETL workflow. The raw data obtained from the ``Source``
    is taken as input. The output of the ``Processor`` is then passed to a
    :class:`~sghi.miniETL.core.Sink` for storage or transmission.

    .. tip::

        This class implements the :class:`~sghi.disposable.Disposable`
        interface allowing for easy resource(s) management and clean up.
    """

    __slots__ = ()

    def __call__(self, raw_data: _RDT) -> _PDT:
        """Transform raw data into processed, clean data and return it.

        Call this ``Processor`` as a callable. Delegate actual call to
        :meth:`process`.

        :param raw_data: The unprocessed data drawn from a `Source`.

        :return: The processed, cleaned data that is ready for further
            consumption downstream.
        """
        return self.process(raw_data)

    @abstractmethod
    def process(self, raw_data: _RDT) -> _PDT:
        """Transform raw data into processed, clean data and return it.

        :param raw_data: The unprocessed data drawn from a `Source`.

        :return: The processed, cleaned data that is ready for further
            consumption downstream.
        """
        ...


class Sink(Disposable, Generic[_PDT], metaclass=ABCMeta):
    """An entity that consumes processed data.

    This interface represents entities that consume processed data(the output
    of a :meth:`data process operation<sghi.miniETL.core.Processor.process>`)
    and the final step of an SGHI ETL workflow. Subclasses implementing this
    interface should override the :meth:`drain` method to specify how the
    processed data is consumed.

    In a typical ETL workflow, the `Load` phase is equivalent to the ``drain``
    method of this class. Therefore, a ``Sink`` is the last step of an SGHI ETL
    workflow and is executed next after the associated :meth:`Processor`
    completes. The Sink takes as input the output of the ``Processor``.

    .. tip::

        This class implements the :class:`~sghi.disposable.Disposable`
        interface allowing for easy resource(s) management and clean up.
    """

    __slots__ = ()

    def __call__(self, processed_data: _PDT) -> None:
        """Consume processed data.

        Call this ``Sink`` as a callable. Delegate actual call to
        :meth:`drain`.

        :param processed_data: The processed data to be consumed.

        :return: None.
        """
        return self.drain(processed_data)

    @abstractmethod
    def drain(self, processed_data: _PDT) -> None:
        """Consume processed data.

        :param processed_data: The processed data to be consumed.

        :return: None.
        """
        ...


class WorkflowDefinition(Generic[_RDT, _PDT], metaclass=ABCMeta):
    """An object that defines the components of an SGHI ETL Workflow.

    A ``WorkflowDefinition`` serves to assemble all the essential parts of an
    ETL Workflow and also serves as the primary unit of execution within an
    SGHI ETL process.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def id(self) -> str:
        """The unique identifier of this workflow.

        This can be used to select a workflow to execute or operate on.

        :return: The unique identifier of this workflow.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of this workflow.

        This is a short, human-friendly "identifier" for this workflow. Unlike
        the :attr:`id`, there is no requirement that this should be unique
        across different workflows. However, workflow authors should strive to
        make the name unique also.

        :return: The name of this workflow.
        """
        ...

    @property
    @abstractmethod
    def description(self) -> str | None:
        """The description of this workflow, if available.

        :return: The description of this workflow or ``None`` if not available.
        """
        ...

    @property
    @abstractmethod
    def source_factory(self) -> Callable[[], Source[_RDT]]:
        """The factory that creates this workflow's :class:`Source`.

        This factory function is invoked early on during the execution of the
        workflow to get the ``Source`` associated with this workflow.

        :return: A factory function that, when invoked, returns the
            ``Source`` instance associated with this workflow.
        """
        ...

    @property
    @abstractmethod
    def processor_factory(
        self,
    ) -> Callable[[], Processor[_RDT, _PDT]]:
        """The factory that creates this workflow's :class:`Processor`.

        This factory function is invoked early on during the execution of the
        workflow to get the ``Processor`` associated with this workflow.

        :return: A factory function that, when invoked, returns the
            ``Processor`` instance associated with this workflow.
        """
        ...

    @property
    @abstractmethod
    def sink_factory(self) -> Callable[[], Sink[_PDT]]:
        """The factory that creates this workflow's :class:`Sink`.

        This factory function is invoked early on during the execution of the
        workflow to get the ``Sink`` associated with this workflow.

        :return: A factory function that, when invoked, returns the
            ``Sink`` instance associated with this workflow.
        """
        ...
