.. toctree::
   :hidden:

========================
``codeco`` documentation
========================

:Revision: |date|

.. warning::

   Work In Progress.

.. contents:: Table of Contents
   :local:


What is ``codeco`` and what is not
==================================

``codeco`` is a Python universal code commenter that allows to generate
annotations for a particular piece of code. It produces HTML that displays
your annotations alongside your code. Annotations can be written in
`Markdown`_ or `reStructuredText`_, while code is passed through `Pygments`_
for syntax highlighting.

``codeco`` is inspired by previous works like `Pycco`_ and `Docco`_ with a
paradigm shift and built around their limitations, like the inability to
separate between documentation comments (annotations) and in-code comments
[#f1]_, difficulty to support other programming languages, difficulty to
support other markup formats and lack of integration with other documentation
frameworks.

Nevertheless, ``codeco`` is not a an exact replacement of `Pycco`_. In
``codeco`` code annotations reside outside the code itself, and is referenced
by line number. It is not desirable for constantly changing code because of the
overhead that implies to redirect the annotations to the correct line number.
It is more appropiate for code explanations in academia, walkthroughs and
tutorials where the code example resides inside the documentation or rarely
changes. Someday this overhead could be minimized with automatic line
synchronization for code changes, but we are not there yet.


.. rubric:: Notes

.. [#f1] In ``codeco`` you can, for example, keep comments on code and make
   annotations about them, or keep comments in a parseable language for
   documentation autogeneration (autodoc) and make annotations about it.


Features
========

- Annotations can highlight multiple lines, or only some characters in
  those lines.
- Interactive line highlighting using JQuery.
- Annotations can be written in `Markdown`_ or `reStructuredText`_.
- Supports any programming language `Pygments`_ supports.
- Can be used standalone, as a library or as a `Sphinx`_ directive.
- Support for templates for HTML generation.
- Python 2.7 and 3 compatible.
- Free and Open-Source Software.


Install
=======

To install ``codeco``, simply execute:

.. annotated-code::

   pip install codeco

   <[==============]>

   <[hidden-annotation]> 1

   Install ``codeco`` using ``pip``.

   ``pip`` is the preferred package manager that allows to install Python
   packages listed in
   `PyPI - the Python Package Index <https://pypi.python.org/pypi>`_.

   In Debian-based systems install packages:

   - For Python 2: ``python-pip``.
   - For Python 3: ``python3-pip``.

   For other platforms please visit the
   `pip homepage <http://www.pip-installer.org/>`_.

   ``codeco`` requires the following libraries, but they should be installed
   along ``codeco``:

   - `Markdown <https://pythonhosted.org/Markdown/>`_
     allows to render markdown syntax.
   - `Docutils <http://docutils.sourceforge.net/docs/index.html>`_
     allows to render reStructuredText.
   - `Pygments <http://pygments.org/>`_
     allows to highlight code.
   - `Beautiful Soup <http://www.crummy.com/software/BeautifulSoup/bs4/doc/>`_
     allows to manipulate the generated HTML so ``codeco`` is able to mark it
     with useful classes for interaction.
   - `html5lib <https://pypi.python.org/pypi/html5lib>`_ is the parser used
     by Beautiful Soup.

   To install them manually:

   .. sourcecode:: bash

      pip install markdown docutils pygments beautifulsoup4 html5lib


Or, to install the latest source:

.. annotated-code::

   git clone https://github.com/carlos-jenkins/codeco.git
   cd codeco
   python setup.py install

   <[==============]>

   <[annotation]> 1[10,54]

   The source for ``codeco`` is available on
   `GitHub <https://github.com/carlos-jenkins/codeco>`_, and released under the
   Apache 2 license.


Usage
=====

``codeco`` can be used standalone, as a library or with `Sphinx`_.

Standalone
----------

If you install ``codeco``, you can run it from the command-line:

.. sourcecode:: bash

   codeco -h


.. _Sphinx: http://sphinx-doc.org/
.. _Markdown: http://pythonhosted.org/Markdown/
.. _reStructuredText: http://sphinx-doc.org/rest.html
.. _Pygments: http://pygments.org/
.. _Pycco: http://fitzgen.github.io/pycco/
.. _Docco: http://jashkenas.github.io/docco/
.. _GitHub: https://github.com/carlos-jenkins/codeco


.. General replacement tokens

.. |date| date:: %B %d ,%Y
.. |time| date:: %H:%M
