# Default packages
import logging
import math
import os
import time
from pathlib import Path
from typing import List, Optional

# Third party packages
from PIL import Image

# From self package
from .logger import setup_logger, terminate_loggers
from .file_utils import clear_log_file, get_output_directory, get_output_filename


def _open_image_inputs(color: str, alpha: str, logger: logging.Logger) -> List:
    """Open and return the color and alpha images as a list of Image objects."""
    logger.info("--- Opening images in memory...")
    if not color:
        color = str(None)
    if not alpha:
        alpha = str(None)
    color_map = None if not Path(color).exists() else Image.open(color)
    alpha_mask = None if not Path(alpha).exists() else Image.open(alpha).convert('L')
    if color_map:
        logger.info(f"--- File disk size: {os.path.getsize(color) / float(1 << 20):,.2f} MB")
    return [color_map, alpha_mask]


def _validate_inputs(color: Image, alpha_mask: Image, logger: logging.Logger,
                     input_texture_color_abs_path: str) -> str | Optional[None]:
    if color is None or alpha_mask is None:
        message = f"One or more inputs do not exist:\n\t-Color: {color}\n\t-Alpha: {alpha_mask}. Skipping..."
    elif not _do_resolutions_match(color, alpha_mask, logger):
        message = f"Inputs do not match in resolution for file: {input_texture_color_abs_path}. Skipping..."
    elif not _is_power_of_two_image(color, logger):
        message = f"Input is not a power of two image: {input_texture_color_abs_path}. Skipping..."
    else:
        message = None
    return message


def _do_resolutions_match(color: Image, alpha: Image, logger: logging.Logger) -> bool:
    """Check if the resolutions of color and alpha images match."""
    logger.info("--- Verifying that inputs resolutions do match ...")
    return True if color.size == alpha.size else False


def _is_power_of_two_image(color: Image, logger: logging.Logger) -> bool:
    """Check if all dimensions of the input image are powers of two."""
    logger.info("--- Verifying that inputs are power of two images ...")
    for res in color.size:
        if (res & (res - 1)) != 0:
            return False
    return True


def _get_mip_levels(image: Image, logger: logging.Logger) -> int:
    """Calculate the number of mip levels based on image size."""
    logger.info("--- Calculating mip map levels...")
    image_short_side = image.size[0] if image.size[0] < image.size[1] else image.size[1]
    logger.info(f"--- Done. Miplevels: {round(math.log2(image_short_side))}")
    return round(math.log2(image_short_side))


def _generate_background(image: Image, logger: logging.Logger) -> Image:
    """Generate a background image and returns the result Image object."""
    logger.info("--- Generating background image and storing it in memory...")
    average_image_color = image.resize((1, 1))
    up_scaled_avg = average_image_color.resize(image.size, Image.NEAREST)
    return up_scaled_avg


def _calculate_image_height(image_width: int, image: Image) -> int:
    """Calculate the height of the image based on the specified width."""
    width_percent = (image_width / float(image.size[0]))
    new_height = int((float(image.size[1]) * float(width_percent)))
    return new_height


def _stack_mip_levels(average_bgr: str, miplevels: int, color: Image, origin_width: int, origin_height: int,
                      output_dir: str, logger: logging.Logger, resample: Image.Resampling = Image.BOX) -> None:
    """Stack Mipmap levels on a background Image with alpha integration to generate a single Image."""
    stack = average_bgr
    logger.info(f"--- Storing original resolution in memory: {origin_width, origin_height}")
    logger.info(f"--- Beginning the stacking process. Please wait...")
    for miplevel in range(miplevels):
        width = 2 ** (miplevel + 1)
        height = _calculate_image_height(width, color)
        new_image = color.resize((width, height), resample)
        to_stack = new_image.copy().resize((origin_width, origin_height), Image.NEAREST)
        img_copy = stack.copy()
        img_copy.paste(to_stack, (0, 0), to_stack)
        stack = img_copy.copy()
    logger.info(f"--- Saving stack to file: {output_dir}")
    stack.save(output_dir)
    logger.info(f"--- Output disk size: {os.path.getsize(output_dir) / float(1 << 20):,.2f} MB")


def _log_and_terminate(logger, message, level=logging.ERROR):
    """Log the given 'message' at the specified 'level' using the 'logger', and then terminate the logger."""
    logger.log(level=level, msg=message)
    terminate_loggers(logger)


def _make_logger_for_file(directory: str, filename: str) -> logging.Logger:
    """Constructs the full path to a log file, clears the existing log file, and sets up a logger."""
    logs_directory = os.path.join(directory, "logs")
    Path(logs_directory).mkdir(parents=True, exist_ok=True)
    out_log_file = Path(os.path.join(logs_directory, f"{filename.split('.')[0]}.txt"))
    clear_log_file(out_log_file)
    return setup_logger("mipmap_flooding", out_log_file.__str__())


def run_mip_flooding(in_texture_color_abs_path: str, in_texture_alpha_abs_path: str, out_abs_path: str) -> None:
    """
    Perform Mipmap Flooding on input color and alpha textures to optimize for disk storage.

    This function processes a pair of input textures (color and alpha). It generates Mipmap levels, starting from the
    original resolution and gradually downsizing to a 1x1 Mipmap. The function then assembles these Mipmaps, layer by
    layer, reintegrating the alpha channel, until it reaches the original resolution.

    Args:
        in_texture_color_abs_path (str): The absolute path to the color texture image.
        in_texture_alpha_abs_path (str): The absolute path to the alpha texture image.
        out_abs_path (str): The absolute path for the output image.

    Example:
        run_mip_flooding('input_color.png', 'input_alpha.png', 'output_texture.png')
    """
    start_time = time.perf_counter()
    out_directory = get_output_directory(out_abs_path)
    out_filename = get_output_filename(out_abs_path)
    if out_directory is None:
        logging.error("Specified output directory does not exist. Skipping...")
        return
    logger = _make_logger_for_file(out_directory, out_filename)
    logger.info("- Start image processing...")
    color, alpha_mask = _open_image_inputs(in_texture_color_abs_path, in_texture_alpha_abs_path, logger)
    validation_log = _validate_inputs(color, alpha_mask, logger, in_texture_color_abs_path)
    if validation_log is not None:
        _log_and_terminate(logger, validation_log)
        return
    miplevels = _get_mip_levels(color, logger)
    average_bgr = _generate_background(color, logger)
    color.putalpha(alpha_mask)
    _stack_mip_levels(average_bgr, miplevels, color, color.size[0], color.size[1], out_abs_path, logger)
    optimized_percentage = os.path.getsize(in_texture_color_abs_path) - os.path.getsize(out_abs_path)
    optimized_percentage = optimized_percentage * 100 / os.path.getsize(in_texture_color_abs_path)
    logger.info(f"--- Final image is {optimized_percentage:,.2f}% smaller in disk.")
    _log_and_terminate(logger, f"- Elapsed time: {time.perf_counter() - start_time} seconds.", logging.INFO)
