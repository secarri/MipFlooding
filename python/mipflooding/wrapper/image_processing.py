from ..bin.loader import mip_flooding
from . import image_format as imgf


def run_mip_flooding(
    color_path: str,
    mask_path: str,
    output_path: str,
    img_format: str = imgf.ImageFormat.PNG,
    recomposite_mip0: bool = True,
) -> None:
    """
    Perform Mipmap Flooding on input color and mask textures to optimize for disk storage.

    Args:
        color_path: The absolute path to the color texture image.
        mask_path: The absolute path to the mask texture image.
        output_path: The absolute path for the output image.
        img_format: The image format of the output image, use ImageFormat to call supported formats.
        recomposite_mip0: If True (default), composite the original Mip0 color back on top
            of the mip-flooded result to preserve full texture fidelity in opaque regions.

    Example:
        run_mip_flooding('input_color.png', 'input_mask.png', 'output_texture.png', ImageFormat.PNG)
    """
    mip_flooding.RunMipFlooding(color_path, mask_path, output_path, img_format, recomposite_mip0)

