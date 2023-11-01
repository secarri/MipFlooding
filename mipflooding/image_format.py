from dataclasses import dataclass


@dataclass(frozen=True)
class ImageFormat:
    """
    A class representing various image formats as attributes.
    This class can be used to access standardized strings representing
    image formats, which can be used for image processing, loading,
    saving, or any related tasks.

    Attributes:
    BMP (str): Bitmap image file format.
    GIF (str): Graphics Interchange Format, a bitmap image format.
    ICO (str): Icon format used in Microsoft Windows.
    JPEG (str): Joint Photographic Experts Group, a commonly used method of lossy compression for digital images.
    PNG (str): Portable Network Graphics, a raster-graphics file-format that supports lossless data compression.
    TGA (str): Truevision TGA (TARGA), a raster graphics file format.
    TIFF (str): Tagged Image File Format, a file format for storing raster graphics images.
    PSD (str): Photoshop Document, Adobe Photoshop's native file format.
    Default (None): An attribute to handle unspecified or unknown formats.
    """
    BMP: str = "BMP"
    GIF: str = "GIF"
    ICO: str = "ICO"
    JPEG: str = "JPEG"
    PNG: str = "PNG"
    TGA: str = "TGA"
    TIFF: str = "TIFF"
    PSD: str = "PSD"
    Default: None = None
