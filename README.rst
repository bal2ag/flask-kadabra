Flask-Kadabra
=============

.. image:: https://secure.travis-ci.org/bal2ag/flask-kadabra.png?branch=master
    :target: http://travis-ci.org/bal2ag/flask-kadabra
    :alt: Build

.. image:: https://readthedocs.org/projects/flask-kadabra/badge/?version=latest&style
    :target: http://flask-kadabra.readthedocs.org/
    :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/bal2ag/flask-kadabra/badge.svg?branch=master
    :target: https://coveralls.io/github/bal2ag/flask-kadabra?branch=master
    :alt: Coverage

How quickly can you figure out how many server errors your Flask app is
throwing? Can you determine which of your routes have the highest error rates?
Do you know how long, on average, your SQLAlchemy writes take?

Flask-Kadabra extends the capabilities of the
`Kadabra <https://github.com/bal2ag/kadabra>`_ metrics library to Flask:

- Enable metrics for your routes with a simple decorator.
- Record metrics from anywhere in your application code, organized by your
  routes.
- Automatically track basic metrics per route such as timing and errors.

Installation is simple::

    $ pip install Flask-Kadabra

Setup is easy::

    from flask import Flask
    from flask_kadabra import Kadabra, record_metrics

    app = Flask()
    kadabra = Kadabra(app)

    @app.route('/')
    @record_metrics
    def index():
        return "Hello, world!"

You can record whatever metrics you want from anywhere in your application
code. They will all be grouped under the route you decorated, and recorded
at the end of your request, with no performance impact::

    from flask import g

    g.metrics.add_count("userSignup", 1.0)

All you have to do is run a local Redis server and run the Kadabra agent
side-by-side with your Flask app, and you have metrics!

Check out the full docs on `read the docs
<http://flask-kadabra.readthedocs.io/en/latest/>`_.
