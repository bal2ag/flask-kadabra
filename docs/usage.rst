.. _usage:

Usage
=====

Using Flask-Kadabra is quite simple. After all, the goal is to enable you to
record metrics from your Flask application with minimal additional code!

- Initialize the :class:`~flask_kadabra.Kadabra` object with your Flask
  application object.
- Decorate any of your routes for which you want to record metrics with
  :data:`~flask_kadabra.record_metrics`.
- Optionally, instrument your application code with any additional metrics you
  want to record with the :class:`~kadabra.client.MetricsCollector` object,
  available as the ``metrics`` attribute on the :data:`~flask.g` object. This
  is shared across your request, is available anywhere within the Flask
  application context, and is totally threadsafe. Note that you don't need to
  record request timing nor 400/500 errors; these will be automatically
  included for each request.

When you run your Flask app, you'll run a local Redis server along with the
Kadabra agent side-by-side with your app, which will enable you to publish your
metrics with no impact to your application's performance, whatever its scale.
For more information on deployment, check out :doc:`deployingyourstack`.

Initialization
--------------

You can initialize the :class:`~flask_kadabra.Kadabra` object directly::

    from flask import Flask
    from flask_kadabra import Kadabra

    app = Flask()
    kadabra = Kadabra(app)

Or, you can defer the installation if you are utilizing the
:doc:`flask:patterns/appfactories` pattern, using the
:meth:`~flask_kadabra.Kadabra.init_app` method::

    from flask import Flask
    from flask_kadabra import Kadabra

    kadabra = Kadabra()

    def create_app():
        app = Flask()
        kadabra.init_app(app)

You can configure the underlying Kadabra client API by passing a dictionary as
the second argument to the :class:`~flask_kadabra.Kadabra` constructor::

    config = {
        'CLIENT_CHANNEL_ARGS': {
            'port': 6500
        }
    }

    app = Flask()
    kadabra(app, config)

For more information about how to configure the client API, see
Kadabra's :ref:`kadabra:configuration` documentation.

There are also some configuration values you can specify for your Flask
application object to change the behavior of the
:class:`~flask_kadabra.Kadabra` object. For more info, check out
:doc:`configuration`.

Enabling Metrics for Your Routes
--------------------------------

To record metrics for API requests to one of your routes, simply use the
:data:`~flask_kadabra.record_metrics` decorator::

    @api.route('/')
    @record_metrics
    def index():
        return "Hello, World!"

This will record the request time in milliseconds (as a timer called
"RequestTime"), whether the HTTP status code of the response was a server
error (as a counter called "Failure" with a value of 0 or 1), and whether the
HTTP status code of the response was a client error (as a counter called
"ClientError" with a value of 0 or 1). For more information on counters and
timers, see :ref:`kadabra:collecting`.

These metrics will be grouped under a "Method" dimension whose value is the
name of your view function, as well as any additional dimensions you've
specified for the ``CLIENT_DEFAULT_DIMENSIONS`` key in Kadabra's configuration
(see :ref:`kadabra:configuration`).

Additionally, a ``metrics`` attribute will be added to Flask's
:data:`~flask.g` object. This exposes the underlying
:class:`~kadabra.client.MetricsCollector` API which allows you to add
counters and timers in your application code. They will be grouped under the
same dimensions as the request time, failure, and client error metrics.

Instrument Your Code with Additional Metrics
--------------------------------------------

Using ``g.metrics`` you can record additional metrics from your application
code. For example, if one of your APIs calls an external third-party service
you may want to time the call::

    start = datetime.datetime.utcnow()
    response = requests.get(...) # External call
    end = datetime.datetime.utcnow()
    g.metrics.set_timer("ExternalCallTime", end - start)

Any metrics you record in the context of a request being executed will be
grouped together under the same dimensions, meaning the same "Method" and any
other dimensions you set via the ``CLIENT_DEFAULT_DIMENSIONS`` configuration
key or elsewhere in your application code.

You can control aspects of how your Flask app uses Kadabra via
:doc:`configuration`.
