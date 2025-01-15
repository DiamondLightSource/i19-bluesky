import subprocess
import sys

from i19_bluesky import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "i19_bluesky", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
