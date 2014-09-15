from math import sin, cos
from random import choice
from itertools import cycle
from collections import OrderedDict
import pygame as pg
from .. import prepare
from ..tools import get_angle
from ..components.tiles import ListTile, StringTile
from ..components.labels import Label
from ..components.words import CODE_WORDS


class Evaluator(object):
    def __init__(self, leftbottom):
        self.state = "Waiting"
        self.result_tile = None
        self.send_speed = 2.5
        self.score_words = CODE_WORDS
        self.bonus_scores = {"len(42)": 42,
                                       "super(MegaUberString)": 100,
                                       "super(UberString)": 50,
                                       "super(String)": 10,
                                       "Palindrome": 20,
                                       "WOW": 100,
                                       "Much Length": 50, 
                                       "Such Elements": 10}

        self.hum = prepare.SFX["hum"]
        self.bells = [pg.mixer.Sound(prepare.SFX["bell" + str(x)]) for x in range(1, 4)]
        
        
        self.resize(leftbottom)
    
    
    def resize(self, leftbottom):
        size = "small" if prepare.SCREEN_SIZE in ((800, 600), (640, 480)) else ""    
        self.machine = prepare.GFX["machine" + size]
        self.rect = self.machine.get_rect(bottomleft=leftbottom)
        self.wheels = cycle([prepare.GFX[x + size] for x in ("wheel1", "wheel2")])
        self.wheel = next(self.wheels)
        wheel_offset = prepare.SETTINGS[prepare.SCREEN_SIZE]["wheel offset"]
        self.wheel_rect = self.wheel.get_rect(topleft=(self.rect.left + wheel_offset[0],
                                                                            self.rect.top + wheel_offset[1]))
        self.snakes = cycle([prepare.GFX["snake" + x + size] for x in ("1", "3", "2", "3")])
        self.snake = next(self.snakes)
        self.snake_rect = self.snake.get_rect(midbottom=(self.wheel_rect.centerx, 
                                                                                  self.wheel_rect.bottom - 1))
        self.door = prepare.GFX["door" + size]
        self.door_rect = self.door.get_rect(topleft=(self.wheel_rect.left + 1,
                                                                        self.wheel_rect.top))
        self.roller = prepare.GFX["roller" + size]
        self.roller_rect = self.roller.get_rect(bottomleft=self.rect.bottomright)
        self.roller_wheels = cycle([prepare.GFX["rollerwheels1" + size],
                                               prepare.GFX["rollerwheels2" + size]])
        self.roller_wheel = next(self.roller_wheels) 
        self.roller_wheel_rect = self.roller_wheel.get_rect(topleft=(self.roller_rect.left,
                                                                                              self.roller_rect.top + 1))
        self.supports = prepare.GFX["supports" + size]
        self.support_rect = self.supports.get_rect(bottomleft=self.rect.bottomright)
        self.cover = pg.Rect(0, self.rect.top, self.rect.left, self.rect.height)
        self.consoles = cycle([prepare.GFX["console" + str(x) + size] for x in range(1, 7)])
        self.console = next(self.consoles)
        
        console_offset = prepare.SETTINGS[prepare.SCREEN_SIZE]["console offset"]
        self.console_rect = self.console.get_rect(topleft=(self.rect.left + console_offset[0],
                                                                                self.rect.top + console_offset[1]))

    def reset(self):
        self.angle = None
        self.result_tile = None
        self.state = "Waiting"

    def evaluate(self, tile, sounds_on):
        result = tile.evaluate()
        if result is not None:
            if sounds_on:
                self.hum.play()
            self.result_tile = self.spit_result(result, tile)
            tile.used = True
            self.state = "Running"
            self.run_ticks = 160
            return True
    
    def check_for_bonuses(self, kind, value):
        length = len(value)
        bonuses = OrderedDict(
                    [("len(42)", kind in ("string", "list") and len(value) == 42),
                     ("super(MegaUberString)", kind == "string" and length > 1000),
                     ("super(UberString)", kind == "string" and length > 250),
                     ("super(String)", kind == "string" and length > 50),
                     ("WOW", kind == "list" and length > 1000),
                     ("Much Length", kind == "list" and length > 200),
                     ("Such Elements", kind == "list" and length > 50),
                     ("Palindrome", kind == "string" and length > 4 and value == value[::-1])
                     ])
        for k in bonuses:
            if bonuses[k]:
                return k
                
    def update(self, game):
        if not game.ticks % 6:
            self.console = next(self.consoles)
        if self.state != "Waiting" and not game.ticks % 6:
            self.snake = next(self.snakes)
            self.wheel = next(self.wheels)
            self.roller_wheel = next(self.roller_wheels)
        
        if self.state == "Running":
            self.run_ticks -= 1
            if not self.run_ticks:
                self.state = "Spitting"
            
        elif self.state == "Spitting":
            self.result_tile.move((self.send_speed, 0))
            rect = self.result_tile.rect
            if rect.right > self.roller_rect.right and rect.left > self.rect.right + 5:
                if self.result_tile.kind == "string" and (self.result_tile.value in self.score_words
                                                                          or self.result_tile.value in self.bonus_scores):
                    self.angle = get_angle(self.result_tile.rect.center,
                                                      game.score_words_rect.center)
                else:
                    self.angle = get_angle(self.result_tile.rect.center,
                                                      self.result_tile.slot.rect.center)
                self.state = "Sending"
                
        elif self.state == "Sending":                                        
            self.result_tile.move((cos(self.angle) * self.send_speed * 4,
                                            -sin(self.angle) * self.send_speed * 4))
            
            if self.result_tile.slot.rect.collidepoint(self.result_tile.rect.center):
                self.result_tile.slot.add_tile(self.result_tile)
                game.tiles.add(self.result_tile)
                self.reset()
            
            elif game.score_words_rect.collidepoint(self.result_tile.rect.center):
                try:
                    game.score += game.score_words[self.result_tile.value]
                except KeyError:
                    game.score += self.bonus_scores[self.result_tile.value]
                if game.persist["sounds"]:
                    choice(self.bells).play()
                self.result_tile.slot.remove_tile()
                self.reset()
                
        
    def spit_result(self, result, tile):
        new = None
        bonus = None
        if isinstance(result, list):
            bonus = self.check_for_bonuses("list", result)
            if not bonus:
                new = ListTile(result, (0, self.roller_rect.top - 20), tile.slot)
                new.rect.right = self.rect.right - 10
                return new
        elif isinstance(result, str):
            bonus = self.check_for_bonuses("string", result)
            new = StringTile(result, (0, self.roller_rect.top - 20), tile.slot)
        if bonus or result in self.score_words:
            result = bonus if bonus else result
            new = StringTile(result, (0, self.roller_rect.top - 20), tile.slot,
                                     "steelblue4")      
        if new: 
            new.rect.right = self.rect.right - 10    
        return new    
        
    def draw(self, surface):
        if self.result_tile:
            self.result_tile.draw(surface)
        pg.draw.rect(surface, pg.Color("black"), self.cover)
        surface.blit(self.machine, self.rect)
        surface.blit(self.console, self.console_rect)
        if self.state == "Waiting":
            surface.blit(self.door, self.door_rect)
        else:
            surface.blit(self.snake, self.snake_rect)
            surface.blit(self.wheel, self.wheel_rect)
        surface.blit(self.roller, self.roller_rect)
        surface.blit(self.roller_wheel, self.roller_wheel_rect)
        surface.blit(self.supports, self.support_rect)
        
        
    