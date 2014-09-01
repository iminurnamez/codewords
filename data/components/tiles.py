
import pygame as pg
from .. import prepare
from ..components.labels import Label

class Tile(object):
    font = prepare.FONTS["Fixedsys500c"]
    font_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["font size"]
    def __init__(self, value, kind, center_point, slot): 
        self.value = value
        self.kind = kind
        self.has_arg = False
        self.valid_args = set()
        self.used = False
        self.linkables = set()
        self.link = None
        if self.kind == "string":
            _value = "'{}'".format(self.value)
        else:
            _value = "{}".format(self.value)
        self.label = Label(self.font, self.font_size, _value, "white",
                                  {"center": center_point})
        self.rect = self.label.rect
        self.pos = center_point
        self.slot = slot
            
    def collide(self, other):
        pass
        
    def relabel(self):
        self.label = Label(self.font, self.font_size, self.value, "white", 
                                  {"center": self.rect.center})
        self.rect = self.label.rect
        
    def move(self, offset):
        self.pos = (self.pos[0] + offset[0],
                         self.pos[1] + offset[1])
        self.rect.center = self.pos
    
    def draw(self, surface):
        self.label.draw(surface)   
        
        
class ListTile(Tile):
    def __init__(self, value, center_point, slot):
        super(ListTile, self).__init__(value, "list", center_point, slot)
        self.linkables = {"index", "append", "extend", "incrementer",
                                 "pop", "remove", "slice"}
        
    def collide(self, other):
        print "self.kind: ", self.kind
        print "self.link: ", self.link
        print "self.has_arg: ", self.has_arg
        print "other.kind: ", other.kind
        print "other.link: ", other.link
        print "other.has_arg: ", other.has_arg
        used = False
        if self.link is None:
            if other.kind in self.linkables:
                self.value = "{}{}".format(self.value, other.value)
                self.link = other.kind
                used = True
                if other.has_arg:
                    self.link = "full"
        elif other.kind == "string":
            if self.link == "append":
                self.value = "{}'{}')".format(self.value.rstrip(")"), other.value)
                used = True
            elif self.link == "remove":
                self.value = "{}.remove('{}')".format(self.value, other.value)
                used = True
        elif other.kind == "list":
            if self.link == "append" and not any((self.has_arg, other.link is not None)):
                self.value = "{}{})".format(self.value.rstrip(")"), other.value)
                used = True
            elif self.link == "extend" and not any((self.has_arg, other.link is not None)):
                self.value = "{}{})".format(self.value.rstrip(")"), other.value)
                self.has_arg = True
                used = True
            elif self.link == "incrementer":
                self.value = "{}{}".format(self.value, other.value)
                used = True
        elif other.kind == "slice":
            if self.link == "slice":
                self.value = "{}{}".format(self.value, other.value)
                used = True
        
        if used:
            other.used = True
            other.slot.tile = None
            self.relabel()
            return True            
            
        
class StringTile(Tile):
    def __init__(self, value, center_point, slot):
        super(StringTile, self).__init__(value, "string", center_point, slot)
        self.linkables = {"split", "rstrip", "lstrip", "incrementer",
                                 "index", "slice", "join", "replace"}

    def collide(self, other):
        used = False
        if self.link is None:
            if other.kind in self.linkables:
                if other.kind == "join":
                    self.value = "'{}'{}".format(self.value, other.value.lstrip("''"))
                    self.link = other.kind
                elif other.kind == "replace":
                    if other.has_second_arg:
                        print "1"
                        self.value = "'{}'{}".format(self.value, other.value.lstrip("''"))
                        self.link = "full"
                        self.has_arg = True
                        
                    elif other.has_arg:
                        self.value = "'{}'{}".format(self.value, other.value.lstrip("''"))
                        self.link = other.kind
                        self.has_arg = True
                        print "2"
                    else:
                        self.value = "'{}'{}".format(self.value, other.value.lstrip("''"))
                        self.link = other.kind
                        print "3"
                #elif other.kind == "split":
                #    self.value = "'{}'{}".format(self.value, other.value.lstrip("''"))
                #    self.link = other.kind
                else:
                    self.value = "'{}'{}".format(self.value, other.value)
                    self.link = other.kind
                    if other.has_arg:
                        self.link = "full"
                
                used = True
                
        elif other.kind == "string":
            if self.link in ("incrementer"):
                self.value = "{} + '{}'".format(self.value.rstrip(" + "), other.value)
                used = True
            elif self.link == "split":
                self.value = "{}'{}')".format(self.value.rstrip("' ')"), other.value)
                used = True
            elif self.link == "replace":
                if self.has_arg: 
                    print "1A"
                    self.value = "{}, '{}')".format(self.value.rstrip(")"), other.value)
                    self.link = "full"
                    used = True
                else:
                    print "2A"
                    self.value = "{}'{}')".format(self.value.rstrip(")"), other.value)
                    self.has_arg = True
                    used = True
            elif self.link == "join":
                if other.link == "join":
                    self.value = "{}{})".format(self.value.rstrip(")"), other.value)
                else:
                    self.value = "{}'{}')".format(self.value.rstrip(")"), other.value)
                self.has_arg = True
                used = True
                self.link = "full"                
        elif other.kind == "list":
            if self.link == "join":
                self.value = "{}{})".format(self.value.rstrip(")"), other.value)
                used = True
        elif other.kind == "slice":
            if self.link in ("slice"):
                self.value == "{}{}".format(self.value, other.value)
        
        if used:
            other.used = True
            other.slot.tile = None
            self.relabel()
            return True            
            
