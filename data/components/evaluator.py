from math import sin, cos
from itertools import cycle
from collections import OrderedDict
import pygame as pg
from .. import tools, prepare
from ..components.tiles import ListTile, StringTile
from ..components.labels import Label


class Evaluator(object):
    def __init__(self, leftbottom):
        self.machine = prepare.GFX["machine"]
        self.rect = self.machine.get_rect(bottomleft=leftbottom)
        self.wheels = cycle([prepare.GFX[x] for x in ("wheel1", "wheel2")])
        self.wheel = next(self.wheels)
        wheel_offset = prepare.SETTINGS[prepare.SCREEN_SIZE]["wheel offset"]
        self.wheel_rect = self.wheel.get_rect(topleft=(self.rect.left + wheel_offset[0],
                                                                            self.rect.top + wheel_offset[1]))
        self.snakes = cycle([prepare.GFX["snake" + x] for x in ("1", "3", "2", "3")])
        self.snake = next(self.snakes)
        self.snake_rect = self.snake.get_rect(midbottom=(self.wheel_rect.centerx, 
                                                                                  self.wheel_rect.bottom - 1))
        self.roller = prepare.GFX["roller"]
        self.roller_rect = self.roller.get_rect(bottomleft=self.rect.bottomright)
        self.roller_wheels = cycle([prepare.GFX["rollerwheels1"], prepare.GFX["rollerwheels2"]])
        self.roller_wheel = next(self.roller_wheels) 
        self.roller_wheel_rect = self.roller_wheel.get_rect(topleft=(self.roller_rect.left, self.roller_rect.top + 1))
        self.supports = prepare.GFX["supports"]
        self.support_rect = self.supports.get_rect(bottomleft=self.rect.bottomright)
        self.cover = pg.Rect(0, self.rect.top, self.rect.left, self.rect.height)
        
        self.state = "Waiting"
        self.result_tile = None
        self.send_speed = 2.5
        self.bonus_scores = {"super(MegaUberString)": 100,
                                       "super(UberString)": 50,
                                       "super(String)": 10,
                                       "Palindrome": 20,
                                       "WOW": 100,
                                       "Much Length": 50, 
                                       "Such Elements": 10}
        self.bonus_label = None
        self.slot = None
        
    def evaluate(self, tile):
        if "append" in tile.value:
            parts = tile.value.split(".append(")   
            val = eval(parts[0].lstrip("'").rstrip("'"))
            if "[" in parts[1]:
                val2 = eval(parts[1].rstrip("')").lstrip("'"))
            else:
                val2 = eval(parts[1].rstrip(")"))
            val.append(val2)
            result = val
        elif "+=" in tile.value:
            parts = tile.value.split(" += ")   
            val = eval(parts[0].lstrip("'").rstrip("'"))
            if "[" in parts[1]:
                val2 = eval(parts[1].rstrip("')").lstrip("'"))
            else:
                val2 = eval(parts[1].rstrip(")"))
            val.append(val2)
            result = val
        elif "extend" in tile.value:
            parts = tile.value.split(".extend(")
            val = eval(parts[0].lstrip("'").rstrip("'"))
            val2 = eval(parts[1].rstrip("')").lstrip("'"))
            val.extend(val2)
            result = val
        
        else:            
            try:
                result = eval(tile.value)
                
            except Exception as e:
                print(repr(e))
                print(e)
                result = None
        
        if result is not None:
            self.spit_result(result, tile)
            return True
    
    def check_for_bonuses(self):
        value = self.result_tile.value
        kind = self.result_tile.kind
        length = len(value)
        scores = OrderedDict(
                        [("super(MegaUberString)", kind == "string" and length > 1000),
                         ("super(UberString)", kind == "string" and length > 250),
                         ("super(String)", kind == "string" and length > 50),
                         ("WOW", kind == "list" and length > 1000),
                         ("Much Length", kind == "list" and length > 250),
                         ("Such Elements", kind == "list" and length > 50),
                         ("Palindrome", kind == "string" and length > 4 and value == value[::-1])])
        for k in scores:
            if scores[k]:
                self.result_tile.value = k
                center = pg.display.get_surface().get_rect().center
                self.bonus_label = Label(prepare.FONTS["Fixedsys500c"], 32, k, "steelblue4", {"center": center})
                self.bonus_label.text.set_alpha(50)                
                return True
                
    def update(self, game):
        if not game.ticks % 6:
            self.snake = next(self.snakes)
            self.wheel = next(self.wheels)
            self.roller_wheel = next(self.roller_wheels)
        if self.state == "Running":
            if self.run_ticks > 0:
                self.run_ticks -= 1
            else:
                self.state = "Spitting"
            
        elif self.state == "Spitting":
            self.result_tile.move((self.send_speed, 0))
            if (self.result_tile.rect.right > self.roller_rect.right
                 and self.result_tile.rect.left > self.rect.right + 5):
                if ((self.result_tile.kind == "string"
                     and self.result_tile.value in game.score_words)
                     or self.check_for_bonuses()):
                    self.angle = tools.get_angle(game.score_words_rect.center,
                                                              self.result_tile.rect.center)
                else:
                    open_slot = game.slot_board.get_empty_slot()
                    self.angle = tools.get_angle(open_slot.rect.center,
                                                              self.result_tile.rect.center)
                    self.slot = open_slot
                self.state = "Sending"
                
        elif self.state == "Sending":                                        
            self.result_tile.move((cos(self.angle) * self.send_speed * 4,
                                            sin(self.angle) * self.send_speed * 4))
            if self.slot and self.result_tile.rect.colliderect(self.slot.rect):
                self.result_tile.rect.center = self.slot.rect.center
                self.slot.tile = self.result_tile
                game.tiles.add(self.result_tile)
                self.slot = None
                self.angle = None
                self.result_tile = None
                self.bonus_label = None
                self.state = "Waiting"
            elif self.result_tile.rect.colliderect(game.score_words_rect):
                try:
                    game.score += game.score_words[self.result_tile.value]
                except KeyError:
                    game.score += self.bonus_scores[self.result_tile.value]
                self.result_tile.slot.tile = None
                self.angle = None
                self.slot = None
                self.result_tile = None
                self.bonus_label = None
                self.state = "Waiting"
        
    def spit_result(self, result, tile):
        klass = None
        if isinstance(result, list):
            klass = ListTile
        elif isinstance(result, str):
            klass = StringTile
        if klass:    
            new = klass(result, (self.roller_rect.left - 100, self.roller_rect.top - 20), tile.slot)
            new.rect.right = self.rect.right - 10
        tile.slot.tile = None
        tile.used = True
        self.result_tile = new
        self.state = "Running"
        self.run_ticks = 20
        
    def draw(self, surface):
        if self.result_tile:
            self.result_tile.draw(surface)
        pg.draw.rect(surface, pg.Color("black"), self.cover)
        surface.blit(self.machine, self.rect)
        surface.blit(self.snake, self.snake_rect)
        surface.blit(self.wheel, self.wheel_rect)
        surface.blit(self.roller, self.roller_rect)
        surface.blit(self.roller_wheel, self.roller_wheel_rect)
        surface.blit(self.supports, self.support_rect)
        if self.bonus_label:
            self.bonus_label.draw(surface)

        
        
    