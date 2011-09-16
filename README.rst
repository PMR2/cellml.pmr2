============
Introduction
============

This package provides CellML Support for PMR2, specifically the
generation and display of CellML related data for PMR2 Exposure files.


------------
Installation
------------

This package requires Plone 3 or later, however Plone 4 is now the
supported version thus Plone 3 support will not be not explicitly
tested.


~~~~~~~~~~~~~~~~~~~~~~~~
Installing with buildout
~~~~~~~~~~~~~~~~~~~~~~~~

You can install cellml.pmr2 using `buildout`_.  

However this module depends on the CellML API Python bindings, which
requires its own buildout process.  The best way to install this is to
use the default PMR2 buildout, which includes all dependencies required
to get you started using PMR2 with CellML support.

.. _buildout: http://pypi.python.org/pypi/zc.buildout

However, if you must install this package on your own, you may do this
in your `buildout.cfg` file.

Example::

    [buildout]
    ...

    [instance]
    ...

    eggs =
        ...
        cellml.pmr2

    zcml =
        ...
        cellml.pmr2


-----
Usage
-----

For further usage information, please refer to the tests and the
associated README files (i.e. cellml/pmr2/README.rst)

