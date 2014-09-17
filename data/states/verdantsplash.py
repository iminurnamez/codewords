from random import randint, choice
from itertools import cycle
import pygame as pg
from .. import tools, prepare


class Snow(object):
    def __init__(self, rect):
        self.started = False
        self.stopped = False
        self.surf = pg.Surface(rect.size).convert()
        self.rect = self.surf.get_rect(topleft=rect.topleft)
        self.surf.fill(pg.Color("white"))
        self.surf.set_colorkey(pg.Color("black"))
        self.blotch_size = (8, 8)
        self.ticks = 0
        
    def update(self, ticks):
        self.ticks += 1
        if not ticks % 5:
            for _ in range(3):
                rand_pos = (randint(-self.blotch_size[0]//2, self.surf.get_width()),
                                   randint(-self.blotch_size[1]//2, self.surf.get_height()))
                pg.draw.rect(self.surf, pg.Color("black"), (rand_pos, self.blotch_size))
        if not ticks % 12:       
            self.blotch_size = (self.blotch_size[0] + 8,
                                        self.blotch_size[1] + 8)
        if self.ticks > 500:
            self.surf.fill(pg.Color("black"))
            self.stopped = True

    def draw(self, surface):
        if not self.stopped:
            surface.blit(self.surf, self.rect)


class Truck(object):
    def __init__(self, lefttop, stop_pos):
        self.image = prepare.GFX["truck"]
        self.pos = lefttop
        self.speed = 7
        self.stop_pos = stop_pos
        self.started = False
        self.stopped = False
        
    def update(self, ticks):
        if self.pos[0] > self.stop_pos:
            self.pos = (self.pos[0] - self.speed, 
                             self.pos[1])
                             
    def draw(self, surface):
        if self.started and not self.stopped:
            surface.blit(self.image, self.pos)
            

class Sun(object):
    def __init__(self, center_pos):
        self.pos = center_pos
        self.speed = 1.0
        self.started = False
        self.stopped = False
        
    def update(self, ticks):
        self.pos = (self.pos[0], 
                         self.pos[1] - self.speed)
        if self.pos[1] < -150:
            self.stopped = True

    def draw(self, surface):
        if self.started and not self.stopped:
            pg.draw.circle(surface, pg.Color("gold3"), 
                                 (int(self.pos[0]), int(self.pos[1])), 100)
        
        
class Raindrop(object):
    def __init__(self, pos, distance):
        self.fallen = False
        self.pos = pos
        self.land = self.pos[1] + distance
        self.speed = 9.3
        
    def update(self):
        self.pos = (self.pos[0], self.pos[1] + self.speed)
        if self.pos[1] > self.land:
            self.fallen = True

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color("blue"), (self.pos, (2, 4)))   


class Cloud(object):
    def __init__(self, topleft):
        self.pos = topleft
        self.image = prepare.GFX["cloudsnake"]

        self.rect = self.image.get_rect(topleft=topleft)
        self.speed = 5.5
        self.raindrops = []
        self.rain_offsets = [(90, 279), (256, 284), (171, 205),
                                     (312, 215), (92, 164), (264, 145),
                                     (185, 103)]
        self.started = False
        self.stopped = False
        
    def update(self, ticks):
        self.pos = (self.pos[0] - self.speed,
                         self.pos[1])
        if not ticks % 2:
            rain_pos = choice(self.rain_offsets)
            rain_pos = (rain_pos[0] + self.pos[0],
                              rain_pos[1] + self.pos[1])
            self.raindrops.append(Raindrop(rain_pos, 650 - self.rect.top))
        for raindrop in self.raindrops:
            raindrop.update()
        self.raindrops = [x for x in self.raindrops if not x.fallen]
                    
    def draw(self, surface):
        for drop in self.raindrops:
            drop.draw(surface)
        if self.started and not self.stopped:
            surface.blit(self.image, self.pos) 
                         

class Vines(object):
    def __init__(self, center_point):
        self.imgs = [prepare.GFX["verdant-" + str(x) + ""] 
                          for x in range(30, 0, -1)]
        self.imgs.append(prepare.GFX["verdantfinal"])
  
        self.rect = self.imgs[0].get_rect(center=(center_point))
        self.imgs= iter(self.imgs)
        self.image = next(self.imgs)
        self.started = False
        self.stopped = False
        
    def update(self, ticks):
        if not ticks % 10:
            try:
                self.image = next(self.imgs)
            except StopIteration:
                pass
    
    def draw(self, surface):
        if self.started and not self.stopped:
            surface.blit(self.image, self.rect)


class Balloon(object):
    def __init__(self, center_point, stop):
        self.base_image = prepare.GFX["balloon"]
        self.pos = center_point
        self.rect = self.base_image.get_rect(center=self.pos)
        self.image = self.base_image
        self.speed = 1.1
        self.stop = stop
        self.started = False
        self.stopped = False
        self.increment = 4.0
        
    def update(self, ticks):
        
        if self.rect.width < 1600 and self.pos[1] < self.stop: 
            self.increment += .01     
            if self.rect.width > 900:
                self.increment += .02
            if self.rect.width > 1200:
                self.increment += .04
            w, h = self.image.get_size()
            new_size = (int(w + int(self.increment)), int(h + int(self.increment)))
            self.image = pg.transform.scale(self.base_image, new_size)
            self.rect = self.image.get_rect(center=self.pos)
        
        
        self.pos = (self.pos[0],
                         self.pos[1] + self.speed)        
        self.rect.center = self.pos
        self.speed += .01
        
    def draw(self, surface):
        if self.started and not self.stopped:
            surface.blit(self.image, self.rect)
        

class Star(object):
    twinkle = pg.Surface((4, 4)).convert_alpha()
    twinkle.fill(pg.Color("yellow"))
    twinkle.set_alpha(64)
    
    def __init__(self, pos):
        self.pos = pos
        self.ticks = randint(0, 4)
        self.frequency = randint(10, 20)
        self.twinkling = False
        
    def update(self):
        self.ticks += 1
        self.twinkling = False
        if not self.ticks % self.frequency:
            self.twinkling = True
 
    def move(self, offset):
        self.pos = (self.pos[0] + offset[0], 
                         self.pos[1] + offset[1])
        
    def draw(self, surface):
        twinkler = pg.Rect(self.pos, (2, 2))
        if self.twinkling:
            surface.blit(self.twinkle, (twinkler.left - 1, twinkler.top - 1))
        pg.draw.rect(surface, (255, 255, 0), twinkler)
        

class Sky(object):
    def __init__(self, (r, g, b), (width, height)):
        self.started = False
        self.stopped = False
        self.r = r
        self.g = g
        self.b = b
        self.peaked = False
        
        self.stars = [Star((randint(1, width), randint(1, height)))
                           for _ in range(50)]
                           
    def update(self, ticks):        
        self.stars = [x for x in self.stars if x.pos[1] > -1]    
        self.g = min(self.g + .1, 128)
        self.b = min(self.b + .15, 200)
        if not self.peaked:
            self.r += .17
            if self.r > 50:
                self.peaked = True
        else:
            self.r = max(0, self.r - .25)
        
    def draw(self, surface):
        surface.fill((int(self.r), int(self.g), int(self.b)))
        for star in self.stars:
            star.move((0, -.9))
            star.update()
            star.draw(surface)
            
            
class Grass(object):
    def __init__(self, rect):
        self.grass = prepare.GFX["grass"]
        self.blue_flower = prepare.GFX["blueflower"]
        self.yellow_flower = prepare.GFX["yellowflower"]
        self.surf = pg.Surface(rect.size)
        self.surf.set_colorkey(pg.Color("black"))
        self.rect = rect
        self.started = False
        self.stopped = False
        self.images = [self.grass] * 7
        self.images.extend([self.blue_flower, self.yellow_flower])
        self.ticks = 0
        
    def update(self, ticks):
        self.ticks += 1
        if self.ticks > 500:
            self.stopped = True
        randpos = (randint(1, self.rect.width), randint(0, self.rect.height))
        self.surf.blit(choice(self.images), randpos)
        
    def draw(self, surface):
        if self.started:
            surface.blit(self.surf, self.rect)
        
        
class Glass(object):
    def __init__(self):
        self.image = prepare.GFX["glass"]
        self.ticks = 0
        self.started = False
        self.stopped = False
        
    def update(self, ticks):
        self.ticks += 1
        if self.ticks > 60:
            self.stopped = True
    
    def draw(self, surface):
        if self.started:
            surface.blit(self.image, (0, 0))
        
        
class VerdantSplash(tools._State):
    def __init__(self):
        super(VerdantSplash, self).__init__()
        self.next = "GAME"
        self.persist["sounds"] = True
        self.persist["fullscreen"] = False
        self.screen_rect = pg.display.get_surface().get_rect()
        self.surf = pg.Surface((1920, 1080))
        self.rect = self.surf.get_rect()
        self.sun = Sun((self.rect.centerx,
                                self.rect.centery + 160))
        self.ground_rect = pg.Rect(0, 600, self.rect.width, self.rect.height - 600)
        self.grass = Grass(self.ground_rect)
        self.road = pg.Rect(0, self.rect.bottom - 100, self.rect.w, 100)
        mountains = [1080, 950, 900, 650, 400, 150, 700, -50, 800,
                             1100, 1250, 1400, 1560, 1680, 1750]
        mountain = prepare.GFX["mountains"]
        self.mountains = pg.Surface((self.screen_rect.width,
                                                    mountain.get_height())).convert()
        self.mountains.fill(pg.Color("black"))
        self.mountains.set_colorkey(pg.Color("black"))
        self.mountains_rect = self.mountains.get_rect(bottomleft=(0, self.ground_rect.top))
        for left in mountains:
            self.mountains.blit(mountain, (left, 0))
        self.sky = Sky((0, 0, 20), (self.rect.width, self.ground_rect.top - 20))
        self.snow = Snow(self.ground_rect)
        self.cloud = Cloud((self.rect.right + 5, self.rect.top + 50))
        self.vines = Vines((self.rect.centerx, self.ground_rect.top + 80))
        self.truck = Truck((self.rect.right + 5, self.rect.bottom - 250),
                                    self.rect.centerx - 450)
        self.balloon = Balloon((self.rect.centerx, self.rect.top - 150),
                                        self.rect.top + 350)         
        self.glass = Glass()
        self.ticks = 0
        self.starts = {170: self.sky,
                            400: self.sun,
                            440: self.snow,
                            900: self.cloud,
                            1230: self.grass,
                            1270: self.vines,
                            1650: self.truck,
                            1850: self.balloon}
        self.props = [self.sky, self.sun, self.snow, self.grass, self.cloud, self.vines,
                           self.truck, self.balloon, self.glass]
        
    def update(self, surface, keys, dt):
        self.ticks += 1
        for tick in self.starts:
            if self.ticks >= tick:
                self.starts[tick].started = True
        self.starts  = {k: v for k, v in self.starts.items() if k > self.ticks}
        
        for obj in self.props:
            if obj.started and not obj.stopped:
                obj.update(self.ticks)

        if self.balloon.pos[1] >= self.balloon.stop:
            self.glass.started = True
        if self.glass.stopped:
            self.done = True
        self.draw(surface)
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True

    def draw(self, surface):
        self.sky.draw(self.surf)
        
        self.sun.draw(self.surf)
        self.surf.blit(self.mountains, self.mountains_rect)
        pg.draw.rect(self.surf, (109, 182, 55), self.ground_rect)
        self.grass.draw(self.surf)
        self.snow.draw(self.surf)
        pg.draw.rect(self.surf, pg.Color("gray1"), self.road)
        self.cloud.draw(self.surf)
        self.vines.draw(self.surf)
        self.truck.draw(self.surf)
        self.balloon.draw(self.surf)
        self.glass.draw(self.surf)
        if self.surf.get_size() != self.screen_rect.size:
            surface.blit(pg.transform.scale(self.surf, self.screen_rect.size), (0, 0))
        else:
            surface.blit(self.surf, (0, 0))