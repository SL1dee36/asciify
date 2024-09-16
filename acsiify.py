import pygame as pg
import numpy as np
from numba import njit
import cv2
import os


@njit(fastmath=True)
def _accelerate_conversion(image, gray_image, width, height, color_coeff, ascii_coeff, step):
    array_of_values = []
    for x in range(0, width, step):
        for y in range(0, height, step):
            char_index = gray_image[x, y] // ascii_coeff
            if char_index:
                r, g, b = image[x, y] // color_coeff
                array_of_values.append((char_index, (r, g, b), (x, y)))
    return array_of_values

def _create_palette(font, ascii_chars, color_lvl):
    colors, color_coeff = np.linspace(0, 255, num=color_lvl, dtype=int, retstep=True)
    color_palette = [np.array([r, g, b]) for r in colors for g in colors for b in colors]
    palette = dict.fromkeys(ascii_chars, None)
    color_coeff = int(color_coeff)
    for char in palette:
        char_palette = {}
        for color in color_palette:
            color_key = tuple(color // color_coeff)
            char_palette[color_key] = font.render(char, False, tuple(color))
        palette[char] = char_palette
    return palette, color_coeff

def _draw_converted_image(surface, image, gray_image, palette, ascii_chars, ascii_coeff, color_coeff, char_step):
    width, height = image.shape[0], image.shape[1]
    array_of_values = _accelerate_conversion(image, gray_image, width, height, color_coeff, ascii_coeff, char_step)
    for char_index, color, pos in array_of_values:
        char = ascii_chars[char_index]
        surface.blit(palette[char][color], pos)

def _get_image(path, capture):
    if path:
        cv2_image = cv2.imread(path)
    else:
        ret, cv2_image = capture.read()
        if not ret:
            exit()
    transposed_image = cv2.transpose(cv2_image)
    image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2RGB)
    gray_image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2GRAY)
    return image, gray_image

def _save_image(surface, output):
    if output:
        pygame_image = pg.surfarray.array3d(surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)

        # Determine the output format based on the file extension
        _, ext = os.path.splitext(output)
        ext = ext.lower()  # Normalize extension to lowercase

        if ext in ('.jpg', '.jpeg'):
            cv2.imwrite(output, cv2_img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])  # JPEG compression
        elif ext in ('.png'):
            cv2.imwrite(output, cv2_img, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])  # PNG compression
        elif ext in ('.gif'):
            # GIF saving typically requires specialized libraries like Pillow
            # Consider adding a GIF saving logic here if you need it
            raise NotImplementedError("GIF saving is not implemented.")
        else:
            cv2.imwrite(output, cv2_img)

