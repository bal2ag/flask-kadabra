import datetime
import kadabra

from flask import g, current_app
from flask import _app_ctx_stack as stack

from functools import wraps

__version__ = '0.1.0'

class Kadabra(object):
    """This object holds ties the Flask application object to the Kadabra
    library. Each app object gets its own :class:`~kadabra.Kadabra` instance,
    which it uses to generate a :class:`~kadabra.client.MetricsCollector` for
    each request.

    :param app: The Flask application object to initialize.
    :type app: ~flask.Flask

    :param config: Dictionary of configuration to use for the
                   :class:`~kadabra.Kadabra` client API. For information on
                   the acceptable values see :ref:`kadabra:configuration`.
    :type config: dict
    """
    def __init__(self, app=None, config=None):
        self.app = app
        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config=None):
        """Configure the application to use Kadabra. Requests will have access
        to a :class:`~kadabra.client.MetricsCollector` via the ``metrics``
        attribute of Flask's :data:`~flask.g` object. You can record
        metrics anywhere in the context of a request like so::

            ...
            g.metrics.add_count("userSignup", 1)
            ...

        The metrics object will be closed and sent at the end of the
        request if any view that handles the request has been annotated with
        :data:`~flask_kadabra.record_metrics`."""
        app.kadabra = kadabra.Kadabra(config)
        self.app = app

        @app.before_request
        def initialize_metrics():
            ctx = stack.top
            if ctx is not None:
                ctx.kadabra_request_start_time = _get_now()
                g.metrics = current_app.kadabra.metrics()

        @app.after_request
        def transport_metrics(response):
            # Only send the metrics if the current view has "opted in".
            ctx = stack.top
            if ctx is not None and getattr(ctx, "enable_kadabra", False):
                end_time = _get_now()
                g.metrics.set_timer("RequestTime",
                        (end_time - ctx.kadabra_request_start_time),
                        kadabra.Units.MILLISECONDS)

                failure = 0
                client_error = 0
                if response.status_code >= 500:
                    failure = 1
                elif response.status_code >= 400:
                    client_error = 1

                g.metrics.add_count("Failure", failure)
                g.metrics.add_count("ClientError", client_error)

                closed = g.metrics.close()
                if not current_app.config.get("DISABLE_KADABRA"):
                    current_app.kadabra.send(closed)
            return response

def record_metrics(func):
    """Views that are annotated with this decorator will cause any request they
    handle to send all metrics collected via the Kadabra client API. For
    example::

        @api.route('/')
        @record_metrics
        def index():
            return 'Hello, world!'

    :param func: The view function to decorate.
    :type func: function
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        ctx = stack.top
        if ctx is not None:
            ctx.enable_kadabra = True
            g.metrics.set_dimension("method", func.__name__)
        return func(*args, **kwargs)
    return decorated_view

def _get_now():
    return datetime.datetime.utcnow()
