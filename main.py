import pygame, sys

import obstacle
from player import Player
from alien import Alien, Extra
from random import choice, randint
from laser import Laser


class Game:
    def __init__(self):
        # Gracz
        player_sprite = Player((screen_width / 2, screen_height - 5), screen_width, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        self.lost = False

        # HP i wynik
        self.lives = 3
        self.life = pygame.image.load('graphics/heart.png').convert_alpha()
        self.lives_surface = pygame.transform.scale(self.life, (32, 32)).convert_alpha()
        self.score = 0
        self.highscore = 0
        self.font = pygame.font.Font('fonts/slkscr.ttf', 32)

        # Przeszkody
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.create_block(40, 480, (99, 255, 101), obstacle.shape_planet)
        self.create_block(200, 480, (254, 255, 144), obstacle.shape_moon)
        self.create_block(340, 480, (254, 255, 222), obstacle.shape_star)
        self.create_block(500, 480, (99, 131, 255), obstacle.shape_planet)

        # Kosmici
        self.aliens = pygame.sprite.Group()
        self.aliens_lasers = pygame.sprite.Group()
        self.alien_setup(rows=6, cols=7)
        self.alien_direction = 1

        # Extra Setup
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(500, 700)

        # Muzyka i dzwieki
        music = pygame.mixer.Sound('audio/theme.mp3')
        music.set_volume(0.1)
        music.play(loops=-1)
        self.laser_sound = pygame.mixer.Sound('audio/laser.wav')
        self.laser_sound.set_volume(0.05)
        self.explosion_sound = pygame.mixer.Sound('audio/explosion.wav')
        self.explosion_sound.set_volume(0.02)

        # Tło
        self.background = pygame.image.load('graphics/bg.png')

    def create_block(self, x_start, y_start, color, shape):
        for row_index, row in enumerate(shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size, color, x, y)
                    self.blocks.add(block)

    def alien_setup(self, rows, cols, x_dist=60, y_dist=48, x_offset=70, y_offset=100):
        color = 'red'
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_dist + x_offset
                y = row_index * y_dist + y_offset
                if row_index == 0:
                    color = 'red'
                elif 1 <= row_index <= 2:
                    color = 'green'
                else:
                    color = 'yellow'
                alien_sprite = Alien(color, x, y)
                self.aliens.add(alien_sprite)

    def alien_pos_check(self):
        all_aliens = self.aliens.sprites()
        down = 0
        for alien in all_aliens:
            if alien.rect.right >= screen_width - 10:
                self.alien_direction = -2
                self.alien_down(2)
            elif alien.rect.left <= 10:
                self.alien_direction = 2
                self.alien_down(2)
            if alien.rect.bottom >= screen_height - 10:
                for laser in self.aliens_lasers:
                    laser.kill()
                for alien in self.aliens:
                    alien.kill()
                for extra in self.extra:
                    extra.kill()
                self.lost = True
                self.lives = 0

    def alien_down(self, dist):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += dist

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 4)
            self.aliens_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(('right', 'left'))))
            self.extra_spawn_time = randint(500, 700)

    def collisions_check(self):
        # Player Lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                # alien collisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    laser.kill()
                    for alien in aliens_hit:
                        self.score += alien.value
                    self.explosion_sound.play()
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    laser.kill()
                    self.score += 500
                    self.explosion_sound.play()
        # Alien Lasers
        if self.aliens_lasers:
            for laser in self.aliens_lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                # player collisions
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        self.lost_screen()
        # Aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                if pygame.sprite.spritecollide(alien, self.player, False):
                    for laser in self.aliens_lasers:
                        laser.kill()
                    for alien in self.aliens:
                        alien.kill()
                    for extra in self.extra:
                        extra.kill()
                    self.lost = True
                    self.lives = 0

    def display_lives(self):
        for live in range(self.lives):
            x = (live * 1.2 * self.lives_surface.get_size()[0] + 10)
            screen.blit(self.lives_surface, (x, 15))

    def display_score(self):
        score_surface = self.font.render(f'SCORE: {self.score}', False, 'White')
        score_rect = score_surface.get_rect(topleft=(350, 15))
        screen.blit(score_surface, score_rect)

    def victory_screen(self):
        if not self.aliens.sprites():
            self.check_highscore()
            victory_surface = self.font.render('Victory!', False, 'white')
            victory_rect = victory_surface.get_rect(center=(screen_width / 2, (screen_height / 2) - 20))

            victory_surface_score = self.font.render(f'Your Score: {self.score}', False, 'white')
            victory_rect_score = victory_surface_score.get_rect(midtop=victory_rect.midbottom)

            victory_surface_highscore = self.font.render(f'Highscore: {self.highscore}', False, 'white')
            victory_rect_highscore = victory_surface_highscore.get_rect(midtop=victory_rect_score.midbottom)

            victory_surface_blank = self.font.render(f'  ', False, 'white')
            victory_rect_blank = victory_surface_score.get_rect(midtop=victory_rect_highscore.midbottom)

            victory_surface2 = self.font.render('Press ESC to quit', False, 'white')
            victory_rect2 = victory_surface2.get_rect(midtop=victory_rect_blank.midbottom)

            screen.blit(victory_surface, victory_rect)
            screen.blit(victory_surface2, victory_rect2)
            screen.blit(victory_surface_score, victory_rect_score)
            screen.blit(victory_surface_highscore, victory_rect_highscore)

            if self.extra.sprites():
                self.extra.sprite.kill()
            for laser in self.aliens_lasers:
                laser.kill()

    def lost_screen(self):
        for alien in self.aliens.sprites():
            if alien.rect.y <= 5:
                self.check_highscore()
                victory_surface = self.font.render('You Lost!', False, 'white')
                victory_rect = victory_surface.get_rect(center=(screen_width / 2, (screen_height / 2) - 20))

                victory_surface_score = self.font.render(f'Your Score: {self.score}', False, 'white')
                victory_rect_score = victory_surface_score.get_rect(midtop=victory_rect.midbottom)

                victory_surface_highscore = self.font.render(f'Highscore: {self.highscore}', False, 'white')
                victory_rect_highscore = victory_surface_highscore.get_rect(midtop=victory_rect_score.midbottom)

                victory_surface_blank = self.font.render(f'  ', False, 'white')
                victory_rect_blank = victory_surface_score.get_rect(midtop=victory_rect_highscore.midbottom)

                victory_surface2 = self.font.render('Press ESC to quit', False, 'white')
                victory_rect2 = victory_surface2.get_rect(midtop=victory_rect_blank.midbottom)

                screen.blit(victory_surface, victory_rect)
                screen.blit(victory_surface2, victory_rect2)
                screen.blit(victory_surface_score, victory_rect_score)
                screen.blit(victory_surface_highscore, victory_rect_highscore)

                for laser in self.aliens_lasers:
                    laser.kill()
                for alien in self.aliens:
                    alien.kill()
                for extra in self.extra:
                    extra.kill()
                self.lost = True

        if self.lives <= 0:
            self.check_highscore()
            victory_surface = self.font.render('You Lost!', False, 'white')
            victory_rect = victory_surface.get_rect(center=(screen_width / 2, (screen_height / 2) - 20))

            victory_surface_score = self.font.render(f'Your Score: {self.score}', False, 'white')
            victory_rect_score = victory_surface_score.get_rect(midtop=victory_rect.midbottom)

            victory_surface_highscore = self.font.render(f'Highscore: {self.highscore}', False, 'white')
            victory_rect_highscore = victory_surface_highscore.get_rect(midtop=victory_rect_score.midbottom)

            victory_surface_blank = self.font.render(f'  ', False, 'white')
            victory_rect_blank = victory_surface_score.get_rect(midtop=victory_rect_highscore.midbottom)

            victory_surface2 = self.font.render('Press ESC to quit', False, 'white')
            victory_rect2 = victory_surface2.get_rect(midtop=victory_rect_blank.midbottom)

            screen.blit(victory_surface, victory_rect)
            screen.blit(victory_surface2, victory_rect2)
            screen.blit(victory_surface_score, victory_rect_score)
            screen.blit(victory_surface_highscore, victory_rect_highscore)
            for laser in self.aliens_lasers:
                laser.kill()
            for alien in self.aliens:
                alien.kill()
            for extra in self.extra:
                extra.kill()
            self.lost = True

    def check_highscore(self):
        with open('highscore.txt') as file:
            tmp_score = int(file.read())
            if self.score >= tmp_score:
                file.close()
                file = open('highscore.txt', 'w')
                file.write(str(self.score))
                file.close()
                self.highscore = self.score
            else:
                self.highscore = tmp_score
                file.close()

    def run(self):
        screen.blit(self.background, (0, 0))

        self.aliens.update(self.alien_direction)
        self.alien_pos_check()
        self.aliens_lasers.update()
        self.extra_alien_timer()
        self.extra.update()
        self.aliens.draw(screen)
        self.aliens_lasers.draw(screen)
        self.extra.draw(screen)

        self.collisions_check()

        self.display_lives()
        self.display_score()

        if self.player.sprites():
            self.player.sprite.lasers.draw(screen)
            self.player.draw(screen)
            self.player.update()

        self.blocks.draw(screen)

        if not self.lost:
            self.victory_screen()
        else:
            self.lost_screen()


if __name__ == '__main__':
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_icon(pygame.image.load('graphics/icon.png'))
    pygame.display.set_caption('Space Invaders... just not that good.')
    clock = pygame.time.Clock()
    game = Game()

    ALIEN_LASER_TIMER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIEN_LASER_TIMER, 700)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIEN_LASER_TIMER:
                game.alien_shoot()

        screen.fill((0, 0, 40))
        game.run()

        pygame.display.flip()
        clock.tick(60)
