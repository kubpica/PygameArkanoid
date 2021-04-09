import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_p
import shelve

pygame.init()

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
font = pygame.font.Font(pygame.font.get_default_font(), 18)
clock = pygame.time.Clock()

uruchomiona = True
paused = False


class Highscore:

    def __init__(self):
        d = shelve.open('score.txt')
        if 'score' in d:
            self.score = d['score']
        else:
            self.score = 0
        d.close()

    def new_score(self, s):
        if s > self.score:
            self.score = s
            d = shelve.open('score.txt')
            d['score'] = s
            d.close()


class Stats:

    def __init__(self):
        self.level = 1
        self.score = 5000
        self.lives = 3
        self.text_surface = font.render('Hello world.'
                                        , True, (255, 255, 255))

    def update_text_surface(self):
        pause_text = "pause"
        if paused:
            pause_text = "unpause"

        self.text_surface = font.render(
            "P to {} | Lives: {} | Level: {} | Score: {}".format(pause_text, self.lives, self.level, self.score)
            , True, (255, 255, 255))

    def set_custom_text(self, text):
        self.text_surface = font.render(text, True, (255, 255, 255))

    def set_level(self, lvl):
        if lvl > -1:
            lvl = lvl % 7

        self.level = lvl

        if self.level == 1:
            self.score = 5000
            self.lives = 3

        if lvl == 0:
            self.set_custom_text(" PygameArkanoid | P to play | Esc to exit | Highscore: {}".format(hs.score))
        elif lvl == 6:
            self.set_custom_text(
                " Congratulations, you won | Score: {} | P to restart | Esc to exit".format(self.score))
            hs.new_score(self.score)
        elif lvl == -1:
            self.set_custom_text(" Game Over | Score: {} | P to restart | Esc to exit".format(self.score))
            hs.new_score(self.score)
        else:
            level.set_level(lvl)
            self.set_custom_text("Lives: {} | Press the UP key to start the level | Esc to exit".format(self.lives))

    def add_score(self, amount):
        self.score += amount
        self.update_text_surface()

    def dec_score(self, amount):
        self.score -= amount
        if self.score < 0:
            self.score = 0
        self.update_text_surface()

    def set_lives(self, amount):
        self.lives = amount
        self.update_text_surface()

    def dec_lives(self):
        self.lives -= 1
        self.set_custom_text("Lives: {} | Press the UP key to resume the game | Esc to exit".format(self.lives))
        if self.lives <= 0:
            self.set_level(-1)

    def display(self):
        screen.blit(self.text_surface, dest=(0, 0))


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((30, 10))
        self.surf.fill((255, 0, 0))
        self.surf = pygame.image.load("images/belka.png").convert()
        self.rect = self.surf.get_rect(center=(x, y))

    def update(self, pressed_keys):
        if pressed_keys[K_LEFT]:
            # print("pressed left")
            self.rect.move_ip(-3, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(3, 0)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH


class Klocek(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((20, 10))
        self.surf = pygame.image.load("images/klocek.png").convert()
        self.rect = self.surf.get_rect(center=(x, y))

    def set_kolor(self, color):
        self.surf.fill(color)

    def hit(self):
        if self.rect.top <= ball.rect.bottom or self.rect.bottom >= ball.rect.top:
            ball.bounceY()
        else:
            ball.bounceX()
        self.kill()  # usuniecie klocka
        stats.add_score(5000)


class Ball(pygame.sprite.Sprite):

    def __init__(self, x, y):
        self.direction = pygame.Vector2()
        self.moving = False
        self.surf = pygame.Surface((5, 5))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(center=(x, y))

    def bounceX(self):
        self.direction.x *= -1

    def bounceY(self):
        self.direction.y *= -1

    def update(self):
        if paused:
            return

        if self.moving:
            self.rect.move_ip(self.direction.x, self.direction.y)

            if self.rect.left < 0:
                self.rect.left = 0
                self.bounceX()
            if self.rect.right > SCREEN_WIDTH - 5:
                self.rect.right = SCREEN_WIDTH - 5
                self.bounceX()
            if self.rect.bottom < 0:
                self.rect.bottom = 0
                self.bounceY()
            if self.rect.top > SCREEN_HEIGHT - 5:
                self.rect.bottom = SCREEN_HEIGHT - 5
                self.moving = False
                stats.dec_lives()
        else:
            if pressed_keys[K_UP]:
                stats.update_text_surface()
                self.direction.x = 3
                self.direction.y = 3
                self.moving = True

            self.rect.x = player.rect.x + 15
            self.rect.y = player.rect.y - 8


class Level:

    def __init__(self):
        self.klocki = pygame.sprite.Group()

    def set_level(self, lvl):
        ball.moving = False
        self.klocki.empty()
        amount_in_row = lvl * 2
        for x in range(amount_in_row):
            for y in range(lvl):
                x_offset = (640 - 40 * amount_in_row) / 2 + 20 * (y % 2)
                self.klocki.add(Klocek(x_offset + 40 * x, 120 + 40 * y))

    def display(self):
        for klocek in self.klocki:
            screen.blit(klocek.surf, klocek.rect)

    def check_collisions(self):
        if pygame.sprite.spritecollideany(ball, self.klocki):
            delete_klocek = pygame.sprite.spritecollideany(ball, self.klocki)
            delete_klocek.hit()
            if not self.klocki:
                stats.set_level(stats.level + 1)


pygame.display.set_caption("Arkanoid UJ - Jakub Pranica")

player = Player(305, 450)
ball = Ball(315, 440)

hs = Highscore()
level = Level()
stats = Stats()
stats.set_level(0)

pygame.mixer.music.load("sounds/intro.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

while uruchomiona:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            uruchomiona = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                uruchomiona = False
            elif event.key == K_p:
                if 0 < stats.level < 6:
                    paused = not paused
                else:
                    stats.set_level(stats.level + 1)

    screen.fill((0, 0, 0))
    stats.display()

    if 0 < stats.level < 6:
        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        ball.update()
        if ball.moving and not paused:
            stats.dec_score(1)

        level.display()
        screen.blit(player.surf, player.rect)
        screen.blit(ball.surf, ball.rect)

        level.check_collisions()

        if pygame.sprite.collide_rect(ball, player):
            if ball.rect.y > player.rect.y:
                ball.bounceY()
            else:
                ball.bounceX()

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
