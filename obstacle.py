import pygame


class Block(pygame.sprite.Sprite):
    def __init__(self, size, color, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

shape_planet = [
    '   xxxx   ',
    '  xxxxxx  ',
    ' xxxxxxxx ',
    'xxxxxxxxxx',
    ' xxxxxxxx ',
    '  xxxxxx  ',
    '   xxxx   '
]

shape_moon = [
    '     xxxxx',
    '   xxxxx  ',
    ' xxxxx    ',
    'xxxxxx    ',
    ' xxxxx    ',
    '   xxxxx  ',
    '     xxxxx'
]

shape_star = [
    '    xx    ',
    '   xxxx   ',
    'xxxxxxxxxx',
    '  xxxxxx  ',
    ' xxxxxxxx ',
    'xxxx  xxxx',
    'xx      xx'
]
