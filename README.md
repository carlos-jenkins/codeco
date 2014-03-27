codeco
======

Universal code annotator using Pygments and reStructuredText or Markdown.


Installation
------------

For Python 2.7:

    sudo apt-get install python-pip
    sudo pip install codeco

For Python 3:

    sudo apt-get install python3-pip
    sudo pip3 install codeco


Documentation
-------------

User guide and API Reference can be found in:

- http://codeco.readthedocs.org/


To build it:

    sudo pip install sphinx-bootstrap-theme
    cd doc/
    make html


TO DO
-----

- Fix directive to parse content in annotations connected to the document tree
  and the Sphinx environment.
- Add support for the directive to include code files and annotations files
  via optional arguments.
