import pygame as pg
from .. import prepare

class Slot(object):
    def __init__(self, rect):
        self.tile = None
        self.rect = rect
        
    def add_tile(self, tile):
        self.tile = tile
        self.tile.pos = self.rect.center
        self.tile.rect.center = self.rect.center
        
    def remove_tile(self):
        self.tile = None
        
        
class SlotBoard(object):
    def __init__(self, num_slots):
        self.num_slots = num_slots
        width = prepare.SETTINGS[prepare.SCREEN_SIZE]["slot width"]     
        height = prepare.SETTINGS[prepare.SCREEN_SIZE]["slot height"]
        self.rect = pg.Rect(0, 0, width, height * num_slots)
        self.rect.topright = pg.display.get_surface().get_rect().topright
        self.slots = [Slot(pg.Rect(self.rect.x, self.rect.y + (y * height), self.rect.w, height))
                          for y in range(num_slots)]
                 
    def get_empty_slot(self):
        for slot in self.slots:
            if slot.tile is None:
                return slot
                
    def update(self):
        for slot in self.slots:
            if (slot.tile is not None) and slot.tile.used:
                slot.tile = None