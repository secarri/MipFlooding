import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

from mipflooding import file_utils, image_processing
from .logger import log_execution_time, setup_logger, terminate_loggers


def _mip_flooding_task(file: str, mask: str, output: str) -> None:
    """Function to run the mip flooding algorithm on a single file, used as a task for the ThreadPoolExecutor."""
    image_processing.run_mip_flooding(file, mask, output)


def run_batch_mip_flood(files: List[str],
                        output_dir: str,
                        input_color_pattern: str = "_C",
                        input_mask_pattern: str = "_A",
                        output_pattern: str = "_C",
                        max_workers: int = 4) -> None:
    """Function to process all relevant files in parallel."""
    out_log_file = Path(os.path.join(output_dir, 'batch_mipmap_flooding.txt'))
    file_utils.clear_log_file(out_log_file)
    batch_logger = setup_logger('batch_mipmap_flooding', out_log_file.__str__())
    batch_logger.info(f"- Maximum number of threads that can be used to execute the given calls set to: {max_workers}")

    @log_execution_time
    def _run_batch_mip_flood(logger) -> None:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for file in files:
                mask = file.replace(input_color_pattern, input_mask_pattern)
                file_name = file.replace(input_color_pattern, output_pattern)
                output = os.path.join(output_dir, Path(file_name).name)
                logger.info(f"--- Submitting mip flooding task to thread pool: {Path(file).name}")
                futures.append(executor.submit(_mip_flooding_task, file, mask, output))
            logger.info("- Waiting for results to complete...")
            for future in futures:
                future.result()
            logger.info(f"--- Done.")

    _run_batch_mip_flood(logger=batch_logger)
    terminate_loggers(batch_logger)
