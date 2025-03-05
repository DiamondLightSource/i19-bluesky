import logging
from unittest.mock import MagicMock, patch

import pytest
from dodal.log import LOGGER as dodal_logger

from i19_bluesky.log import (
    LOGGER,
    BeamlineHutch,
    _get_logging_path,
    do_default_logging_setup,
    integrate_bluesky_logs,
    setup_log_config,
)

TEST_GRAYLOG_PORT = 5555


def _destroy_handlers(loggers: list[logging.Logger]):
    for logger in loggers:
        for handler in logger.handlers:
            handler.close()
        logger.handlers.clear()


@pytest.fixture(scope="function")
def clear_and_mock_loggers():
    _destroy_handlers([LOGGER, dodal_logger])
    mock_open_with_tell = MagicMock()
    mock_open_with_tell.tell.return_value = 0
    with (
        patch("dodal.log.logging.FileHandler._open", mock_open_with_tell),
        patch("dodal.log.GELFTCPHandler.emit") as graylog_emit,
        patch("dodal.log.TimedRotatingFileHandler.emit") as filehandler_emit,
    ):
        graylog_emit.reset_mock()
        filehandler_emit.reset_mock()
        yield filehandler_emit, graylog_emit
    _destroy_handlers([LOGGER, dodal_logger])


@pytest.mark.skip_log_setup
@patch("i19_bluesky.log.environ")
@patch("i19_bluesky.log.Path.mkdir")
def test_logging_path_set_to_tmp_if_not_on_beamline(
    mock_mkdir: MagicMock, mock_environ: MagicMock
):
    mock_environ.get.return_value = None
    log_path = _get_logging_path(BeamlineHutch.EH1)
    assert log_path.as_posix() == "/tmp/logs/bluesky/i19-1"
    assert mock_mkdir.call_count == 1


@pytest.mark.skip_log_setup
@pytest.mark.parametrize(
    "hutch, expected_path",
    [
        (BeamlineHutch.EH1, "/dls_sw/i19-1/logs/bluesky"),
        (BeamlineHutch.EH2, "/dls_sw/i19-2/logs/bluesky"),
    ],
)
@patch("i19_bluesky.log.environ")
@patch("i19_bluesky.log.Path.mkdir")
def test_logging_path_set_to_correct_beamline_location_if_env_var_exists(
    mock_mkdir: MagicMock,
    mock_environ: MagicMock,
    hutch: BeamlineHutch,
    expected_path: str,
):
    mock_environ.get.return_value = "i19-1"  # Default on beamline
    # Pass i19-2 for test
    log_path = _get_logging_path(hutch)
    assert log_path.as_posix() == expected_path
    mock_mkdir.assert_called_once()


@pytest.mark.skip_log_setup
def test_integrate_bluesky_logs():
    mock_dodal_logger = MagicMock()
    with (
        patch("i19_bluesky.log.bluesky_logger") as mock_bluesky_log,
        patch("i19_bluesky.log.ophyd_async_logger") as mock_ophyd_log,
    ):
        integrate_bluesky_logs(mock_dodal_logger)
        assert mock_bluesky_log.parent == mock_dodal_logger
        assert mock_ophyd_log.parent == mock_dodal_logger


@pytest.mark.skip_log_setup
def test_messages_logged_from_dodal_and_i19_bluesky_sent_to_graylog_and_file(
    clear_and_mock_loggers,
):
    mock_filehandler_emit, mock_GELFTCPHandler_emit = clear_and_mock_loggers
    do_default_logging_setup(
        "i19-bluesky.log", BeamlineHutch.EH2, TEST_GRAYLOG_PORT, dev_mode=True
    )
    logger = LOGGER
    logger.info("test i19_Bluesky")
    dodal_logger.info("test_dodal")

    filehandler_calls = mock_filehandler_emit.mock_calls
    graylog_calls = mock_GELFTCPHandler_emit.mock_calls

    assert len(filehandler_calls) >= 2
    assert len(graylog_calls) >= 2

    for handler in [filehandler_calls, graylog_calls]:
        handler_names = [c.args[0].name for c in handler]
        handler_messages = [c.args[0].message for c in handler]
        assert "i19_bluesky" in handler_names
        assert "Dodal" in handler_names
        assert "test i19_Bluesky" in handler_messages
        assert "test_dodal" in handler_messages


@patch("i19_bluesky.log.integrate_bluesky_logs")
@patch("i19_bluesky.log.do_default_logging_setup")
def test_setup_log_config_does_default_setup_and_bluesky_integration(
    patch_default_setup, patch_integrate_logs
):
    setup_log_config(BeamlineHutch.EH2, TEST_GRAYLOG_PORT, dev_mode=True)

    patch_integrate_logs.assert_called_once()
    patch_default_setup.assert_called_once_with(
        "i19-bluesky.log", BeamlineHutch.EH2, TEST_GRAYLOG_PORT, True
    )
