import logging
import os
import subprocess
import sys
from pathlib import Path

import clr

logger = logging.getLogger(__name__)

_dll_name = Path("ImageProcessingLibrary.dll")
_dll_path = Path(__file__).parent.parent / "net4.7.2"
_unblocked = False


def _unblock_library(dll_full_path: Path) -> None:
    """Unblock a DLL downloaded from the internet (Windows only).

    Uses PowerShell's Unblock-File command. Only runs once per process
    and is skipped entirely on non-Windows platforms.
    """
    global _unblocked
    if _unblocked:
        return

    if os.name != "nt":
        logger.debug("Unblocking is not necessary on this OS.")
        _unblocked = True
        return

    try:
        subprocess.run(
            ["powershell", "-Command", f"Unblock-File -Path '{dll_full_path}'"],
            check=True,
            capture_output=True,
        )
        logger.info("%s has been unblocked.", dll_full_path)
    except subprocess.CalledProcessError as e:
        logger.warning("Failed to unblock %s: %s", dll_full_path, e)
    except FileNotFoundError:
        logger.debug("PowerShell not found — skipping unblock.")

    _unblocked = True


_unblock_library(_dll_path / _dll_name)

sys.path.append(str(_dll_path))
clr.AddReference(str(_dll_name.stem))

# noinspection PyUnresolvedReferences
from ImageProcessingLibrary import MipFlooding as mip_flooding

if __name__ == "__main__":
    print(_dll_path)
