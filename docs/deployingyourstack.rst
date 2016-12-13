.. _deployingyourstack:

Deploying Your Stack
====================

Deploying your Flask application involves more than just your application code
itself. Even the simplest production deployment requires a real webserver to
route HTTP requests to your application (see :ref:`flask:deployment`). I refer
to the application code plus everything needed for it to smoothly run as a
fully-functioning web service as your **stack**. Your stack is the unit that is
deployed along with your application code to your local host, a remote server,
a virtual machine, or whatever environment from which you're running everything
(more on that in a moment).

Kadabra requires two additions to your application's stack:

1. A channel to send metrics asynchronously from your application. Channels are
   described more in :ref:`kadabra:sending`, but since Redis is currently the
   only supported channel, this means you will need to be running a Redis
   server to which your Flask application can connect. Typically this just
   means running a local Redis instance alongside your application.
2. A properly configured :class:`~kadabra.Agent` running in a dedicated process
   to publish your application metrics. For more information see
   :ref:`kadabra:publishing`.

You'll eventually want a backend database where you can publish metrics. The
only backend database currently supported is `InfluxDB 
<https://www.influxdata.com/time-series-platform/influxdb/>`_. You can setup an
InfluxDB server on your hosting provider or use InfluxDB's hosted options.
Until you have your server setup, you can just use the
:class:`~kadabra.publishers.DebugPublisher` to send metrics to a logger.

.. note:: Having the metrics in a dedicated database like InfluxDB will be
   extremely helpful for production environments and allows you to easily set
   up dashboards and alarming around your service. You should definitely spend
   some time setting it up when you're ready to deploy into production and
   start acquiring users.

Infrastructure Management
-------------------------

In the modern era, you will want to make it as easy to deploy your application
as possible. You don't want to be manually installing your dependencies,
starting the Redis server, kicking off your application, and so on for every
deployment. In addition to saving developer pain, this also helps prevent bugs
from being introduced during deployment time, and makes it simple to deploy to
different environments and cloud providers. Furthermore, you don't want to have
to manually restart processes when they inevitably fail; your infrastructure
management system should take care of process management for you.

Options include configuration management and orchestration tools such as
`Puppet <https://puppet.com/>`_, `Chef <https://www.chef.io/chef/>`_, and
`Ansible <https://www.ansible.com/>`_. Personally I like to deploy my
applications as containers using `Docker <https://www.docker.com/>`_. Whatever
tool you use, you'll want to be sure that metrics flow from your application to
the publisher destination of your choice.

The Full Stack
--------------

I think of my basic Flask application (say, one that talks to a SQL database)
in five components:

1. The Flask application code itself
2. The HTTP webserver to serve the Flask application (typically
   `gunicorn <http://gunicorn.org/>`_ running locally)
3. The reverse proxy that will listen to external requests and proxy them to
   gunicorn (typically `nginx <https://www.nginx.com>`_)
4. A local `Redis <https://redis.io/>`_ server for queueing metrics to be
   published and as a cache if needed
5. The Kadabra :class:`~kadabra.Agent` for publishing metrics

Additionally I usually run an InfluxDB server that can only be accessed by my
webserver hosts, which will publish metrics to that server.

Because I use Docker, I typically author a simple `compose
<https://docs.docker.com/compose/>`_ file with a service for each of the
components above. A thorough treatment of "dockerizing" the entire stack is
beyond the scope of this section, but the agent is worth talking about.

Running the agent basically consists of configuring it and calling the
:meth:`~kadabra.Agent.start` method. You can use the code from
:ref:`kadabra:gettingstarted` and just run it in a dedicated Python process,
with the possible addition of configuration e.g. if your Redis server is
refered to as something other than ``localhost``.

You will want to run this process under some sort of a process management
system, at a minimum something like `supervisord <http://supervisord.org/>`_
but ideally a more robust system like Docker. In my compose file I use the
``command`` configuration key with something like ``python run.py``, where
``run.py`` contains the agent code. The agent is designed to respond gracefully
to shutdown signals like ``SIGINT`` and ``SIGTERM``, and will try to make sure
there are no metrics that haven't yet been published before shutting down.