class IndexTile(Tile):
    def __init__(self, value, center_point, slot):
        super(IndexTile, self).__init__(value, "index", center_point, slot)    
        
class IncrementerTile(Tile):
    def __init__(self, center_point, slot):
        super(IncrementerTile, self).__init__(" + ", "incrementer", center_point, slot)
        
    
    
class MaxTile(Tile):
    def __init__(self, center_point, slot):
        super(MaxTile, self).__init__("max()", "max", center_point, slot)
        self.valid_args = {"list", "string"}
        
    def collide(self, other):
        if other.kind in self.valid_args and not self.has_arg:
            if other.link is None:
                self.add_argument(other)
                return True
                
    def add_argument(self, other):
        if other.kind == "list":
            self.value = "max({})".format(other.value)
        elif other.kind == "string":
            self.value = "max('{}')".format(other.value)
        self.has_arg = True
        other.used = True
        other.slot.tile = None
        self.relabel()

        
        
class MinTile(Tile):
    def __init__(self, center_point, slot):
        super(MinTile, self).__init__("min()", "min", center_point, slot)
        self.valid_args = {"list", "string"}
        
    def collide(self, other):
        if other.kind in self.valid_args and not self.has_arg:
            self.add_argument(other)
            return True
        
    def add_argument(self, other):
        if other.kind == "list":
            self.value = "min({})".format(other.value)
        elif other.kind == "string":
            self.value = "min('{}')".format(other.value)
        self.has_arg = True
        other.used = True
        other.slot.tile = None
        self.relabel()
        
        
class AppendTile(Tile):
    def __init__(self, center_point, slot):
        super(AppendTile, self).__init__(".append()", "append", center_point, slot)
        self.valid_args = {"list", "string"}
        
    def collide(self, other):
        used = False
        if (other.kind in self.valid_args
             and not self.has_arg
             and other.link is None):
            self.add_argument(other)
            return True
            
    def add_argument(self, other):    
        if other.kind == "list":
            self.value = ".append({})".format(other.value)
        elif other.kind == "string":
            self.value = ".append('{}')".format(other.value)
        self.has_arg = True
        other.used = True
        other.slot.tile = None
        self.relabel()   

class ExtendTile(Tile):
    def __init__(self, center_point, slot):
        super(ExtendTile, self).__init__(".extend()", "extend", center_point, slot)
        self.valid_args = {"list", "string"}
        
    def collide(self, other):
        used = False
        if other.kind in self.valid_args and not self.has_arg:
            self.add_argument(other)
            return True
            
    def add_argument(self, other):    
        if other.kind == "list":
            self.value = ".extend({})".format(other.value)
            self.has_arg = True
            other.used = True
            other.slot.tile = None
            self.relabel()           
        

class JoinTile(Tile):
    def __init__(self, center_point, slot):
        super(JoinTile, self).__init__("''.join()", "join", center_point, slot)
        self.valid_args = {"list"}
         
    def collide(self, other):
        if other.kind in self.valid_args and not self.has_arg:
            self.add_argument(other)
            return True
            
    def add_argument(self, other):
        if other.kind == "list":
            self.value = "{}{})".format(self.value.rstrip(")"), str(other.value))
            self.has_arg = True
            other.used = True
            other.slot.tile = None
            self.relabel()
        
class SliceTile(Tile):
    def __init__(self, value, center_point, slot):
        super(SliceTile, self).__init__(value, "slice", center_point, slot)
    
    
class SplitTile(Tile):
    def __init__(self, center_point, slot):
        super(SplitTile, self).__init__(".split()", "split", center_point, slot)
        self.valid_args = {"string"}
        
    def  collide(self, other):
        if other.kind in self.valid_args and not self.has_arg:
            self.add_argument(other)
            return True

    def add_argument(self, other):
            self.value = "{}'{}')".format(self.value.rstrip(")"), other.value)
            self.has_arg = True
            other.used = True
            other.slot.tile = None
            self.relabel()
        
class SortedTile(Tile):
    def __init__(self, center_point, slot):
        super(SortedTile, self).__init__("sorted()", "sorted", center_point, slot)
        self.valid_args = {"list", "string"}
        
    def collide(self, other):
        if other.kind in self.valid_args and not self.has_arg:
            self.add_argument(other)
            return True
            
    def add_argument(self, other):
        if other.kind == "string" and other.link is None:
            self.value = "{}'{}')".format(self.value.rstrip(")"), other.value)
        else:
            self.value = "{}{})".format(self.value.rstrip(")"), other.value)
        self.has_arg = True
        other.used = True
        other.slot.tile = None
        self.relabel()
    
    
#class ListFuncTile(Tile):
#    def __init__(
   
#class RemoveTile

class ReplaceTile(Tile):
    def __init__(self, center_point, slot):
        super(ReplaceTile, self).__init__(".replace()", "replace", center_point, slot)
        self.valid_args = {"string"}
        self.has_second_arg = False
         
    def collide(self, other):
        if other.kind in self.valid_args and not self.has_second_arg:
            self.add_argument(other)
            return True
            
    def add_argument(self, other):
        if self.has_arg:
            self.value = "{}, '{}')".format(self.value.rstrip(")"), other.value)
            self.has_second_arg = True
        else:
            self.value = "{}'{}')".format(self.value.rstrip(")"), other.value)
            self.has_arg = True
        other.used = True
        other.slot.tile = None
        self.relabel()

#class ShuffleTile
 
    
    
    
    