#!/usr/bin/env python

import pygame as pg
from math import sin, cos, atan2

"""
testing out an idea for sdl-iso-project:

I REALLY want ramps and other non-cube blocks, but I REALLY DON'T want
overcomplicated and unnecessary geometry capabilities.

Here is my idea: blocks that have an AABB and a plane intersecting them,
"chopping off" a piece of the AABB. This could be defined something like this:

struct chopped_bbox_t {
    bbox_t box;
    ray_t normal; // for the plane
} 

With this kind of system, I wouldn't have to add very much data whatsoever, and
none of the current behavior would have to change. All I have to do is check if
a block uses a chopped bounding box, and then apply a ray-plane collision.
Well, not exactly that simple but that's the gist of it lol

"""

class Ray:
    def __init__(self, pos, vec):
        self.pos = pos
        self.vec = vec

class BBox:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size

    def check_inside(self, pos):
        for i in (0, 1):
            if not (0 <= pos[i] - self.pos[i] <= self.size[i]):
                return False
        return True

class ChoppedBBox(BBox):
    def __init__(self, pos, size, normal):
        super().__init__(pos, size)
        self.normal = normal

def vec_add(a, b):
    return tuple(t[0] + t[1] for t in zip(a,b))

def vec_sub(a, b):
    return tuple(t[0] - t[1] for t in zip(a,b))

"""
def hamilton_prod(quat1, quat2):
    prod_signs = (
        (1, -1, -1, -1),
        (1,  1,  1, -1),
        (1, -1,  1,  1),
        (1,  1, -1,  1)
    )

    prod_orders = (
        (0, 1, 2, 3),
        (1, 0, 3, 2),
        (2, 3, 0, 1),
        (3, 2, 1, 0)
    )
    
    result = [0] * 4

    for i in range(4):
        for j in range(4):
            result[i] += quat1[j] * quat2[prod_orders[i][j]] * prod_signs[i][j]

    return tuple(result)

def inverse_quat(quat):
    return (quat[0], *(-v for v in quat[1:]))
"""

def main():
    ray = Ray((1, 1, 1), (-.9, -.9, -.9))
    cbox = ChoppedBBox((-.5, -.5, -.5), (1, 1, 1), Ray((0, 0, 0), (1, 0, 0)))

    # collide_ray_cbox(ray, cbox)

if __name__ == "__main__":
    main()

