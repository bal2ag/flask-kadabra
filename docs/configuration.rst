.. _configuration:

Configuration
=============

Most of the configuration you'll do is for the :class:`~kadabra.Kadabra` client
API itself. You'll pass a dictionary containing all the configuration keys and
values for any defaults you want to override when you initialize the Flask
extension::

    from flask import Flask
    from flask_kadabra import Kadabra

    app = Flask()

    config = {
        "CLIENT_DEFAULT_DIMENSIONS": {
            "environment": "development"
        }
    }

    kadabra = Kadabra()
    kadabra.init_app(app, config)

Or using the constructor directly::

    kadabra = Kadabra(app, config)

Configuration keys, values, and defaults are explained in the Kadabra
documentation under :ref:`kadabra:configuration`.

However, the Flask extension does support one configuration value itself, which
can be stored in the Flask application's :class:`~flask.Config`.

================= =============================================================
`DISABLE_KADABRA` If present in the config and set to ``True``, metrics will
                  not actually be sent to the channel. This is useful if you
                  are just developing your service and don't need to actually
                  see metrics flowing yet.
================= =============================================================
