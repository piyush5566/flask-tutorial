Flaskr
======

The blog app.


Install
-------

::

    # clone the repository
    $ git clone https://github.com/piyush5566/flask-tutorial.git
    $ cd flask-tutorial

Create a virtualenv and activate it::
On Windows cmd::
    $ py -3 -m venv .venv
    $ .venv\Scripts\activate.bat

Install Flaskr::
    $ pip install -e .


Run
---

.. code-block:: text
  $ flask --app flaskr init-db
  $ flask --app flaskr run --debug

Open http://127.0.0.1:5000 in a browser

Test
----

::

    $ pip install pytest
    $ pytest

Run with coverage report::

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # open htmlcov/index.html in a browser
