from math import pi, cos, sin
import pygame as pg
from .. import tools, prepare
from ..components.angles import (get_xaxis_reflection, get_yaxis_reflection, get_angle,
                                                    get_collision_side, project, get_opposite_angle)
from ..components.dimmer import Dimmer


        
class Bumper(object):
    def __init__(self, l, t, w, h):
        self.surf = pg.Surface((w, h)).convert()
        self.rect = self.surf.get_rect(topleft=(l, t))
        self.surf.fill(pg.Color("black"))
        self.surf.set_colorkey(pg.Color("black"))
        

class Goal(object):
    def __init__(self, center_point):
        self.rect = pg.Rect(0, 0, 150, 30)
        self.rect.center = center_point

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color("gold3"), self.rect)

        
class Ball(object):
    def __init__(self, center_point):
        self.angle = pi * .3
        self.speed = 10.0
        self.max_speed = 15.0
        self.min_speed = 10.0  
        self.radius = 10
        self.pos = center_point
        self.rect = pg.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.rect.center = self.pos
        self.surf = pg.Surface((self.radius * 2, self.radius * 2)).convert()
        self.surf.fill(pg.Color("black"))
        self.surf.set_colorkey(pg.Color("black"))
        pg.draw.circle(self.surf, pg.Color("white"), (self.radius, self.radius), 15)
        
        
    def update(self, game):
        self.speed -= .01
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        elif self.speed < self.min_speed:
            self.speed = self.min_speed
        
        self.pos = project(self.pos, self.angle, self.speed)
        self.rect.center = self.pos
        projection = project(self.pos, self.angle, self.speed)            
        for bumper in game.bumpers:
            if bumper.rect.colliderect(self.rect):
                if bumper.rect.centery == game.screen_rect.centery:
                    self.angle = get_yaxis_reflection(self.pos, projection)
                else:
                    self.angle = get_xaxis_reflection(self.pos, projection)
        for paddle in game.paddles:
            if paddle.rect.colliderect(self.rect):
                to_ball = get_angle(paddle.rect.center, self.pos)
                if (paddle.tl_angle >= to_ball >= paddle.tr_angle
                                or paddle.bl_angle <= to_ball <= paddle.br_angle):
                    self.angle = get_xaxis_reflection(self.pos, projection)
                    self.angle -= paddle.english * paddle.bounce_mod

                else:
                    self.angle = get_yaxis_reflection(self.pos, projection)                 
                self.speed += abs(paddle.english)
                self.pos = project(self.pos, self.angle, self.speed)    
                    
    def draw(self, surface):
        self.rect.center = self.pos
        surface.blit(self.surf, self.rect)
        
class Paddle(object):
    def __init__(self, image, center_point, bounce_mod):
        self.image  = image
        self.rect = self.image.get_rect(center=center_point)
        self.pos = center_point
        self.speed = 8.0
        self.controlled = False
        self.velocity = 0
        self.tl_angle = get_angle(self.rect.center, self.rect.topleft)
        self.tr_angle = get_angle(self.rect.center, self.rect.topright)
        self.bl_angle = get_angle(self.rect.center, self.rect.bottomleft)
        self.br_angle = get_angle(self.rect.center, self.rect.bottomright) 
        self.bounce_mod = bounce_mod
        self.english = 0.0
        
    def update(self, ball, keys):
        if not self.controlled:
            rel_x = self.pos[0] - ball.pos[0]
            if abs(rel_x) > 80:
                try:
                    relative_x = rel_x / abs(rel_x)
                except ZeroDivisionError:
                    relative_x = -self.velocity
                    self.english = 0.0
                if self.velocity != -relative_x:
                    self.velocity = -relative_x
                else:
                    self.english += -relative_x * .1
                self.pos = (self.pos[0] + (self.velocity * self.speed),
                                 self.pos[1])    
            
            
            
        else:
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                self.velocity = -1
                self.english = max(-5, self.english - .1)
                
            elif keys[pg.K_RIGHT] or keys[pg.K_d]:
                self.velocity = 1
                self.english = min(self.english + .1, 5)
                   
            else:
                self.velocity = 0
                self.english = 0
            self.pos = (self.pos[0] + (self.velocity * self.speed),
                                self.pos[1])
        
                        
        
    def draw(self, surface):
        self.rect.center = self.pos
        surface.blit(self.image, self.rect)
        
        
class PySplash(tools._State):
    def __init__(self):
        super(PySplash, self).__init__()
        self.next = "SPLASH"
        screen = pg.display.get_surface().get_rect()        
        self.game_rect = screen.inflate(-40, -40)
        self.bumpers = [Bumper(*x) for x in [(0, 0, screen.w, 20),
                                                            (0, screen.h - 20, screen.w, 20),
                                                            (0, 0, 20, screen.h),
                                                            (screen.w - 20, 0, 20, screen.h)]]                                                            
        self.screen_rect = screen
        x_scale = screen.w / 1920.0
        y_scale = screen.h / 1080.0
        logos = [prepare.GFX["pygamepoweredlogo"],
                     prepare.GFX["pythonpoweredlogo"]]
        logos = [pg.transform.scale(logo, (int(logo.get_width() * x_scale), int(logo.get_height() * y_scale)))
                     for logo in logos]
        self.paddles = [Paddle(logos[0], (screen.centerx - 50, screen.top + 100), -.05),
                               Paddle(logos[1], (screen.centerx + 50, screen.bottom - 100), .05)]
        
        self.ball = Ball(screen.center)
        self.goals = [Goal(self.bumpers[0].rect.center), Goal(self.bumpers[1].rect.center)]
        self.dimmer = Dimmer(screen.size)
        
    def update(self, surface, keys, dt):
        for goal in self.goals:
            if goal.rect.colliderect(self.ball.rect):
                self.done = True
                return
        for paddle in self.paddles:
            paddle.update(self.ball, keys)
            clamped = paddle.rect.clamp(self.game_rect)
            if clamped != paddle.rect:
                paddle.rect = clamped
                paddle.pos = paddle.rect.center
        self.ball.update(self)    
           
        self.dimmer.update()
        if self.dimmer.done:
            self.done = True
        self.draw(surface)
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        for bumper in self.bumpers:
            pg.draw.rect(surface, pg.Color("steelblue4"), bumper)
        
        for paddle in self.paddles:
            paddle.draw(surface)
        for goal in self.goals:
            goal.draw(surface)
        self.ball.draw(surface)
        self.dimmer.draw(surface)
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_LEFT, pg.K_a):
                self.paddles[1].velocity = -1
                self.paddles[1].controlled = True
            elif event.key in (pg.K_RIGHT, pg.K_d):
                self.paddles[1].velocity = 1
                self.paddles[1].controlled = True
            elif event.key == pg.K_ESCAPE:
                self.done = True
    
        
    
    