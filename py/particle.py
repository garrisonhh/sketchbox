#!/usr/bin/env python

import pygame as pg
import random

SC_W = 800
SC_H = 600
P = [[(random.random() < 0.05) for x in range(SC_W)] for y in range(SC_H)]

def tick():
    global P
    P_N = [[False for x in range(SC_W)] for y in range(SC_H)]

    for y in range(SC_H):
        for x in range(SC_W):
            if P[y][x]:
                if y < SC_H - 1:
                    if not P[y + 1][x]:
                        P_N[y + 1][x] = True
                    elif x > 0 and not P[y + 1][x - 1]:
                        P_N[y + 1][x - 1] = True
                    elif x < SC_W - 1 and not P[y + 1][x + 1]:
                        P_N[y + 1][x + 1] = True
                    else:
                        P_N[y][x] = True
                else:
                    P_N[y][x] = True

    P = P_N

def main():
    pg.init()
    screen = pg.display.set_mode((SC_W, SC_H))
    timer = pg.time.Clock()
    timer.tick()

    while 1:
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                pg.quit()
                exit(0)

        tick()

        screen.fill((0, 0, 0))

        for y in range(SC_H):
            for x in range(SC_W):
                if P[y][x]:
                    screen.set_at((x, y), (200, 175, 100))

        pg.display.flip()
        timer.tick(120)

if __name__ == "__main__":
    main()
