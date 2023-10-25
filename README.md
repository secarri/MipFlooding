# Mip Flooding

[![Sergi Carrion](https://img.shields.io/badge/secarri-open%20source-blueviolet.svg)](https://es.linkedin.com/in/secarri)

Python implementation of the "mip flooding" algorithm used in God of War. This algorithm was presented in the 2019 GDC talk and optimizes game textures sizes on disk.

> "This is fast to generate, and it scales well with the image size, because of the logarithmic component to the algorithmic time complexity, and  on disk, this will compress better, because of those large areas of constant color."
> - GDC. (2019, Sean Feeley). Interactive Wind and Vegetation in “God of War” [Video]. YouTube. https://www.youtube.com/watch?v=MKX45_riWQA

<p align="center">
  <img src="examples/example.gif" width="150" height="115" alt="Texture before and after the mip flooding">
</p>

## Prerequisites

-   [Python 3.10](https://www.python.org/downloads/release/python-3100/) or a Digital Content Creation (DCC) application with Python support.

## Installation

1. Download [the latest release]([https://github.com/EmbarkStudios/blender-tools/releases/latest](https://github.com/secarri/mip_flooding/releases)) from Github!
2. Place the package in your preferred location (whether within your Python libraries or a custom directory, with the option of using `sys.path.append` or any other approach).
3. From your preferred DCC package, importing the image_processing package.

## Code sample

```python
print("The code will go here!")
```
