Changelog
=========

0.10.5 - Released (2021-06-23)
------------------------------

* Correct the pmr specific urljoin helper such that it will not clobber
  a provided url's external scheme if it was presen; fixes joining an
  absolute url.

0.10.4 - Released (2021-06-10)
------------------------------

* Updated test cases to work with plone.testing-4.1.x.

0.10.3 - Released (2019-08-30)
------------------------------

* Replacing the legacy PMR1 title generator to not rely on the source
  workspace for the generation of "citation author, year" title for any
  given exposure files, as all legacy exposures are assumed to have been
  properly annotated.

0.10.2 - Released (2016-12-29)
------------------------------

* Minor text fixes.

0.10.1 - Released (2016-09-21)
------------------------------

* Fix the issue where using unicode in titles may result in errors.
* Tooltip for the OpenCOR launch link, though done purely in JavaScript
  due to framework limitations.

0.10.0 - Released (2016-03-08)
------------------------------

* Support for the latest web service version (i.e. Collection+JSON).
* Various changes to make it compatible with rdflib-4.x, as the package
  ``pmr2.rdf`` has pinned its dependency to the latest versions.
* Include a custom parser that restores the less strict method of rdfxml
  parsing.
* BiVeS based interactive component viewer for mathematic equations.
* OpenCOR launch link through the ExposureFileNote mechanism.

0.9.1 - Released (2015-08-18)
-----------------------------

* Fixed an issue where empty CellML Metadata attributes would result in
  a raw rdflib object serialized into the note object, causing potential
  issues later.

0.9 - Released (2015-03-20)
---------------------------

* Main test no longer directly depend on ``pmr2.mercurial`` for the data
  as ``pmr2.app`` now has a test case that provides the data.
* Fixed the setup for the mercurial specific live test case such that it
  is completely excluded from the testsuite as it was interfering with
  comprehensive testing of all relevant packages if ``pmr2.mercurial``
  was missing.

0.8 - Released (2014-08-14)
---------------------------

* New model loader that will be able to resolve CellML files that are
  known (or made known to be) part of the repo.
* Facilities that resolve absolutely linked references that have
  hostnames that are virtual hosts of the current instance are provided,
  including editors for the configuration of this.  This is mostly for
  embedded workspaces which parent workspaces must use absolute URLs for
  them.
* New test harnesses - uses the test runner layer facilities.

0.7 - Released (2014-04-03)
---------------------------

* `jq` to `$` renaming.

0.6 - Released (2013-07-08)
---------------------------

* Update dependency of form library to pmr2.z3cform.
* Make use of bootstrap css classes.
* Ensure the Plone dynamic stuff are disabled to not interfere with the
  CellML specific search forms.

0.5.1 - Released (2012-11-06)
-----------------------------

* Handle some subset of csymbols such that they will be rendered in the
  Mathematics view. [A1kmm]
* CellML search viewlet should be enabled at the intended case by
  default.

0.5 - Released (2012-10-03)
---------------------------

* Removal of form layout wrappers and general form cleanups.
* Update imports and library used to not depend on deprecated cruft.
* Provide PMR1 curation flags as support for that has been moved out of
  pmr2.app.

0.4 - Released (2012-02-10)
---------------------------

* Provide a CellML specific searchbox viewlet.
* Clean up some of the indexes to enable better searching.
* Compatibility fix for the new annotator requirements.

0.3.1 - Released (2011-09-19)
-----------------------------

* Raw code wrapper need to be updated to not render.

0.3 - Released (2011-08-17)
---------------------------

* Updated import location for pmr2.app-0.4.

0.2 - Released (2011-04-11)
---------------------------

* Math rendering for CellML 1.1, make use of the CellML API.
* Use MathJAX for cross browser math rendering.
* Updated import location to pmr2.app-0.4
* Included other CellML specific parts that got removed fom pmr2.app.

0.1.1 - Released (2010-07-05)
-----------------------------

* Fixed handling of null values in fields which were never present
  before.

0.1 - Released (2010-06-21)
---------------------------

* Extracted all CellML related functionality found in pmr2.app into this
  package.
* Merged functions provided in pmr2.processor.cmeta into this package.
* Keywords and other metadata no longer depends on the presence of 
  citations for the Cmeta annotations.
* Updated code generation, now generates CellML 1.1 code using the 
  cellml.api.simple package.  
* Also no longer deadlocks server process due to the usage of fork 
  (workaround of the select syscall locking issue by the API).
* Rendering of generated code uses shjs for highlighting.
* Various OpenCell specific views added.  Merged the launch via OpenCell
  link into the session link (i.e. when no session file is specified,
  the CellML file will be launched via that link instead).
