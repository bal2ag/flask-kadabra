import datetime
import kadabra

from flask import g, request, current_app
from functools import wraps

__version__ = '0.1.0'

class Kadabra(object):
    """This object holds ties the Flask application object to the Kadabra
    library. Each app object gets its own :class:`~kadabra.Kadabra` instance,
    which it uses to generate a :class:`~kadabra.client.MetricsCollector` for
    each request."""
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app, config=None):
        """Configure the application to use Kadabra. Requests will have access
        to a :class:`~kadabra.client.MetricsCollector` via the `metrics`
        attribute of Flask's :attr:`~flask.Flask.g` object. You can record
        metrics anywhere in the context of a request like so::

            ...
            g.metrics.add_count("userSignup", 1)
            ...

        The metrics object will be closed and sent at the end of the
        request if any view that handles the request has been annotated with
        :meth:`~flask_kadabra.record_metrics`."""
        app.kadabra = kadabra.Kadabra(config)
        self.app = app

        @app.before_request
        def initialize_metrics():
            request.start_time = _get_now()
            g.metrics = current_app.kadabra.metrics()

        @app.after_request
        def transport_metrics(response):
            # Only send the metrics if the current view has "opted in" or they
            # have been enabled application-wide
            if getattr(request, "record_metrics", False):
                end_time = _get_now()
                g.metrics.set_timer("RequestTime",
                        (end_time - request.start_time),
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

def record_metrics(dimensions=None):
    """Views that are annotated with this method will cause any request they
    handle to send all metrics collected via the Kadabra client API.

    :type dimensions: dict
    :param dimensions: Any dimensions to set for metrics that are handled by
                       this view.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request.record_metrics = True
            g.metrics.set_dimension("method", func.__name__)
            if dimensions:
                for name,value in dimensions.iteritems():
                    g.metrics.set_dimension(name, value)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def _get_now():
    return datetime.datetime.utcnow()
