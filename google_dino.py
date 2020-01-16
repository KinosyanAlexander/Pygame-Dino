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




pole_im = load_image('pole.png', -1)

dino_front_im = [load_image('dino\\front.png', -1)][0]
dino_beg_anim = [load_image(f'dino\\beg{i + 1}.png', -1) for i in range(2)]
dino_prignut_anim = [load_image(f'dino\\prignut{i + 1}.png', BLACK) for i in range(2)]

small_cactuses_im = [load_image(f'cactuses\\small{i + 1}.png', BLACK) for i in range(1)]

game_over_im = load_image(f'game_over.png', BLACK)
rect_game_over = game_over_im.get_rect()
rect_game_over.center = (w//2, h//2)

restart_button_im = load_image(f'restart_button.png', BLACK)
rect_restart_button = restart_button_im.get_rect()
rect_restart_button.center = (rect_game_over.width // 2 + rect_game_over.left, rect_game_over.bottom + 70)

class Pole(pygame.sprite.Sprite):
    image = pole_im
    
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        
        self.v  = 10
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
    
    def update(self):
        if is_game_now:
            self.rect.x -= self.v
        if self.rect.bottomright[0] >= 0 :
            self.draw()
        else:
            self.kill()
        if max([i.rect.right for i in pole]) <= w:
            pole.add(Pole((self.rect.bottomright)))
    
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
        
        if pygame.sprite.spritecollide(self, cactuses, False, collided=pygame.sprite.collide_mask) or pygame.sprite.spritecollide(self, birds, False, collided=pygame.sprite.collide_mask):
            is_game_now = False
            restart = False
            game_over = True
        
    def draw(self):
        self.rect = self.image.get_rect()
        self.rect.bottomleft = list(map(int, self.pos))
        sc.blit(self.image, self.rect)

    def jump(self):
        if self.jump_v >= self.MAX_JUMP * -1:
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
        self.pos[0] -= pole.sprites()[-1].v
        
        if self.pos[0] <= self.start_position - self.space and not self.is_plod:
            cactus = Cactus(small_cactuses_im[0], self.pos[0] + self.space)
            cactuses.add(cactus)
            self.is_plod = True

        if self.rect.right < 0:
            self.kill()
        
        self.draw()

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
        else:
            if int(self.numb) <= int(score_widget.numb):
                self.changable = True
        self.draw()
    
    def draw(self):
        sc.blit(self.surf, self.pos)


    
    






def settings():
    global pole, dino, cactuses, birds, restart, score_widget, hi_score_widget
    pole = pygame.sprite.Group()


    pole.add(Pole((0, h - 50)))

    dino = Dino()


    cactuses = pygame.sprite.Group()
    cactuses.add(Cactus(small_cactuses_im[0], w + 1000))
    
    birds = pygame.sprite.Group()
    
    
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
        cactuses.draw(sc)
        dino.draw()
        score_widget.draw()
        hi_score_widget.draw()
        if game_over:
            sc.blit(game_over_im, rect_game_over)
            sc.blit(restart_button_im, rect_restart_button)
    elif is_game_now:
        pole.update()
        cactuses.update()
        dino.update(keys)
        score_widget.update()
        hi_score_widget.update()
    clock.tick(FPS)
    pygame.display.flip()
    pygame.display.update()
pygame.quit()
