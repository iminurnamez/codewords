import random
import pygame as pg
from .. import prepare
from ..components.labels import Label


def my_join(joiner, joinee=None):
    if joinee is None:
        return "".join(joiner)
    else:    
        return joiner.join(joinee)

def my_replace(string_, other_string, replacer):
    return string_.replace(other_string, replacer)
    
def my_split(string_, splitter=None):
    return string_.split(splitter)
    
def my_append(list_, string_):
    list_.append(string_)
    return list_
    
def my_extend(list_, other_list):
    list_.extend(other_list)
    return list_

def my_slicer(subject, slicer):
    return subject[slicer]
    
def my_slice(args):
    result = args[0]
    for slicer in args[1:]:
        result = my_slicer(result, slicer)
    return result  
            
def my_adder(first, second):
    return first + second

def my_incrementer(first, second):
    first += second
    return first
    
def my_shuffle(list_):
    random.shuffle(list_)
    return list_
    
def my_choice(iterable):
    return random.choice(iterable)
    
def my_reverse_sorted(iterable):
    return sorted(iterable, reverse=True)
    
def my_reversed(iterable):
    return list(reversed(iterable))
    

    
class Tile(object):
    font = prepare.FONTS["Fixedsys500c"]
    font_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["font size"]
    
    def __init__(self, value, kind, center_point, slot, color="white"): 
        self.value = value
        self.kind = kind
        self.color = color
        self.args = []
        self.valid_args = set() 
        self.used = False
        self.handled = False
        self.linkables = set()
        self.link = None
        self.method = None
        self.function = None
        if self.kind == "string":
            self.text = "'{}'".format(self.value)
        else:
            self.text = "{}".format(self.value)
        self.label = Label(self.font, self.font_size, self.text, self.color,
                                  {"center": center_point})
        self.rect = self.label.rect
        self.pos = center_point
        self.slot = slot
        
    def collide(self, other):
        pass
        
    def relabel(self):
        self.label = Label(self.font, self.font_size, self.text, self.color, 
                                  {"center": self.rect.center})
        self.rect = self.label.rect
        
    def move(self, offset):
        self.pos = (self.pos[0] + offset[0],
                        self.pos[1] + offset[1])
        self.rect.center = self.pos
    
    def draw(self, surface):
        self.label.draw(surface)   
        
        
class ListTile(Tile):
    def __init__(self, value, center_point, slot, color="white"):
        super(ListTile, self).__init__(value, "list", center_point, slot, color)
        self.linkables = {"index", "slice"}
        self.valid_methods = {"append", "extend", "incrementer",
                                         "pop", "remove", "adder"}
    def collide(self, other):
        used = False
        if self.link is None:
            if other.kind in self.linkables:
                self.link = other.kind
                if not self.args:
                    self.args = [self.value] 
                self.args.append(other.value)
                self.text = "{}{}".format(self.text, other.text)
                used = True
            elif other.kind in self.valid_methods:
                self.link = other.kind
                self.method = other.function
                self.args = [self.value] + other.args
                self.text = "{}{}".format(self.text, other.text)
                used = True
        
        elif other.kind == "string" and other.link is None:
            if self.link == "append" and len(self.args) < 2:
                self.text = "{}{})".format(self.text.rstrip(")"), other.text)
                self.args.append(other.value)
                used = True
            elif self.link == "remove" and len(self.args) < 2:
                self.text = "{}{}".format(self.text.rstrip(")"), other.text)
                self.args.append(other.value)
                used = True
            elif self.link in ("adder", "incrementer") and len(self.args) < 2:
                self.text = "{}{}".format(self.text, other.text)
                self.args.append(other.value)
                used = True
        
        elif other.kind == "list" and other.link is None:
            if self.link == "extend" and len(self.args) < 2:
                self.text = "{}{})".format(self.text.rstrip(")"), other.text)
                self.args.append(other.value)
                used = True
            elif self.link in ("adder", "incrementer") and len(self.args) < 2:
                self.text = "{}{}".format(self.text, other.text)
                self.args.append(other.value)
                used = True                

        if used:
            other.used = True
            other.slot.tile = None
            self.relabel()
            return True            
            
    def evaluate(self):
        result = None
        try:       
            if self.link in ("slice", "index"):
                result = my_slice(self.args)
                if self.link == "index":
                    if result == [] or result == "":
                        result = None
                    else:
                        result = result[0]        
                    
            elif self.method:
                result = self.method(*self.args) 
        except Exception as e:
            pass
        return result

        
