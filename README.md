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

> *Last updated: 2026-02-14*

> **Note:** These statistics were generated on a Windows 11 machine (Intel Core i7-13700K, 32GB RAM). Benchmarks are automatically updated with each change, so the values below may differ from the examples shown in the GIFs. Test images are sourced from [Poly Haven](https://polyhaven.com/models/nature) and [Fab](https://www.fab.com/sellers/Quixel%20Megascans).

### Single Processing
| Input                       | Old Size Disk | New Size Disk | Percentage Smaller | Elapsed Time |
|-----------------------------|---------------|---------------|--------------------|--------------|
| T_Chair_C.PNG | 2.52 MB | 1.77 MB | 29.86% | 0.61 sec |
| T_butterflies_C.png | 10.26 MB | 9.89 MB | 3.66% | 2.26 sec |
| T_fern_C.jpg | 1.97 MB | 1.46 MB | 25.90% | 2.33 sec |
| T_peri_C.png | 52.18 MB | 12.69 MB | 75.67% | 3.01 sec |
| T_potted_C.png | 59.03 MB | 28.72 MB | 51.35% | 3.14 sec |
| **Average** | | | 37.29% | 2.27 sec |

### Batch Processing

| Same set of files above | Elapsed Time |
|-------------------------|--------------|
| Synchronous calls       | 12.34 sec    |
| Asynchronous calls      | 8.85 sec     |

<p align="center">

  <img src="docs/examples/batch_example.gif" width="700" alt="Texture before and after the mip flooding">

</p>

## What's next?
 
* Support for Packed Textures with Alpha Channel.