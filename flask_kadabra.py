import datetime
import kadabra

from flask import g, request, current_app
from functools import wraps

__version__ = '0.1.0'

class Kadabra(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app, config=None):
        app.kadabra = kadabra.Client(config)

        @app.before_request
        def initialize_metrics():
            request.start_time = datetime.datetime.utcnow()
            g.metrics = current_app.kadabra.get_collector()

        @app.after_request
        def transport_metrics(response):
            if getattr(request, "record_metrics", False):
                end_time = datetime.datetime.utcnow()
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
                if not app.config.get("DISABLE_KADABRA"):
                    current_app.kadabra.send(closed)
            return response

def record_metrics(dimensions=None):
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
