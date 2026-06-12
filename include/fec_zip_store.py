"""FEC ZIP file storage utilities.

Handles deterministic path construction, streaming download, and retention
(reuse of an already-downloaded ZIP without re-fetching from FEC).

Path contract: data/raw/<file_type>_<cycle>.zip
Example: data/raw/indiv_2024.zip
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Default raw data directory relative to the project root.
_PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR: Path = _PROJECT_ROOT / "data" / "raw"

# Chunk size for streaming download (1 MiB).
_CHUNK_SIZE = 1 << 20

# Default HTTP GET timeout in seconds.
_DOWNLOAD_TIMEOUT = 300


def build_raw_zip_path(
    file_type: str,
    cycle: int,
    raw_dir: Optional[Path] = None,
) -> Path:
    """Return the canonical local path for a FEC bulk download ZIP.

    Args:
        file_type: FEC file type code (e.g. ``"indiv"``, ``"cn"``).
        cycle:     Election cycle year (e.g. ``2024``).
        raw_dir:   Override for the raw data directory.  Defaults to
                   ``data/raw/`` under the project root.

    Returns:
        ``Path`` of the form ``<raw_dir>/<file_type>_<cycle>.zip``.
    """
    base = Path(raw_dir) if raw_dir is not None else RAW_DIR
    return base / f"{file_type}_{cycle}.zip"


def download_zip(
    url: str,
    dest_path: Path,
    timeout: int = _DOWNLOAD_TIMEOUT,
) -> None:
    """Download a ZIP from *url* and save it to *dest_path*.

    Creates parent directories as needed.  Uses streaming to handle
    large files without loading the whole archive into memory.

    Args:
        url:       Remote URL of the ZIP file.
        dest_path: Destination path (will be created or overwritten).
        timeout:   HTTP GET timeout in seconds.

    Raises:
        requests.HTTPError: If the server returns a non-2xx status.
    """
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Downloading %s -> %s", url, dest_path)
    with requests.get(url, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        with dest_path.open("wb") as fh:
            for chunk in resp.iter_content(chunk_size=_CHUNK_SIZE):
                fh.write(chunk)
    logger.info("Saved %s (%s bytes)", dest_path, dest_path.stat().st_size)


def retain_or_download_zip(
    file_type: str,
    cycle: int,
    url: str,
    changed: bool,
    raw_dir: Optional[Path] = None,
    timeout: int = _DOWNLOAD_TIMEOUT,
) -> tuple[Path, bool]:
    """Return the local ZIP path, downloading only when necessary.

    Retention rule: if the ZIP already exists on disk **and** change
    detection reports the remote file is unchanged (``changed=False``),
    the existing file is reused without a network request.  In every
    other case (missing locally, or remote content changed) the file
    is downloaded and stored.

    Args:
        file_type: FEC file type code.
        cycle:     Election cycle year.
        url:       Remote URL to fetch when a download is required.
        changed:   ``True`` if change detection reports a newer version
                   is available on the FEC server.
        raw_dir:   Override for the raw data directory.
        timeout:   HTTP GET timeout forwarded to :func:`download_zip`.

    Returns:
        ``(zip_path, downloaded)`` where *downloaded* is ``True`` if a
        new file was fetched, ``False`` if the retained copy was reused.
    """
    zip_path = build_raw_zip_path(file_type, cycle, raw_dir)

    if zip_path.exists() and not changed:
        logger.info("Reusing retained ZIP (unchanged): %s", zip_path)
        return zip_path, False

    download_zip(url, zip_path, timeout=timeout)
    return zip_path, True
