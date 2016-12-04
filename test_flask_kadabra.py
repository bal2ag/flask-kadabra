from flask import (Flask, g, Response, request, current_app)

from flask_kadabra import Kadabra, record_metrics
import kadabra

from mock import mock, MagicMock, call

import datetime

NOW = datetime.datetime.utcnow()

def get_app():
    return Flask(__name__)

@mock.patch('flask_kadabra.Kadabra.init_app')
def test_ctor_no_app(mock_init_app):
    kadabra = Kadabra()

    kadabra.init_app.assert_has_calls([])
    assert kadabra.app == None

@mock.patch('flask_kadabra.Kadabra.init_app')
def test_ctor_no_app(mock_init_app):
    app = MagicMock()
    kadabra = Kadabra(app)

    kadabra.init_app.assert_called_with(app)
    assert kadabra.app == app

@mock.patch('kadabra.Kadabra')
def test_init(mock_client):
    client = mock_client.return_value
    app = get_app()

    kadabra = Kadabra()
    kadabra.init_app(app)

    assert kadabra.app == app
    assert app.kadabra == client
    assert len(app.before_request_funcs[None]) == 1
    assert app.before_request_funcs[None][0].__name__ == 'initialize_metrics'
    assert len(app.after_request_funcs[None]) == 1
    assert app.after_request_funcs[None][0].__name__ == 'transport_metrics'

@mock.patch('kadabra.Kadabra')
def test_init_metrics(mock_client):
    client = mock_client.return_value
    client.metrics = MagicMock()
    client.send = MagicMock()

    app = get_app()
    @app.route('/')
    def test_route():
        return 'test'

    kadabra = Kadabra()
    kadabra.init_app(app)

    with app.test_client() as c:
        c.get('/')
        client.metrics.assert_called_with()
        client.send.assert_has_calls([])

@mock.patch('flask_kadabra._get_now', return_value=NOW)
@mock.patch('kadabra.Kadabra')
def test_transport_200(mock_client, mock_get_now):
    client = mock_client.return_value
    client.metrics = MagicMock()
    metrics = client.metrics.return_value
    metrics.add_count = MagicMock()
    metrics.set_timer = MagicMock()
    metrics.set_dimension = MagicMock()
    metrics.close = MagicMock()
    closed = metrics.close.return_value
    client.send = MagicMock()

    app = get_app()

    @app.route('/')
    @record_metrics()
    def test_route():
        return 'test'

    unit = Kadabra()
    unit.init_app(app)

    with app.test_client() as c:
        c.get('/')
        client.metrics.assert_called_with()
        metrics.set_dimension.assert_called_with("method", "test_route")
        metrics.set_timer.assert_called_with("RequestTime", NOW - NOW,
                kadabra.Units.MILLISECONDS)
        metrics.add_count.assert_has_calls([
                call("Failure", 0),
                call("ClientError", 0)])
        metrics.close.assert_called_with()
        client.send.assert_called_with(closed)

@mock.patch('flask_kadabra._get_now', return_value=NOW)
@mock.patch('kadabra.Kadabra')
def test_transport_500(mock_client, mock_get_now):
    client = mock_client.return_value
    client.metrics = MagicMock()
    metrics = client.metrics.return_value
    metrics.add_count = MagicMock()
    metrics.set_timer = MagicMock()
    metrics.set_dimension = MagicMock()
    metrics.close = MagicMock()
    closed = metrics.close.return_value
    client.send = MagicMock()

    app = get_app()
    
    @app.route('/')
    @record_metrics()
    def test_route():
        response = Response()
        response.status_code = 500
        return response

    unit = Kadabra()
    unit.init_app(app)

    with app.test_client() as c:
        c.get('/')
        client.metrics.assert_called_with()
        metrics.set_dimension.assert_called_with("method", "test_route")
        metrics.set_timer.assert_called_with("RequestTime", NOW - NOW,
                kadabra.Units.MILLISECONDS)
        metrics.add_count.assert_has_calls([
                call("Failure", 1),
                call("ClientError", 0)])
        metrics.close.assert_called_with()
        client.send.assert_called_with(closed)

