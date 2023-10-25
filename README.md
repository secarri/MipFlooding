# Mip Flooding

[![Sergi Carrion](https://img.shields.io/badge/secarri-open%20source-blueviolet.svg)](https://es.linkedin.com/in/secarri)

Python implementation of the "mip flooding" algorithm used in God of War. This algorithm was presented in the 2019 GDC talk and optimizes game textures sizes on disk.

<p align="center">
  <img src="examples/example.gif" width="150" height="115" alt="Texture before and after the mip flooding">
</p>

> "This is fast to generate, and it scales well with the image size, because of the logarithmic component to the algorithmic time complexity, and  on disk, this will compress better, because of those large areas of constant color."
> - GDC. (2019, Sean Feeley). Interactive Wind and Vegetation in “God of War” [Video]. YouTube. https://www.youtube.com/watch?v=MKX45_riWQA

## Prerequisites

-   [Python 3.10](https://www.python.org/downloads/release/python-3100/) or a Digital Content Creation (DCC) application with Python support.

## Installation

1. Download [the latest release]([https://github.com/EmbarkStudios/blender-tools/releases/latest](https://github.com/secarri/mip_flooding/releases)) from Github!
2. Place the package in your preferred location (whether within your Python libraries or a custom directory, with the option of using `sys.path.append` or any other approach).
3. From your preferred DCC package, import the `image_processing` package.

## Code sample

```python
print("The code will go here!")
```
## Statistics

| Input                      | Old Size Disk | New Size Disk | Percentage Smaller | Elapsed Time |
| --------------------------  | ------------ | ------------- | ------------------- | ------------ |
| butterflies_4K_albedo.png  | 9.78 MB      | 6.03 MB       | 38.29%             | 3.13s        |
| cloth_4K_albedo.png        | 12.64 MB     | 9.89 MB       | 21.77%             | 3.39s        |
| fern_2K_albedo.png         | 2.31 MB      | 1.07 MB       | 53.68%             | 0.57s        |
| fern_long_height_albedo.png| 4.79 MB      | 2.14 MB       | 55.30%             | 1.14s        |
| flowers_4K_albedo.png      | 9.30 MB      | 6.03 MB       | 35.24%             | 3.01s        |
| leafs_4K_albedo.png        | 8.48 MB      | 7.46 MB       | 12.03%             | 3.77s        |
| purple_flower_4K_albedo.png| 16.98 MB     | 13.54 MB      | 20.25%             | 2.90s        |
| rocks_4K_albedo.png        | 2.78 MB      | 2.30 MB       | 17.06%             | 2.34s        |
| **Average**                |              |               | 31.705%            | 2.5s         |

