import random
from math import isclose
import pygame as pg
from pygame import Rect

"""
figuring out collision for sdl-iso-project
"""

SIDE = 20

def collides(a, b, x):
    return a < x < b

def collide1d(sA, lA, sB, lB):
    return collides(sB, sB + lB, sA) or collides(sB, sB + lB, sA + lA) or (isclose(sA, sB) and isclose(lA, lB))

def collideRect(rA, rB):
    return collide1d(rA.x, rA.w, rB.x, rB.w) and collide1d(rA.y, rA.h, rB.y, rB.h)

def rayCollideRect(pos, vec, rect):
    :

class Entity:
    def __init__(self, rect):
        self.rect = rect
        self.vel = [0, 0]

    def collideWith(self, rect):
        return collideRect(self.rect, rect) 

    def tick(self, ms, rectlist):
        t = ms / 1000
        tvel = [v * t for v in self.vel]

        

def main():
    pg.init()
    screen = pg.display.set_mode((640, 480))
    timer = pg.time.Clock()
    timer.tick()

    me = Entity(Rect(100, 100, SIDE, SIDE))
    ctrl = [0, 0]
    spd = 100
    
    wrld = [[random.random() < .1 for x in range(int(screen.get_width() / SIDE))] for y in range(int(screen.get_height() / SIDE))]

    while 1:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit(0)

        ctrl[0] = ctrl[1] = 0
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            ctrl[0] = -1
        if keys[pg.K_w]:
            ctrl[1] = -1
        if keys[pg.K_d]:
            ctrl[0] = 1
        if keys[pg.K_s]:
            ctrl[1] = 1
        
        for i in (0, 1):
            me.vel[i] = ctrl[i] * spd
        me.tick(timer.get_time())

        collideResolve(me, wrld)

        screen.fill((0, 0, 0))

        for y in range(len(wrld)):
            for x in range(len(wrld[y])):   
                if wrld[y][x]:
                    rect = Rect(x * SIDE, y * SIDE, SIDE, SIDE)
                    color = (200, 200, 200) if me.collideWith(rect) else (100, 100, 100)
                    pg.draw.rect(screen, color, rect)

        pg.draw.rect(screen, (200, 0, 200), me.rect)

        pg.display.flip()
        timer.tick(25)

if __name__ == "__main__":
    main()
