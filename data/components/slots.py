import pygame as pg
from .. import prepare

class Slot(object):
    def __init__(self, rect):
        self.tile = None
        self.rect = rect
        
    def add_tile(self, tile):
        self.tile = tile
        
    def remove_tile(self):
        self.tile = None
        
        
class SlotBoard(object):
    def __init__(self, rect):
        self.rect = rect
        slot_height = prepare.SETTINGS[prepare.SCREEN_SIZE]["slot height"]
        self.slots = [Slot(pg.Rect(self.rect.x, self.rect.y + y, self.rect.w, slot_height))
                          for y in range(0, self.rect.height, slot_height)]
                 
    def get_empty_slot(self):
        for slot in self.slots:
            if slot.tile is None:
                return slot
                
    def update(self):
        for slot in self.slots:
            if (slot.tile is not None) and slot.tile.used:
                slot.tile = None