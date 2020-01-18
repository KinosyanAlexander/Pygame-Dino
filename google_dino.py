#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import os
from copy import deepcopy
import random as rn
from win32api import GetSystemMetrics



def load_image(name, colorkey=None):
    way = os.getcwd()
    print(way)
    fullname = way + '\\' +  os.path.join('data\\images\\', name)
    print(fullname)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image



def resize_sp(sp, zoom=1):
    for d in range(zoom):
        for i, v in enumerate(sp):
            sp[i] = pygame.transform.scale2x(v)
    return sp


RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
is_full_screen = 1
is_game_now = False
space_from_enemy = list(range(600, 850))
enemy_levels = (300, 340, 380)
restart = True
game_over = False
FPS = 60
score = 0
clock = pygame.time.Clock()


with open('data\\hi_score.txt', encoding='utf-8') as f:
    hi_score = f.read()


pygame.init()

w, h = GetSystemMetrics(0), 450

sc = pygame.display.set_mode((w, h), pygame.FULLSCREEN)


pygame.font.init()
myfont = pygame.font.SysFont('sitkasmallsitkatextbolditalicsitkasubheadingbolditalicsitkaheadingbolditalicsitkadisplaybolditalicsitkabannerbolditalic', 50)

pygame.mixer.init()
jump_sound = pygame.mixer.Sound('data\\sounds\\jump.wav')
game_over_sound = pygame.mixer.Sound('data\\sounds\\game_over.wav')
sourse_point_sound = pygame.mixer.Sound('data\\sounds\\chekpoint.wav')

pole_im = load_image('pole.png', -1)

dino_front_im = [load_image('dino\\front.png', -1)][0]
dino_beg_anim = [load_image(f'dino\\beg{i + 1}.png', -1) for i in range(2)]
dino_prignut_anim = [load_image(f'dino\\prignut{i + 1}.png', BLACK) for i in range(2)]

small_cactuses_im = [load_image(f'cactuses\\small{i + 1}.png', BLACK) for i in range(3)]
big_cactuses_im = [load_image(f'cactuses\\big{i + 1}.png', BLACK) for i in range(3)]
all_cactuses_im = [small_cactuses_im, big_cactuses_im]

bird_anim = [load_image(f'bird\\bird{i + 1}.png', BLACK) for i in range(2)]



