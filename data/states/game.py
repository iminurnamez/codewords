
import pygame as pg
from .. import tools, prepare
from ..components.tiles import StringTile, ListTile, MaxTile, IndexTile, IncrementerTile
from .. components.evaluator import Evaluator
from ..components.tile_generator import TileGenerator
from ..components.slots import SlotBoard
from ..components.words import CODE_WORDS
from ..components.labels import Label, GroupLabel


class Game(tools._State):
    def __init__(self):
        super(Game, self).__init__()
        screen = pg.display.get_surface().get_rect()
        self.cursor = prepare.GFX["pythoncursor"]
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_visible = True
        
        
        self.tile_generator = TileGenerator()
        slot_width = prepare.SETTINGS[prepare.SCREEN_SIZE]["slot width"]
        self.slot_board = SlotBoard(pg.Rect(screen.right - slot_width,
                                                             screen.top, slot_width, prepare.SETTINGS[prepare.SCREEN_SIZE]["slot length"]))
        self.tiles = set()
        for slot in self.slot_board.slots:
            tile = self.tile_generator.generate(slot.rect.center, slot, self.tiles)

        self.current_tile = None
        self.evaluator = Evaluator(screen.bottomleft)
        self.trash_can = prepare.GFX["trashcan"]
        self.trash_rect = self.trash_can.get_rect(bottomright=screen.bottomright) 
        self.ticks = 0
        scores_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["score box size"]
        self.score_words = CODE_WORDS
        self.score_words_rect = pg.Rect((screen.left + 2, screen.top + 2), scores_size)
        top = self.score_words_rect.top + 5
        left = self.score_words_rect.left + 10
        right = self.score_words_rect.right -10
        self.font = prepare.FONTS["Fixedsys500c"]
        self.small_font = prepare.SETTINGS[prepare.SCREEN_SIZE]["sm font size"]
        self.large_font = prepare.SETTINGS[prepare.SCREEN_SIZE]["lg font size"]
        self.labels = []
        for word in self.score_words:
            label = GroupLabel(self.labels, self.font, self.small_font, word, "steelblue4",
                                         {"topleft": (left, top)})
            score_label = GroupLabel(self.labels, self.font, self.small_font, str(self.score_words[word]),
                                                  "gold3", {"topright": (right, top)})
            top += label.rect.height + 5
        self.score = 0
        score_center = (self.slot_board.rect.left - self.score_words_rect.left) // 2
        self.score_label = Label(self.font, self.large_font, "{}".format(self.score), "gold3",
                                           {"midtop": (score_center, 0)})
  
    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
            self.done =True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.quit = True
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.current_tile is None:
                for tile in self.tiles:
                    if tile.rect.collidepoint(event.pos):
                        self.current_tile = tile
                        self.cursor_visible = False
                        pg.mouse.set_pos(tile.rect.center)
                        break
            
        elif event.type == pg.MOUSEBUTTONUP:
            self.current_tile = None
            self.cursor_visible = True
        
    def update(self, surface, keys, dt):
        self.ticks += 1
        if self.evaluator.state == "Waiting":
            if len(self.tiles) < 30:
                open_slot = self.slot_board.get_empty_slot()
                new = self.tile_generator.generate(open_slot.rect.center, open_slot, self.tiles)
              
        if self.current_tile is not None:
            current = self.current_tile
            current.pos = pg.mouse.get_pos()
            current.rect.center = current.pos
            
            if self.evaluator.rect.colliderect(current.rect): 
                if self.evaluator.state == "Waiting": 
                    if self.evaluator.evaluate(current):
                        self.current_tile = None
            elif self.trash_rect.colliderect(current.rect):
                current.slot.tile = None
                current.used = True
                self.current_tile = None
                self.cursor_visble = True      
            else:
                for tile in {t for t in self.tiles.difference({current})
                                 if not t.rect.colliderect(self.slot_board.rect)}:
                    if tile.rect.colliderect(current.rect):
                        if tile.collide(current):
                            self.cursor_visible = True
                            self.current_tile = None
                            break
        
        self.tiles = {x for x in self.tiles if not x.used}        
        self.evaluator.update(self)
        self.score_label = Label(self.font, self.large_font, "{}".format(self.score), "gold3",
                                           {"midtop": (pg.display.get_surface().get_rect().centerx, 2)})

        self.draw(surface)
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        for slot in self.slot_board.slots:
            if slot.tile is None:
                color = "gold3"
            else:
                color = "steelblue4"
            pg.draw.rect(surface, pg.Color(color), slot.rect, 1)   
        pg.draw.rect(surface, pg.Color("gold3"), self.score_words_rect.inflate(2, 2), 4)
        pg.draw.rect(surface, pg.Color("steelblue4"), self.score_words_rect, 2)
        for tile in self.tiles:
            tile.draw(surface)
        self.evaluator.draw(surface)
        for label in self.labels:
            label.draw(surface)
        surface.blit(self.trash_can, self.trash_rect)
        pg.draw.rect(surface, pg.Color("red"), (pg.mouse.get_pos(), (4,4)))
        self.score_label.draw(surface)
        if self.cursor_visible:
            self.cursor_rect.center = pg.mouse.get_pos()
            surface.blit(self.cursor, self.cursor_rect)
