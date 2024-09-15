import pygame as pg
import numpy as np
from numba import njit
import cv2

@njit(fastmath=True)
def accelerate_conversion(image, gray_image, width, height, color_coeff, ascii_coeff, step):
    array_of_values = []
    for x in range(0, width, step):
        for y in range(0, height, step):
            char_index = gray_image[x, y] // ascii_coeff
            if char_index:
                r, g, b = image[x, y] // color_coeff
                array_of_values.append((char_index, (r, g, b), (x, y)))
    return array_of_values

class ArtConverter:
    def __init__(self, path='output.mp4', font_size=12, color_lvl=32):
        pg.init()
        self.path = path
        self.capture = cv2.VideoCapture(path)
        self.COLOR_LVL = color_lvl
        self.image, self.gray_image = self.get_image()
        self.RES = self.WIDTH, self.HEIGHT = self.image.shape[0], self.image.shape[1]
        # self.surface = pg.display.set_mode(self.RES)  # Убираем отображение в окне Pygame
        self.clock = pg.time.Clock()

        self.ASCII_CHARS = ' ixzao*#MW&8%B@$'
        self.ASCII_COEFF = 255 // (len(self.ASCII_CHARS) - 1)

        self.font = pg.font.SysFont('Сourier', font_size, bold=True)
        self.CHAR_STEP = int(font_size * 0.6)
        self.PALETTE, self.COLOR_COEFF = self.create_palette()

        self.rec_fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.record = True  # Включаем запись сразу
        self.recorder = cv2.VideoWriter('ascii_col.mp4', cv2.VideoWriter_fourcc(*'mp4v'), self.rec_fps, (2560, 1440))

    def get_frame(self):
        # Создаем временную поверхность для рендеринга
        temp_surface = pg.Surface((2560, 1440)) 
        temp_surface.fill('black')
        self.draw_converted_image(temp_surface)
        frame = pg.surfarray.array3d(temp_surface)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return cv2.transpose(frame)

    def draw_converted_image(self, surface):  # Добавляем поверхность в параметр
        image, gray_image = self.get_image()
        array_of_values = accelerate_conversion(image, gray_image, self.WIDTH, self.HEIGHT,
                                                self.COLOR_COEFF, self.ASCII_COEFF, self.CHAR_STEP)
        for char_index, color, pos in array_of_values:
                char = self.ASCII_CHARS[char_index]
                surface.blit(self.PALETTE[char][color], pos)

    def create_palette(self):
        colors, color_coeff = np.linspace(0, 255, num=self.COLOR_LVL, dtype=int, retstep=True)
        color_palette = [np.array([r, g, b]) for r in colors for g in colors for b in colors]
        palette = dict.fromkeys(self.ASCII_CHARS, None)
        color_coeff = int(color_coeff)
        for char in palette:
            char_palette = {}
            for color in color_palette:
                color_key = tuple(color // color_coeff)
                char_palette[color_key] = self.font.render(char, False, tuple(color))
            palette[char] = char_palette
        return palette, color_coeff

    def get_image(self):
        # self.cv2_image = cv2.imread(self.path)
        ret, self.cv2_image = self.capture.read()
        if not ret:
            exit()
        transposed_image = cv2.transpose(self.cv2_image)
        image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2RGB)
        gray_image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2GRAY)
        return image, gray_image

    def draw_cv2_image(self):
        resized_cv2_image = cv2.resize(self.cv2_image, (640, 360), interpolation=cv2.INTER_AREA)
        cv2.imshow('img', resized_cv2_image)

    def draw(self):
        self.surface.fill('black')
        self.draw_converted_image()
        # self.draw_cv2_image()

    def save_image(self):
        pygame_image = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite('output/ascii_col_image.jpg', cv2_img)

    def record_frame(self):
        if self.record:
            frame = self.get_frame()
            self.recorder.write(frame)


    def run(self):
        total_frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        current_frame = 0
        while True:
            # Убираем обработку событий Pygame
            #for i in pg.event.get(): 
            #    if i.type == pg.QUIT:
            #        exit()
            #    elif i.type == pg.KEYDOWN:
            #        if i.key == pg.K_s:
            #            self.save_image()
            #        if i.key == pg.K_r:
            #            self.record = not self.record

            if not self.capture.isOpened():
                break

            self.record_frame()  # Записываем каждый кадр
            current_frame += 1

            # Вывод процента выполнения в консоль
            percent_complete = (current_frame / total_frames) * 100
            print(f"\r{self.path} - {percent_complete:.2f}% | {current_frame} from {total_frames}", end="")

            #pg.display.set_caption(f"FPS: {self.clock.get_fps():.2f}") # Убираем вывод в заголовок окна
            #pg.display.flip()
            self.clock.tick()

        # Завершаем запись и освобождаем ресурсы
        self.recorder.release()
        self.capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    app = ArtConverter()
    app.run() 