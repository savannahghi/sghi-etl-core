.. sghi-etl-core documentation master file, created by sphinx-quickstart on
   Thu Jan 11 01:28:14 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: images/sghi_logo.webp
   :align: center

SGHI ETL Core
=============

sghi-etl-core specifies the API of simple ETL workflows. That is, this project
defines and specifies the interfaces of the main components needed to implement
an ETL workflow.

Installation
------------

We recommend using the latest version of Python. Python 3.11 and newer is
supported. We also recommend using a `virtual environment`_ in order
to isolate your project dependencies from other projects and the system.

Install the latest sghi-etl-core version using pip:

.. code-block:: bash

    pip install sghi-etl-core


API Reference
-------------

.. autosummary::
   :template: module.rst
   :toctree: api
   :caption: API
   :recursive:

     sghi.etl.core


.. _virtual environment: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments
