from random import choice, randint
from string import ascii_uppercase
from .tiles import (ListTile, StringTile, IndexTile, MaxTile, IncrementerTile,
                             MinTile, AppendTile, SliceTile, ExtendTile, JoinTile, SplitTile,
                             SortedTile, ReplaceTile, AdderTile, ListFuncTile, ShuffleTile,
                             ChoiceTile, ReversedTile, ReverseSortedTile)
from . import words

class TileGenerator(object):
    choices = ["list", "string", "method", "method", "function", "index", "slice"]
    letters = ascii_uppercase
    methods = [IncrementerTile, AdderTile, AppendTile, ExtendTile, JoinTile, SplitTile, ReplaceTile]
    functions = [MaxTile, MinTile, SortedTile, ReverseSortedTile, ReversedTile, ListFuncTile, ShuffleTile, ChoiceTile]
    indices = [0,0,0,0,1,1,1,2,2,3,4,-1,-1,-1,-2,-2,-3]
    slices = ["[::-1]", "[::-1]", "[1:]", "[1:]", "[2:]", "[3:]", "[-3]", "[:-2]", "[:-1]",
                 "[:-1]", "[::2]", "[::3]", "[1::2]", "[-1:]", "[-2:]", "[-3:]"]
    
    def generate(self, center_point, slot, tiles):
        selection = choice(self.choices)
        if selection == "list":
            num = randint(1, 5)
            values = [choice(self.letters) for _ in range(num)]
            new = ListTile(values, center_point, slot)
        elif selection == "string":
            new = StringTile(choice(words.WORDS), center_point, slot)
        elif selection == "index":
            new = IndexTile(choice(self.indices), center_point, slot)
        elif selection == "method":
            new = choice(self.methods)(center_point, slot)
        elif selection == "function":
            new = choice(self.functions)(center_point, slot)
        elif selection == "slice":
            value = choice(self.slices)
            new = SliceTile(value, center_point, slot)
        tiles.add(new)
        slot.add_tile(new)
        return new