class Asciify:
    def __init__(self):
        pg.init()
        self.ascii_chars = ' ixzao*#MW&8%B@$'
        self.font = pg.font.SysFont('Courier', 12, bold=False)  # Default font size

    def video(self, video_path, color_lvl=32, pixel_size=12, output_path='ascii_col.avi', 
              geometry=None, output_fps=None):
        """
        Converts a video file to ASCII art and saves it as a new video file.

        Args:
            video_path (str): The path to the input video file.
            color_lvl (int, optional): The number of color levels. Defaults to 32.
            pixel_size (int, optional): The size of the font. Defaults to 12.
            output_path (str, optional): The path to the output video file. Defaults to 'ascii_col.avi'.
            geometry (str, optional): 'WIDTHxHEIGHT' for resizing the output video. Defaults to None (uses source video resolution).
            output_fps (int, optional): The frame rate of the output video. Defaults to None (uses source video frame rate).
        """

        ascii_coeff = 255 // (len(self.ascii_chars) - 1)
        char_step = int(pixel_size * 1)

        palette, color_coeff = _create_palette(self.font, self.ascii_chars, color_lvl)

        capture = cv2.VideoCapture(video_path)
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        source_fps = capture.get(cv2.CAP_PROP_FPS)
        source_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        source_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Determine output resolution from geometry or source
        if geometry:
            try:
                output_width, output_height = map(int, geometry.split('x'))
            except ValueError:
                raise ValueError("Invalid geometry format. Use 'WIDTHxHEIGHT'")
        else:
            output_width, output_height = source_width, source_height

        output_fps = output_fps or source_fps

        # Enforce AVI format for XVID
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  
        output_path = output_path if output_path else 'ascii_col.avi'  # Ensure AVI extension

        recorder = cv2.VideoWriter(output_path, fourcc, output_fps, (output_width, output_height))

        current_frame = 0
        while True:
            if not capture.isOpened():
                break

            image, gray_image = _get_image(None, capture)

            # Resize the image to the output resolution
            image = cv2.resize(image, (output_width, output_height), interpolation=cv2.INTER_AREA)
            gray_image = cv2.resize(gray_image, (output_width, output_height), interpolation=cv2.INTER_AREA)

            surface = pg.Surface((output_width, output_height))  # Use output resolution
            surface.fill('black')
            _draw_converted_image(surface, image, gray_image, palette, self.ascii_chars, ascii_coeff, color_coeff, char_step)

            frame = pg.surfarray.array3d(surface)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Remove cv2.transpose here
            recorder.write(frame) 

            current_frame += 1
            percent_complete = (current_frame / total_frames) * 100
            print(f"\r{os.path.basename(video_path)} - {percent_complete:.2f}% | {current_frame}/{total_frames}", end="")

        recorder.release()
        capture.release()
        print("\nVideo conversion complete!")


    def image(self, image_path, color_lvl=32, pixel_size=12, output_path=None, geometry=None):
        """
        Converts an image file to ASCII art and saves it as an image file.

        Args:
            image_path (str): The path to the input image file.
            color_lvl (int, optional): The number of color levels. Defaults to 32.
            pixel_size (int, optional): The size of the font. Defaults to 12.
            output_path (str, optional): The path to the output image file. If None, the output file is named 'ascii_col_image.jpg'.
            geometry (str, optional): 'WIDTHxHEIGHT' for resizing the output image. Defaults to None (uses source image resolution).
        """

        ascii_coeff = 255 // (len(self.ascii_chars) - 1)
        char_step = int(pixel_size * 1)

        palette, color_coeff = _create_palette(self.font, self.ascii_chars, color_lvl)

        image, gray_image = _get_image(image_path, None)

        if not image.any():
            return

        # Determine output resolution from geometry or source
        if geometry:
            try:
                output_width, output_height = map(int, geometry.split('x'))
            except ValueError:
                raise ValueError("Invalid geometry format. Use 'WIDTHxHEIGHT'")
            image = cv2.resize(image, (output_width, output_height), interpolation=cv2.INTER_AREA)
            gray_image = cv2.resize(gray_image, (output_width, output_height), interpolation=cv2.INTER_AREA)
            surface = pg.Surface((output_width, output_height))
        else:
            surface = pg.Surface((image.shape[0], image.shape[1]))

        surface.fill('black')
        _draw_converted_image(surface, image, gray_image, palette, self.ascii_chars, ascii_coeff, color_coeff, char_step)

        if not output_path:
            # Generate a default output path based on input file
            base, ext = os.path.splitext(image_path)
            output_path = base + "_ascii" + (".jpg" if ext.lower() not in ('.png', '.jpg', '.jpeg') else ext)

        _save_image(surface, output_path)
        print(f"\r{os.path.basename(image_path)} - 100% | 1/1", end="")
        print("\nImage conversion complete!")


# Create an instance of the Asciify class
acsiify = Asciify()


def acsiify_wrapper(obj_type=None, **kwargs):
    if obj_type is None:
        raise ValueError("Must provide either 'video' or 'image' keyword argument.")

    if obj_type == 'video':
        video_path = kwargs.pop('video')
        return acsiify.video(video_path, **kwargs)
    elif obj_type == 'image':
        image_path = kwargs.pop('image')
        return acsiify.image(image_path, **kwargs)


acsiify.image("input.jpg",color_lvl=32, output_path='output32.jpg',pixel_size=10) 
acsiify.video("input.mp4", output_path='output.mp4', pixel_size=10, output_fps=60)

acsiify.image("input.jpg",color_lvl=64, output_path='output64.jpg',pixel_size=10) 
acsiify.image("input.jpg",color_lvl=96, output_path='output96.jpg',pixel_size=10) 
acsiify.image("input.jpg",color_lvl=128, output_path='output128.jpg',pixel_size=10) 
acsiify.image("input.jpg",color_lvl=256, output_path='output256.jpg',pixel_size=10) 

#acsiify.video("input.mp4", output_path="output.mp4", geometry="1920x1080", pixel_size=10)