class StringTile(Tile):
    def __init__(self, value, center_point, slot, color="white"):
        super(StringTile, self).__init__(value, "string", center_point, slot, color)
        self.linkables = {"slice", "index"}
        self.valid_methods = {"join", "replace", "split", "adder", "incrementer"}

    def collide(self, other):
        used = False
        if self.link is None:
            if other.kind in self.linkables:
                self.link = other.kind
                self.args = (self.value, other.value)
                self.text = "{}{}".format(self.text, other.text)
                used = True
            elif other.kind in self.valid_methods:
                self.link = other.kind
                self.method = other.function
                if other.kind in ("adder", "incrementer"):
                    self.args = [self.value] 
                else:
                    self.args = [self.value] + other.args
                if other.kind == "join":
                    self.text = "{}{}".format(self.text, other.text.lstrip("''"))
                elif other.kind == "replace":
                    self.text = "{}{}".format(self.text, other.text)
                else:
                    self.text = "{}{}".format(self.text, other.text)
                used = True
        
        elif other.kind == "string" and other.link is None:
            if self.link == "split" and len(self.args) < 2:
                self.args.append(other.value)        
                self.text = "{}{})".format(self.text.rstrip(")"), other.text)
                used = True
            elif self.link == "replace" and len(self.args) < 3:
                self.args.append(other.value)
                if len(self.args) < 3:
                    self.text = "{}{}, )".format(self.text.rstrip(")"), other.text)
                else:
                    self.text = "{}{})".format(self.text.rstrip(")"), other.text)
                used = True
            elif self.link in ("adder", "incrementer") and len(self.args) < 2:
                self.args.append(other.value)
                self.text = "{}{}".format(self.text, other.text)
                used = True
            elif self.link == "join" and len(self.args) < 2:
                self.args.append(other.value)
                self.text = "{}{})".format(self.text.rstrip(")"), other.text)
                used = True
        elif other.kind == "list" and other.link is None:
            if self.link == "join":
                self.args.append(other.value)
                self.text = "{}{})".format(self.text.rstrip(")"), other.text)
                used = True
        
        if used:
            other.used = True
            other.slot.tile = None
            self.relabel()
            return True       
    
    def evaluate(self):
        result = None
        try:
            if self.method:
                result = self.method(*self.args)        
            elif self.link in ("slice", "index"):
                result = my_slice(self.args)    
        except:
            pass
        return result

            
class IndexTile(Tile):
    def __init__(self, value, center_point, slot, color="white"):
        super(IndexTile, self).__init__(value, "index", center_point, slot, color)
        self.text = "[{}]".format(self.value)
        self.relabel()
        self.rect = self.label.rect
        
        if self.value == -1:
            self.value = slice(self.value, None)
        else:    
            self.value = slice(self.value, self.value + 1)
        
        
class SliceTile(Tile):
    def __init__(self, value, center_point, slot, color="white"):
        super(SliceTile, self).__init__(value, "slice", center_point, slot, color)
        self.text = self.value
        self.relabel()
        self.rect = self.label.rect
        
        slicers = []
        stripped = self.text.strip("[]")
        for x in stripped.split(":"):
            if x:
                slicers.append(int(x))
            else:
                slicers.append(None)
        self.value = slice(*slicers)
        
        
class AdderTile(Tile):
    def __init__(self, center_point, slot, color="white"):
        super(AdderTile, self).__init__(" + ", "adder", center_point, slot, color)
        self.text = self.value
        self.relabel()
        self.rect = self.label.rect
        self.function = my_incrementer
    
    def collide(self, other):
        pass
        
        
class IncrementerTile(Tile):
    def __init__(self, center_point, slot, color="white"):
        super(IncrementerTile, self).__init__(" += ", "incrementer", center_point, slot, color)
        self.text = self.value
        self.relabel()
        self.rect = self.label.rect
        self.function = my_incrementer
        
    def collide(self, other):
        pass


        

class MethodTile(Tile):
    def __init__(self, value, kind, center_point, slot, color):
        super(MethodTile, self).__init__(value, kind, center_point, slot, color)
        
    def collide(self, other):
        if (other.kind in self.valid_args
                    and not self.args
                    and other.link is None):
            self.text = "{}{})".format(self.text.rstrip(")"), other.text)
            self.args.append(other.value)
            other.used = True
            other.slot.tile = None
            self.relabel()   
            return True
     
    def evaluate(self):
        pass    
        
