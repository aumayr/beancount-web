Development
===========

Setting up a development environment
------------------------------------

If you want to hack on Fava or run the latest development version, make sure
you have Python 3 (with `pip`) and Node.js (with `npm`) installed. For running
the tests, you will need `tox` and to run the linters you will need
`pre-commit`.  Then this will get you up and running:

.. code:: bash

    git clone https://github.com/beancount/fava.git
    cd fava
    # using a virtual environment is optional, but recommended
    virtualenv -p python3 venv
    . venv/bin/activate
    make
    pre-commit install  # add a pre-commit hook to run linters
    pip install --editable .

You can start Fava in the virtual environment as usual by running ``fava``.
Running in debug mode with ``fava --debug`` is useful for development.

You can run the tests with ``make test``. After any changes to the Javascript
code, you will need to re-run `make`, or, if you are working on the frontend
code, running ``npm run dev`` in the ``frontend`` folder will watch for file
changes and rebuild the Javascript bundle continuously.

If you need a newer version of Beancount than the latest released one, you can
install from source like so (more details `here
<http://furius.ca/beancount/doc/install>`__):

.. code:: bash

    pip install hg+https://bitbucket.org/blais/beancount#egg=beancount

Contributions are very welcome, just open a PR on `GitHub
<https://github.com/beancount/fava/pulls>`__.

Fava is released under the `MIT License
<https://github.com/beancount/fava/blob/main/LICENSE>`__.

