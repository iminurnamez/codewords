import pygame as pg
from .. import tools, prepare
#from ..prepare import GFX, SETTINGS, SCREEN_SIZE, FONTS, MUSIC, SFX
from ..components.tiles import Tile, StringTile, ListTile, MaxTile, IndexTile, IncrementerTile
from ..components.evaluator import Evaluator
from ..components.tile_generator import TileGenerator
from ..components.slots import SlotBoard
from ..components.words import CODE_WORDS
from ..components.labels import Label, GroupLabel


class Game(tools._State):
    def __init__(self):
        super(Game, self).__init__()
        
        screen = pg.display.get_surface().get_rect()
        self.screen_size = prepare.SCREEN_SIZE
        self.tile_generator = TileGenerator()
        self.slot_board = SlotBoard(30)
        self.tiles = set()
        for slot in self.slot_board.slots:
            tile = self.tile_generator.generate(slot.rect.center, slot, self.tiles)
            
        self.current_tile = None
        self.cursor_visible = True
        self.resize()
        pg.mixer.music.load(prepare.MUSIC["energy"])

    
    def startup(self, persistent):
        self.persist = persistent
        if pg.mixer.music.get_busy():
            if not self.persist["sounds"]:
                pg.mixer.music.stop()
        else:
            if self.persist["sounds"]:
                pg.mixer.music.play(-1)
        
        if self.screen_size != prepare.SCREEN_SIZE:
            Tile.font_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["font size"]
            self.resize()
            
            
    def resize(self):    
        size = "small" if prepare.SCREEN_SIZE in ((800, 600), (640, 480)) else ""
        screen = pg.display.get_surface().get_rect()
        self.screen_size = screen.size
        self.evaluator = Evaluator(screen.bottomleft)
        self.slot_board = SlotBoard(30)
        slots = self.slot_board.slots[::-1]
        for tile in self.tiles:
            tile.relabel()
            tile.slot = slots.pop()
            tile.pos = tile.slot.rect.center
            tile.rect.center = tile.pos
            tile.slot.tile = tile
        self.cursor = prepare.GFX["pythoncursor" + size]
        self.cursor_rect = self.cursor.get_rect()        
        self.trash_can = prepare.GFX["trashcan" + size]
        self.trash_rect = self.trash_can.get_rect(midbottom=(self.slot_board.rect.centerx,
                                                                                       screen.bottom - 5))                                                         
        self.help_icon = prepare.GFX["questionmark" + size]
        self.help_rect = self.help_icon.get_rect(topleft=(screen.left + 10, screen.top + 5))   
        self.settings_icon = prepare.GFX["gear" + size]
        self.settings_rect = self.settings_icon.get_rect(midleft=(self.help_rect.right + 20,
                                                                                          self.help_rect.centery))                                                                            
        scores_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["score box size"]
        self.score_words = CODE_WORDS
        self.score_words_rect = pg.Rect((screen.left + 2, self.help_rect.bottom + 5), scores_size)
        
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
        self.ticks = 0
        score_center = (self.slot_board.rect.left - self.score_words_rect.left) // 2
        self.score_label = Label(self.font, self.large_font, "{}".format(self.score), "gold3",
                                           {"midtop": (score_center, 0)})

        
    def dump_tiles(self):
        """Get rid of all untouched tiles and replace with new tiles"""
        to_remove = set()
        for tile in self.tiles:
            if not tile.handled:
                to_remove.add(tile)
                tile.slot.remove_tile()
        for slot in self.slot_board.slots:
            if not slot.tile:
                new_tile = self.tile_generator.generate(slot.rect.center,
                                                                          slot, self.tiles)
        self.tiles = self.tiles - to_remove
        self.score = max(0, self.score - 10)
        
    def get_event(self, event):
        if event.type == pg.QUIT:
            self.next = "EXITSCREEN"
            self.done =True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.next = "EXITSCREEN"
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.current_tile is None:
                if self.help_rect.collidepoint(event.pos):
                    self.next = "HELP"
                    self.done = True
                    return
                elif self.settings_rect.collidepoint(event.pos):
                    self.next = "OPTIONS"
                    self.done = True
                    return
                elif self.trash_rect.collidepoint(event.pos):
                    self.dump_tiles()
                elif self.evaluator.rect.collidepoint(event.pos):
                    self.evaluator.hurry()                
                for tile in self.tiles:
                    if tile.rect.collidepoint(event.pos):
                        self.current_tile = tile
                        self.cursor_visible = False
                        tile.handled = True
                        pg.mouse.set_pos(tile.rect.center)
                        break
        elif event.type == pg.MOUSEBUTTONUP:
            if self.current_tile is not None:
                current = self.current_tile
                current.pos = pg.mouse.get_pos()
                current.rect.center = current.pos
                for tile in {t for t in self.tiles.difference({current})
                                 if not t.rect.colliderect(self.slot_board.rect)}:
                    if tile.rect.colliderect(current.rect):
                        if tile.collide(current):
                            self.cursor_visible = True
                            self.current_tile = None
                            break
                else:
                    self.current_tile = None
                    self.cursor_visible = True
        
    def update(self, surface, keys, dt):
        self.ticks += 1
        if self.evaluator.state == "Waiting":
            if len(self.tiles) < self.slot_board.num_slots:
                open_slot = self.slot_board.get_empty_slot()
                new = self.tile_generator.generate(open_slot.rect.center,
                                                                   open_slot, self.tiles)
              
        if self.current_tile is not None:
            current = self.current_tile
            current.pos = pg.mouse.get_pos()
            current.rect.center = current.pos
            if self.evaluator.rect.colliderect(current.rect): 
                if self.evaluator.state == "Waiting": 
                    if self.evaluator.evaluate(current, self.persist["sounds"]):
                        self.current_tile = None
                        self.cursor_visible = True
            elif self.trash_rect.colliderect(current.rect):
                self.score = max(0, self.score - 1)
                current.slot.tile = None
                current.used = True
                self.current_tile = None
                self.cursor_visble = True      
            #else:
            #    for tile in {t for t in self.tiles.difference({current})
            #                     if not t.rect.colliderect(self.slot_board.rect)}:
            #        if tile.rect.colliderect(current.rect):
            #            if tile.collide(current):
            #                self.cursor_visible = True
            #                self.current_tile = None
            #                break
        
        self.tiles = {x for x in self.tiles if not x.used}
        self.evaluator.update(self)
        self.score_label = Label(self.font, self.large_font, "{}".format(self.score),
                                "gold3", {"midtop": (pg.display.get_surface().get_rect().centerx, 2)})
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
        surface.blit(self.settings_icon, self.settings_rect)
        surface.blit(self.help_icon, self.help_rect)
        self.score_label.draw(surface)
        if self.cursor_visible:
            self.cursor_rect.center = pg.mouse.get_pos()
            surface.blit(self.cursor, self.cursor_rect)
