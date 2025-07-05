import pygame

class BF16graphic:
    WIDTH = 16
    HEIGHT = 16
    PIXEL_SCALE = 32  # 16 * 32 = 512

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def clear(self):
        self.screen.fill((0, 0, 0))
        self.update()

    def draw_grid(self, color=(40, 40, 40)):
        for x in range(self.WIDTH):
            pygame.draw.line(
                self.screen,
                color,
                (x * self.PIXEL_SCALE, 0),
                (x * self.PIXEL_SCALE, self.HEIGHT * self.PIXEL_SCALE),
            )
        for y in range(self.HEIGHT):
            pygame.draw.line(
                self.screen,
                color,
                (0, y * self.PIXEL_SCALE),
                (self.WIDTH * self.PIXEL_SCALE, y * self.PIXEL_SCALE),
            )

    def draw_box(self, x, y, width, height, color=(255, 255, 255)):
        pygame.draw.rect(self.screen, color, (x, y, width, height))

    def draw_text(self, text: str, x: int, y: int, color=(255, 255, 255), font_size=18):
        font = pygame.font.SysFont("Arial", font_size)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def draw_line(self, x1, y1, x2, y2, color=(255, 255, 255), width=1):
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), width)

    def update(self):
        pygame.display.flip()

    class THREED:
        def draw_cube(self, screen, x, y, z, size, color=(255, 255, 255)):
            iso_x = (x - z) * 0.707 + self.WIDTH * self.PIXEL_SCALE / 2
            iso_y = (y + z) * 0.707 + self.HEIGHT * self.PIXEL_SCALE / 2
            pygame.draw.rect(screen, color, (iso_x, iso_y, size, size), 2)
