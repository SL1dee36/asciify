# Asciify: Your Video and Image to ASCII Art Converter

Asciify is a Python library designed to transform your images and videos into unique, text-based ASCII art representations.  It's a simple yet powerful tool for adding a retro touch to your multimedia content.

## Features

- **Versatile Conversion:**  Convert both images and videos to ASCII art.
- **Supported Formats:**
    - **Video:**  MP4, AVI
    - **Image:** JPG, JPEG, PNG
- **Customization:**
    - **Color Levels:**  Adjust the number of color levels for a richer or simpler aesthetic.
    - **Font Size:**  Control the level of detail with different font sizes.
    - **Resolution:** Resize the output video or image to your desired dimensions.
    - **Frame Rate:** Adjust the frame rate of output videos.
- **Progress Tracking:**  The library provides console output displaying the conversion progress, percentage complete, and current/total frame/image count.
- **Easy to Use:**  Simple function calls make it easy to convert your files.

## Installation

```bash
pip install opencv-python numpy pygame numba
```

## Usage

### Basic Usage

```python
from asciify import acsiify_wrapper

# Convert a video to ASCII video art
acsiify_wrapper('video', video='input_video.mp4', output_path='output_video.avi') 

# Convert an image to ASCII art
acsiify_wrapper('image', image='input_image.jpg', output_path='output_image.png') 
```

**Before/After (color_lvl=32):**

![image](https://github.com/user-attachments/assets/256e053c-c3f3-4763-985e-4fa37d8bde41)

### Advanced Usage

Utilize the available parameters for finer control over the conversion process:

**Video Conversion Parameters:**

- `video_path` (str): Path to the input video file (required).
- `color_lvl` (int, optional): Number of color levels (default: 32).
- `pixel_size` (int, optional): Font size (default: 12).
- `output_path` (str, optional): Path to the output video file (default: 'ascii_col.avi').
- `geometry` (str, optional): 'WIDTHxHEIGHT' to resize the output video (default: None - uses source video resolution).
- `output_fps` (int, optional): Frame rate of the output video (default: None - uses source video frame rate).

**Image Conversion Parameters:**

- `image_path` (str): Path to the input image file (required).
- `color_lvl` (int, optional): Number of color levels (default: 32).
- `pixel_size` (int, optional): Font size (default: 12).
- `output_path` (str, optional): Path to the output image file (default: None - uses the input image's path with "_ascii" appended).
- `geometry` (str, optional): 'WIDTHxHEIGHT' to resize the output image (default: None - uses source image resolution).

**Example with Custom Resolution and Frame Rate:**

```python
from asciify import acsiify_wrapper

acsiify_wrapper('video', video='my_video.mp4', output_path='my_ascii_video.avi', geometry='640x360', output_fps=24)

# OR
from asciify import *

# Convert an image to ASCII art
acsiify.image("input.jpg", output_path="output32.jpg", color_lvl=32, pixel_size=10)

# Convert a video to ASCII video art
acsiify.video("input.mp4", output_path="output32.mp4", color_lvl=32, pixel_size=10, output_fps=60)

```

## API Reference

**`acsiify_wrapper(obj_type, **kwargs)`**

- **Parameters:**
    - `obj_type` (str):  Must be either 'video' or 'image' to indicate the type of object to convert.
    - `**kwargs`: Keyword arguments specific to the object type (video or image). See the parameter lists above for details.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on the GitHub repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Pygame
- OpenCV
- NumPy
- Numba
