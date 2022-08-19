import mock
import pytest

import gantry
from gantry.exceptions import ClientNotInitialized
from gantry.logger import main


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("ping", {}),
        ("ready", {}),
        ("instrument", {}),
        ("log_feedback", {}),
        ("log_feedback_event", {}),
        ("log_predictions", {}),
        ("log_prediction_event", {}),
        ("log_record", {"application": "foobar", "version": "1.2.3"}),
        ("log_records", {"application": "foobar", "version": "1.2.3"}),
    ],
)
@pytest.mark.parametrize("module", [main, gantry])
def test_uninit_client_main(module, method, params):
    with mock.patch("gantry.logger.main._CLIENT", None):
        with pytest.raises(ClientNotInitialized):
            getattr(module, method)(**params)


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("ping", {}),
        ("ready", {}),
        ("instrument", {}),
        ("log_feedback", {}),
        ("log_feedback_event", {}),
        ("log_predictions", {}),
        ("log_prediction_event", {}),
        (
            "log_records",
            {
                "application": "foobar",
                "version": "1.2.3",
                "inputs": [1, 2, 3],
                "outputs": [4, 5, 6],
                "feedback_keys": ["A"],
                "feedback_ids": [10],
                "feedbacks": [4, 5, 6],
                "ignore_inputs": ["A"],
                "timestamps": "today",
                "sort_on_timestamp": True,
                "sample_rate": 1.0,
                "as_batch": False,
                "tags": {},
            },
        ),
        (
            "log_record",
            {
                "application": "foobar",
                "version": "1.2.3",
                "inputs": [1, 2, 3],
                "outputs": [4, 5, 6],
                "feedback_keys": ["A"],
                "feedback_id": [10],
                "feedback": [4, 5, 6],
                "ignore_inputs": ["A"],
                "timestamp": "today",
                "sample_rate": 1.0,
                "tags": {},
            },
        ),
    ],
)
@pytest.mark.parametrize("module", [main, gantry])
def test_logger_methods(module, method, params):
    m = mock.Mock()
    with mock.patch("gantry.logger.main._CLIENT", m):
        getattr(module, method)(**params)
        getattr(m, method).assert_called_once_with(**params)


@pytest.mark.parametrize("ping_ret", [True, False])
@pytest.mark.parametrize("module", [main, gantry])
@mock.patch("gantry.logger.client.Gantry.ping")
@mock.patch("gantry.logger.client.Gantry.ready")
def test_logger_init(mock_ready, mock_ping, module, ping_ret):
    m = mock.Mock()
    mock_ping.return_value = ping_ret
    with mock.patch("gantry.logger.main._CLIENT", m):
        module.init()
        mock_ping.assert_called_once()
        if ping_ret:
            mock_ready.assert_called_once()