game_over_im = load_image(f'game_over.png', BLACK)
rect_game_over = game_over_im.get_rect()
rect_game_over.center = (w//2, h//2)

restart_button_im = load_image(f'restart_button.png', BLACK)
rect_restart_button = restart_button_im.get_rect()
rect_restart_button.center = (rect_game_over.width // 2 + rect_game_over.left, rect_game_over.bottom + 70)

class Pole(pygame.sprite.Sprite):
    image = pole_im
    
    def __init__(self, pos, v):
        pygame.sprite.Sprite.__init__(self)
        
        self.v = v
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
    
    def update(self):
        if is_game_now:
            self.rect.x -= int(self.v)
        if self.rect.bottomright[0] >= 0 :
            self.draw()
        else:
            self.kill()
        if max([i.rect.right for i in pole]) <= w:
            pole.add(Pole(self.rect.bottomright, self.v))
    
    def draw(self):
        sc.blit(self.image, self.rect)

class Dino(pygame.sprite.Sprite):
    
    def __init__(self):
        self.image = dino_front_im
        self.anim_sp = dino_beg_anim
        
        self.rect = self.image.get_rect()
        self.pos = [30, h - pole_im.get_height() + 30 - 50]
        self.rect.bottomleft = self.pos
        
        self.c = 0
        self.lim_anim = 12
        
        self.is_jump = True
        self.MAX_JUMP = 10
        self.jump_v = self.MAX_JUMP
        self.g = 0.5
        
    
    def update(self, keys):
        global is_game_now, restart, game_over
        
        if keys[pygame.K_DOWN]:
            self.anim_sp = dino_prignut_anim
        else:
            self.anim_sp = dino_beg_anim
        if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            self.is_jump = True
        
        
        if self.is_jump:
            self.jump()
        else:
            self.c += 1
            self.image = self.anim_sp[(self.c // (self.lim_anim // len(self.anim_sp))) % len(self.anim_sp)]
        
        self.draw()
        
        if pygame.sprite.spritecollide(self, enemies, False, collided=pygame.sprite.collide_mask):
            game_over_sound.play()
            is_game_now = False
            restart = False
            game_over = True
        
    def draw(self):
        self.rect = self.image.get_rect()
        self.rect.bottomleft = list(map(int, self.pos))
        sc.blit(self.image, self.rect)

    def jump(self):
        if self.jump_v >= self.MAX_JUMP * -1:
            if self.jump_v == self.MAX_JUMP:
                jump_sound.play()
            self.pos[1] -= self.jump_v / self.g#(self.jump_v ** 2) / 2
            self.jump_v -= self.g
            
        else:
            self.jump_v = self.MAX_JUMP
            self.is_jump = False
        self.image = dino_front_im
        self.c = 0

class Cactus(pygame.sprite.Sprite):
    def __init__(self, im, x):
        pygame.sprite.Sprite.__init__(self)
        self.image = im
        self.pos = [x, h - pole_im.get_height() - 25]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = self.pos
        self.space = rn.choice(space_from_enemy)
        self.start_position = self.pos[0]
        self.is_plod = False
    
    def draw(self):
        self.rect.bottomleft = self.pos
        sc.blit(self.image, self.rect)
    
    def update(self):
        self.pos[0] -= int(pole.sprites()[-1].v)
        
        if self.pos[0] <= self.start_position - self.space and not self.is_plod:
            enemy = rn.choice([Cactus(rn.choice(rn.choice(all_cactuses_im)), self.pos[0] + self.space),
                               Bird(self.pos[0] + self.space, rn.choice(enemy_levels))])
            enemies.add(enemy)
            self.is_plod = True

        if self.rect.right < 0:
            self.kill()
        
        self.draw()

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.pos = [x, y]
        self.anim_sp = bird_anim
        self.image = self.anim_sp[0]
        
        self.rect = self.image.get_rect()
        self.rect.bottomleft = self.pos
        
        self.c = 0
        self.lim_anim = 20
        
        self.space = rn.choice(space_from_enemy)
        self.start_position = self.pos[0]
        self.is_plod = False
    
    def update(self):

        self.c += 1
        self.image = self.anim_sp[(self.c // (self.lim_anim // len(self.anim_sp))) % len(self.anim_sp)]
        
        #self.pos[0] -= pole.sprites()[-1].v
        
        self.rect.move_ip((int(-pole.sprites()[-1].v), 0))
        
        
        if self.rect.left <= self.start_position - self.space and not self.is_plod:
            enemy = rn.choice([Cactus(rn.choice(rn.choice(all_cactuses_im)), self.rect.left + self.space),
                               Bird(self.rect.left + self.space, rn.choice(enemy_levels))])
            enemies.add(enemy)
            self.is_plod = True

        if self.rect.right < 0:
            self.kill()
        self.draw()
    
    def draw(self):
        #self.rect.bottomleft = self.pos
        sc.blit(self.image, self.rect)

class Numbers():
    def __init__(self, pos, color, numb=score, changable=True, pristavka=''):
        self.numb = numb
        self.surf = myfont.render(pristavka + str(int(self.numb)).rjust(5, '0'), False, (color))
        self.pos = pos
        self.changable = changable
        self.pristavka = pristavka
        self.color = color
    
    def update(self):
        if self.changable:
            self.numb += 10 / FPS
            self.surf = myfont.render(self.pristavka + str(int(self.numb)).rjust(5, '0'), False, (self.color))
            if not self.pristavka:
                #print(self.numb)
                if not int(self.numb) % 100 and 0 < self.numb <= 800:
                    for i in pole:
                        i.v += 10/FPS
                if not int(self.numb) % 100 and int(self.numb + 10 / FPS) % 100 and self.numb > 99:
                    sourse_point_sound.play()
                #print(pole.sprites()[0].v)
        else:
            if int(self.numb) <= int(score_widget.numb):
                self.changable = True
        self.draw()
    
    def draw(self):
        sc.blit(self.surf, self.pos)


def settings():
    global pole, dino, enemies, restart, score_widget, hi_score_widget
    pole = pygame.sprite.Group()


    pole.add(Pole((0, h - 50), 10))

    dino = Dino()


    enemies = pygame.sprite.Group()
    enemies.add(Cactus(small_cactuses_im[0], w + 1000))
    
    
    
    surface_of_myfont = myfont.render(str(int(score)).rjust(5, '0'), False, (BLACK))
    score_widget = Numbers((w - surface_of_myfont.get_width() - 50, surface_of_myfont.get_height() - 10), BLACK)
    
    hi_score = int(open('data\\hi_score.txt', encoding='utf-8').read())
    hi_score_widget = Numbers((score_widget.pos[0] - score_widget.surf.get_width() - 120, score_widget.pos[1]),
                              (100, 100, 100),
                              numb=hi_score,
                              changable=False,
                              pristavka='HI ')
    
    
    restart = False


settings()


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            elif event.key == pygame.K_F5:
                if is_full_screen:
                    sc = pygame.display.set_mode((w, h))
                    is_full_screen = 0
                else:
                    sc = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
                    is_full_screen = 1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if rect_restart_button.collidepoint(event.pos) and not is_game_now and game_over:
                is_game_now = True
                game_over = False
                restart = True
    
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_SPACE] and not is_game_now:
        is_game_now = True
        restart = True
    
    sc.fill(WHITE)
    
    if restart:
        if hi_score_widget.changable:
            with open('data\\hi_score.txt', 'w', encoding='utf-8') as f:
                f.write(str(int(hi_score_widget.numb)).rjust(5, '0'))
        settings()
    if not is_game_now:
        pole.draw(sc)
        enemies.draw(sc)
        dino.draw()
        score_widget.draw()
        hi_score_widget.draw()
        if game_over:
            sc.blit(game_over_im, rect_game_over)
            sc.blit(restart_button_im, rect_restart_button)
    elif is_game_now:
        pole.update()
        enemies.update()
        dino.update(keys)
        score_widget.update()
        hi_score_widget.update()
    clock.tick(FPS)
    pygame.display.flip()
    pygame.display.update()
pygame.quit()
