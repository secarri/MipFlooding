# Mip Flooding

[![Sergi Carrion](https://img.shields.io/badge/secarri-open%20source-blueviolet.svg)](https://es.linkedin.com/in/secarri)
[![Sergi Carrion](https://img.shields.io/badge/read-article-blue.svg)](https://www.artstation.com/blogs/se_carri/XOBq/the-god-of-war-texture-optimization-algorithm-mip-flooding)

Python implementation of the "mip flooding" algorithm used in God of War. This algorithm was presented in the 2019 GDC talk and optimizes game textures sizes on disk.

<p align="center">

  <img src="examples/mip_flood_example.gif" width="300" height="300" alt="Texture before and after the mip flooding">

</p>

> "This is fast to generate, and it scales well with the image size, because of the logarithmic component to the algorithmic time complexity, and  on disk, this will compress better, because of those large areas of constant color."
> - GDC. (2019, Sean Feeley). Interactive Wind and Vegetation in “God of War” [Video]. YouTube. https://www.youtube.com/watch?v=MKX45_riWQA

## Prerequisites

-   [Python 3.10](https://www.python.org/downloads/release/python-3100/) or a Digital Content Creation (DCC) application with Python support.
-   The Pillow Python library. You can install it using `pip install Pillow`.

## Installation

1. Download [the latest version from main]((https://github.com/secarri/mip_flooding)) from GitHub!
2. Place the package in your preferred location (whether within your Python libraries or a custom directory, with the option of using `sys.path.append` or any other approach).
3. From your preferred DCC package, import the `image_processing` module form the `mipflooding` package.

## Code sample

```python
import os
import time
from pathlib import Path

from mipflooding import batch_processing, image_processing

main_path = r"C:\Users\Sergi\Desktop\TestFlooding\examples_article"
output_dir = os.path.join(main_path, "output")


def get_files(path, pattern="_C"):
    files = os.listdir(path)
    return [os.path.join(path, file) for file in files if pattern in file]


def batch_mip_flood_slow(files):
    for file in files:
        mask = file.replace("_C", "_A")
        file_name = file.replace("_C", "_MIPF_C")
        output = os.path.join(output_dir, Path(file_name).name.__str__())
        image_processing.run_mip_flooding(file, mask, output)


if __name__ == "__main__":
    start_time = time.perf_counter()
    # batch_mip_flood_slow(get_files(main_path))
    batch_processing.run_batch_mip_flood(get_files(main_path), output_dir)
    end_time = time.perf_counter()
    print(f"Elapsed time: {end_time - start_time:,.2f} sec.")

```
## Statistics

### Single Processing
| Input                       | Old Size Disk | New Size Disk | Percentage Smaller | Elapsed Time |
|-----------------------------|---------------|---------------|--------------------|--------------|
| butterflies_4K_albedo.png   | 9.78 MB       | 6.05 MB       | 38.14%             | 3.13 sec     |
| cloth_4K_albedo.png         | 12.64 MB      | 9.92 MB       | 21.50%             | 3.39 sec     |
| fern_2K_albedo.png          | 2.31 MB       | 1.08 MB       | 53.14%             | 0.57 sec     |
| fern_long_height_albedo.png | 4.79 MB       | 2.18 MB       | 54.54%             | 1.14 sec     |
| flowers_4K_albedo.png       | 9.30 MB       | 6.14 MB       | 34.03%             | 3.01 sec     |
| leafs_4K_albedo.png         | 8.48 MB       | 7.52 MB       | 11.29%             | 3.77 sec     |
| purple_flower_4K_albedo.png | 16.98 MB      | 13.57 MB      | 20.09%             | 2.90 sec     |
| rocks_4K_albedo.png         | 2.78 MB       | 2.32 MB       | 16.57%             | 2.34 sec     |
| **Average**                 |               |               | 31.16%             | 2.50 sec     |

### Batch Processing

| Same set of files above | Elapsed Time |
|-------------------------|--------------|
| Synchronous calls       | 25.34 sec    |
| Asynchronous calls      | 5.97 sec     |

## What's next?

* Release a version with its own setup installer. 
* Support for Packed Textures with Alpha Channel.
* Selective Mip Flooding for Specific Channels.
