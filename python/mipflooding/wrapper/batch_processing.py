import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

from . import image_processing

logger = logging.getLogger(__name__)


def _match_mask(image_path: str, color_name_pattern: str, mask_name_pattern: str) -> str | None:
    mask_path = image_path.replace(color_name_pattern, mask_name_pattern)
    return mask_path if Path(mask_path).exists() else None


def _mip_flooding_task(file: str, mask: str, output: str) -> None:
    """Run the mip flooding algorithm on a single file."""
    img_fmt = Path(output).suffix.lstrip(".").lower()
    image_processing.run_mip_flooding(file, mask, output, img_format=img_fmt)


def run_batch_mip_flood(
    files: List[str],
    output_dir: str,
    input_color_pattern: str = "_C",
    input_mask_pattern: str = "_A",
    output_pattern: str = "_C",
    max_workers: int | None = None,
) -> List[str]:
    """Process all relevant files in parallel using mip flooding.

    Returns:
        A list of error messages for any files that failed to process.
        An empty list means all files succeeded.
    """
    errors: List[str] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {}
        for file in files:
            mask = _match_mask(file, input_color_pattern, input_mask_pattern)
            if mask is None:
                logger.warning("No mask found for %s — skipping.", file)
                continue
            file_name = file.replace(input_color_pattern, output_pattern)
            output = os.path.join(output_dir, Path(file_name).name)
            future = executor.submit(_mip_flooding_task, file, mask, output)
            future_to_file[future] = file

        for future in as_completed(future_to_file):
            source_file = future_to_file[future]
            try:
                future.result()
            except Exception as e:
                error_msg = f"Failed to process {source_file}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

    return errors
