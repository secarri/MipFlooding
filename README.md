# Mip Flooding

[![Sergi Carrion](https://img.shields.io/badge/secarri-open%20source-blueviolet.svg)](https://es.linkedin.com/in/secarri)
[![Sergi Carrion](https://img.shields.io/badge/read-article-blue.svg)](https://www.artstation.com/blogs/se_carri/XOBq/the-god-of-war-texture-optimization-algorithm-mip-flooding)

C# and Python implementation of the "mip flooding" algorithm used in God of War. This algorithm was presented in the 2019 GDC talk and optimizes game textures sizes on disk.

The C# ImageProcessingLibrary is called from Python, making it easily accessible from any DCC package that supports Python.
<p align="center">

  <img src="docs/examples/mip_flood_example.gif" width="300" height="300" alt="Texture before and after the mip flooding">

</p>

> "This is fast to generate, and it scales well with the image size, because of the logarithmic component to the algorithmic time complexity, and  on disk, this will compress better, because of those large areas of constant color."
> - GDC. (2019, Sean Feeley). Interactive Wind and Vegetation in “God of War” [Youtube Video](https://www.youtube.com/watch?v=MKX45_riWQA).

## Prerequisites

-   Any version of Python that has `pythonnet` installed or a Digital Content Creation (DCC) application with Python support.
-   The `pythonnet` Python library. You can install it using `pip install pythonnet`.

## Installation

1. Visit the [latest release page](https://github.com/secarri/MipFlooding/releases)!
2. Download the `mipflooding.zip` package from the bottom of the release page.
3. Unzip the `mipflooding.zip` file and place the `mipflooding` package in your preferred location. You can either add it to your Python libraries or place it in a custom directory and update your `sys.path` accordingly.
4. From your preferred DCC package, import the `image_processing` module form the `wrapper` package.

## Code sample

```python
import os
import time
from pathlib import Path

from mipflooding.wrapper import image_processing
from mipflooding.wrapper import batch_processing

# Variables for single thread test
wrapper_path = Path(__file__).parent
color = wrapper_path / "src" / "MipFlooding" / "tests" / "book_debri_tall_C.png"
mask = wrapper_path / "src" / "MipFlooding" / "tests" / "book_debri_tall_A.png"
out = wrapper_path / "src" / "MipFlooding" / "tests" / "outs" / "output_bug.png"

# Variables for multi thread test
directory = wrapper_path / "src" / "MipFlooding" / "tests"
output_dir = wrapper_path / "src" / "MipFlooding" / "tests" / "outs"


def get_files(path, pattern="_C"):
    files = os.listdir(path)
    return [os.path.join(path, file) for file in files if pattern in file]


def run_single_test():
    start_time = time.perf_counter()
    image_processing.run_mip_flooding(str(color), str(mask), str(out))
    end_time = time.perf_counter()
    print(f"Single thread time: {end_time - start_time:,.2f} sec.")


def run_multi_test():
    start_time = time.perf_counter()
    batch_processing.run_batch_mip_flood(files=get_files(directory), output_dir=output_dir, max_workers=4)
    end_time = time.perf_counter()
    print(f"Multi thread time: {end_time - start_time:,.2f} sec.")


if __name__ == "__main__":
    # Single Thread Mip Flooding
    run_single_test()
    # Multi Thread Mip Flooding
    run_multi_test()


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

<p align="center">

  <img src="docs/examples/batch_example.gif" width="700" alt="Texture before and after the mip flooding">

</p>

## What's next?
 
* Support for Packed Textures with Alpha Channel.
