import pygame

class bf16graphic:
    WIDTH = 16
    HEIGHT = 16
    PIXEL_SCALE = 32  # 16x32 = 512 window
    _INIT = False
    _screen = None
    _surface = None

    @staticmethod
    def init():
        if not bf16graphic._INIT:
            pygame.init()
            bf16graphic._screen = pygame.display.set_mode(
                (bf16graphic.WIDTH * bf16graphic.PIXEL_SCALE, bf16graphic.HEIGHT * bf16graphic.PIXEL_SCALE)
            )
            bf16graphic._surface = pygame.Surface((bf16graphic.WIDTH, bf16graphic.HEIGHT))
            pygame.display.set_caption("BF16 Graphics")
            bf16graphic._INIT = True

    @staticmethod
    def draw_pixels(memory: list[int], color_func: callable):
        """Draw 16x16 pixels from memory[0..255] using a color function."""
        bf16graphic.init()
        for y in range(bf16graphic.HEIGHT):
            for x in range(bf16graphic.WIDTH):
                i = y * bf16graphic.WIDTH + x
                val = memory[i]
                color = color_func(val)
                rect = pygame.Rect(
                    x * bf16graphic.PIXEL_SCALE,
                    y * bf16graphic.PIXEL_SCALE,
                    bf16graphic.PIXEL_SCALE,
                    bf16graphic.PIXEL_SCALE,
                )
                pygame.draw.rect(bf16graphic._screen, color, rect)

        pygame.display.flip()

    @staticmethod
    def clear():
        bf16graphic.init()
        bf16graphic._screen.fill((0, 0, 0))
        pygame.display.flip()

    @staticmethod
    def draw_grid(color=(40, 40, 40)):
        bf16graphic.init()
        for x in range(bf16graphic.WIDTH):
            pygame.draw.line(
                bf16graphic._screen,
                color,
                (x * bf16graphic.PIXEL_SCALE, 0),
                (x * bf16graphic.PIXEL_SCALE, bf16graphic.HEIGHT * bf16graphic.PIXEL_SCALE),
            )
        for y in range(bf16graphic.HEIGHT):
            pygame.draw.line(
                bf16graphic._screen,
                color,
                (0, y * bf16graphic.PIXEL_SCALE),
                (bf16graphic.WIDTH * bf16graphic.PIXEL_SCALE, y * bf16graphic.PIXEL_SCALE),
            )
        pygame.display.flip()

    @staticmethod
    def draw_text(text: str, x: int, y: int, color=(255, 255, 255), font_size=18):
        bf16graphic.init()
        font = pygame.font.SysFont("Arial", font_size)
        text_surface = font.render(text, True, color)
        bf16graphic._screen.blit(text_surface, (x, y))
        pygame.display.flip()

    @staticmethod
    def update():
        pygame.display.flip()

    @staticmethod
    def close():
        pygame.quit()
        bf16graphic._INIT = False