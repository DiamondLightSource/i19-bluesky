import logging
from unittest.mock import MagicMock, patch

import pytest

from i19_bluesky.log import BeamlineHutch, _get_logging_path, integrate_bluesky_logs


@pytest.fixture
def dummy_logger():
    logger = logging.getLogger("i19_bluesky")
    yield logger


def _destroy_handlers(logger: logging.Logger):
    for handler in logger.handlers:
        handler.close()
    logger.handlers.clear()


@patch("i19_bluesky.log.environ")
@patch("i19_bluesky.log.Path.mkdir")
def test_logging_path_set_to_tmp_if_not_on_beamline(
    mock_mkdir: MagicMock, mock_environ: MagicMock
):
    mock_environ.get.return_value = None
    log_path = _get_logging_path(BeamlineHutch.EH1)
    assert log_path.as_posix() == "/tmp/logs/bluesky/i19-1"
    assert mock_mkdir.call_count == 1


@patch("i19_bluesky.log.environ")
@patch("i19_bluesky.log.Path.mkdir")
def test_logging_path_set_to_correct_beamline_location(
    mock_mkdir: MagicMock, mock_environ: MagicMock
):
    mock_environ.get.return_value = "i19-1"  # Default on beamline
    # Pass i19-2 for test
    log_path = _get_logging_path(BeamlineHutch.EH2)
    assert log_path.as_posix() == "/dls_sw/i19-2/logs/bluesky"
    mock_mkdir.assert_called_once()


def test_integrate_bluesky_logs():
    mock_dodal_logger = MagicMock()
    with (
        patch("i19_bluesky.log.bluesky_logger") as mock_bluesky_log,
        patch("i19_bluesky.log.ophyd_async_logger") as mock_ophyd_log,
    ):
        integrate_bluesky_logs(mock_dodal_logger)
        assert mock_bluesky_log.parent == mock_dodal_logger
        assert mock_ophyd_log.parent == mock_dodal_logger
