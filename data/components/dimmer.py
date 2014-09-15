import pygame as pg


class Dimmer(object):
    def __init__(self, size):
        self.surf = pg.Surface(size)
        self.surf.fill(pg.Color("gray1"))
        self.surf.convert_alpha()
        self.alpha = 255
        self.increment = .005
        self.fading_in = True
        self.done = False
        
    def update(self):
        if self.fading_in:
            self.alpha -= self.increment
            self.increment += .001
            if self.alpha <= 0:
                print self.increment
                self.alpha = 0
                self.fading_in = False
        else:
            self.increment -= .0005
            self.alpha += self.increment
            if self.alpha >= 255:
                self.done = True
        self.surf.set_alpha(int(self.alpha)) 
    
    def draw(self, surface):
        surface.blit(self.surf, (0, 0))