@mock.patch('flask_kadabra._get_now', return_value=NOW)
@mock.patch('kadabra.Kadabra')
def test_transport_400(mock_client, mock_get_now):
    client = mock_client.return_value
    client.metrics = MagicMock()
    metrics = client.metrics.return_value
    metrics.add_count = MagicMock()
    metrics.set_timer = MagicMock()
    metrics.set_dimension = MagicMock()
    metrics.close = MagicMock()
    closed = metrics.close.return_value
    client.send = MagicMock()

    app = get_app()

    @app.route('/')
    @record_metrics()
    def test_route():
        response = Response()
        response.status_code = 400
        return response

    unit = Kadabra()
    unit.init_app(app)

    with app.test_client() as c:
        c.get('/')
        client.metrics.assert_called_with()
        metrics.set_dimension.assert_called_with("method", "test_route")
        metrics.set_timer.assert_called_with("RequestTime", NOW - NOW,
                kadabra.Units.MILLISECONDS)
        metrics.add_count.assert_has_calls([
                call("Failure", 0),
                call("ClientError", 1)])
        metrics.close.assert_called_with()
        client.send.assert_called_with(closed)

@mock.patch('flask_kadabra._get_now', return_value=NOW)
@mock.patch('kadabra.Kadabra')
def test_transport_disable(mock_client, mock_get_now):
    client = mock_client.return_value
    client.metrics = MagicMock()
    metrics = client.metrics.return_value
    metrics.add_count = MagicMock()
    metrics.set_timer = MagicMock()
    metrics.set_dimension = MagicMock()
    metrics.close = MagicMock()
    closed = metrics.close.return_value
    client.send = MagicMock()

    app = get_app()
    app.config["DISABLE_KADABRA"] = True

    @app.route('/')
    @record_metrics()
    def test_route():
        return 'test'

    unit = Kadabra()
    unit.init_app(app)

    with app.test_client() as c:
        c.get('/')
        client.metrics.assert_called_with()
        metrics.set_dimension.assert_called_with("method", "test_route")
        metrics.set_timer.assert_called_with("RequestTime", NOW - NOW,
                kadabra.Units.MILLISECONDS)
        metrics.add_count.assert_has_calls([
                call("Failure", 0),
                call("ClientError", 0)])
        metrics.close.assert_called_with()
        client.send.assert_has_calls([])

@mock.patch('flask_kadabra._get_now', return_value=NOW)
@mock.patch('kadabra.Kadabra')
def test_decorator_dimensions(mock_client, mock_get_now):
    client = mock_client.return_value
    client.metrics = MagicMock()
    metrics = client.metrics.return_value
    metrics.add_count = MagicMock()
    metrics.set_timer = MagicMock()
    metrics.set_dimension = MagicMock()
    metrics.close = MagicMock()
    closed = metrics.close.return_value
    client.send = MagicMock()

    testDimensionName = "testDimensionName"
    testDimensionValue = "testDimensionValue"

    app = get_app()

    @app.route('/')
    @record_metrics({testDimensionName: testDimensionValue})
    def test_route():
        return 'test'

    unit = Kadabra()
    unit.init_app(app)

    with app.test_client() as c:
        c.get('/')
        client.metrics.assert_called_with()
        metrics.set_dimension.assert_has_calls([
                call("method", "test_route"),
                call(testDimensionName, testDimensionValue)])
        metrics.set_timer.assert_called_with("RequestTime", NOW - NOW,
                kadabra.Units.MILLISECONDS)
        metrics.add_count.assert_has_calls([
                call("Failure", 0),
                call("ClientError", 0)])
        metrics.close.assert_called_with()
        client.send.assert_called_with(closed)