class AppendTile(MethodTile):
    def __init__(self, center_point, slot, color="white"):
        super(AppendTile, self).__init__(".append()", "append", center_point, slot, color)
        self.function = my_append
        self.valid_args = {"list", "string"}

            
class ExtendTile(MethodTile):
    def __init__(self, center_point, slot, color="white"):
        super(ExtendTile, self).__init__(".extend()", "extend", center_point, slot, color)
        self.function = my_extend
        self.valid_args = {"list", "string"}
 
        
class JoinTile(MethodTile):
    def __init__(self, center_point, slot, color="white"):
        super(JoinTile, self).__init__("''.join()", "join", center_point, slot, color)
        self.function = my_join
        self.valid_args = {"list"}
         
    def evaluate(self):
        try:
            return self.function(*self.args)
        except:
            return
            
            
class ReplaceTile(MethodTile):
    def __init__(self, center_point, slot, color="white"):
        super(ReplaceTile, self).__init__(".replace()", "replace", center_point, slot, color)
        self.function = my_replace
        self.valid_args = {"string"}
         
    def collide(self, other):
        if other.kind in self.valid_args and len(self.args) < 2:
            self.args.append(other.value)
            other.used = True
            other.slot.tile = None
            self.relabel()
            return True

            
class SplitTile(MethodTile):
    def __init__(self, center_point, slot, color="white"):
        super(SplitTile, self).__init__(".split()", "split", center_point, slot, color)
        self.function = my_split
        self.valid_args = {"string"}
        


            
class FunctionTile(Tile):
    def __init__(self, value, kind, center_point, slot, color):
        super(FunctionTile, self).__init__(value, kind, center_point, slot, color)

    def collide(self, other):
        if (other.kind in self.valid_args
            and not self.args
            and other.link is None):
            self.args = other.value
            self.text = "{}{})".format(self.text.rstrip(")"), other.text)
            other.used = True
            other.slot.tile = None
            self.relabel()
            return True
    
    def evaluate(self):
        try:
            return self.function(self.args)
        except:
            return
        
class MaxTile(FunctionTile):
    def __init__(self, center_point, slot, color="white"):
        super(MaxTile, self).__init__("max()", "max", center_point, slot, color)
        self.valid_args = {"list", "string"}
        self.function = max
        
        
class MinTile(FunctionTile):
    def __init__(self, center_point, slot, color="white"):
        super(MinTile, self).__init__("min()", "min", center_point, slot, color)
        self.text = self.value
        self.valid_args = {"list", "string"}
        self.function = min

        
class SortedTile(FunctionTile):
    def __init__(self, center_point, slot, color="white"):
        super(SortedTile, self).__init__("sorted()", "sorted", center_point, slot, color)
        self.valid_args = {"list", "string"}
        self.function = sorted
        

class ReverseSortedTile(FunctionTile):
    def __init__(self, center_point, slot, color="white"):
        super(ReverseSortedTile, self).__init__("sorted(reverse=True)", "sorted", center_point, slot, color)
        self.valid_args = {"list", "string"}
        self.function = my_reverse_sorted
        
    def collide(self, other):
        if (other.kind in self.valid_args
            and not self.args
            and other.link is None):
            self.args = other.value
            self.text = "{}{}, reverse=True)".format(self.text.rstrip("reverse=True)"), other.text)
            other.used = True
            other.slot.tile = None
            self.relabel()
            return True
            
            
class ListFuncTile(FunctionTile):
    def __init__(self, center_point, slot, color="white"):
        super(ListFuncTile, self).__init__("list()", "listfunc", center_point, slot, color)
        self.valid_args = {"list", "string"}
        self.function = list


class ReversedTile(FunctionTile):
    def __init__(self, center_point, slot, color="white"):
        super(ReversedTile, self).__init__("reversed()", "reversed", center_point, slot, color)
        self.valid_args = {"list", "string"}
        self.function = my_reversed
   
   
class ShuffleTile(FunctionTile):
    def __init__(self, center_point, slot, color="white"):
        super(ShuffleTile, self).__init__("random.shuffle()", "shuffle", center_point, slot, color)
        self.valid_args = {"list"}
        self.function = my_shuffle

  
class ChoiceTile(FunctionTile):
    def __init__(self, center_point, slot, color="white"):
        super(ChoiceTile, self).__init__("random.choice()", "choice", center_point, slot, color)
        self.valid_args = {"list", "string"}
        self.function = my_choice      
        
  