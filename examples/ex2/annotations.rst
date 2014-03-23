<[annotation]> 1

1. Install ``pip``
==================

``pip`` is the preferred package manager that allows to install Python packages
listed in `PyPI - the Python Package Index <https://pypi.python.org/pypi>`_.

In Debian-based systems install packages:

:Python 2: ``python-pip``.
:Python 3: ``python3-pip``.

For other platforms please visit the
`pip homepage <http://www.pip-installer.org/>`_.


<[annotation]> 2

2. Install dependencies
=======================

``codeco`` has the following dependencies:

- `Markdown <https://pythonhosted.org/Markdown/>`_
  allows to render markdown syntax.
- `Docutils <http://docutils.sourceforge.net/docs/index.html>`_
  allows to render reStructuredText.
- `Pygments <http://pygments.org/>`_
  allows to highlight code.
- `Beautiful Soup <http://www.crummy.com/software/BeautifulSoup/bs4/doc/>`_
  allows to manipulate the generated HTML so ``codeco`` is able mark it with
  useful classes for interaction.
