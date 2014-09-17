import pygame as pg
from .. import tools, prepare
from ..components.labels import Label, GroupLabel

class HelpScreen(tools._State):
    def __init__(self):
        super(HelpScreen, self).__init__()
        self.next = "GAME"
        
    def startup(self, persistent):    
        self.persist = persistent
        self.cursor = prepare.GFX["pythoncursor"]
        self.cursor_rect = self.cursor.get_rect()
        screen = pg.display.get_surface().get_rect()
        center = screen.centerx
        font = prepare.FONTS["Fixedsys500c"]        
        font_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["font size"]
        lg_font_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["lg font size"] // 2
        help_lines = ["Drag And Join Code To Assemble Snippets",
                            "Process Snippets In The Evalutron",
                            "Score Points By Creating Score Words",
                            "Get Bonus Points For Palindromes and Long Lists/Strings",
                            "Drag Code To Trashcan To Throw Away (-1 Point)",
                            "Click Trashcan To Dump All Untouched Code (-10 Points)"
                            ]                            
        controls = [("Left Click", "Grab/Drag Code"), ("ESCAPE", "Quit")]
        spacer = prepare.SCREEN_SIZE[1] // 20
        top = spacer
        self.labels = []
        title = GroupLabel(self.labels, font, lg_font_size, "help(Code Words)",
                                   "steelblue4", {"midtop": (center, top)})
        top += title.rect.height + (spacer // 2)
        for line in help_lines:
            label = GroupLabel(self.labels, font, font_size, line, "steelblue4",
                                        {"midtop": (center, top)})
            top += label.rect.height + (spacer // 2)
        top += spacer
        control_title = GroupLabel(self.labels, font, lg_font_size, "help(Controls)",
                                               "steelblue4", {"midtop": (center, top)})
        top += control_title.rect.height + spacer // 2
        for control, purpose in controls:
            c_label = GroupLabel(self.labels, font, font_size, control, "steelblue4",
                                        {"topright": (center - spacer, top)})
            p_label = GroupLabel(self.labels, font, font_size, purpose, "steelblue4",
                                             {"topleft": (center + spacer, top)})            
            top += label.rect.height + spacer
        end_label = GroupLabel(self.labels, font, font_size, "Click to Continue",
                                           "steelblue4", {"centerx": center, 
                                           "bottom": screen.bottom - (spacer)})        
    
    
    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.done = True        
        
    def draw(self, surface):
        surface.fill(pg.Color("gold3"))
        for label in self.labels:
            label.draw(surface)        
        self.cursor_rect.center = pg.mouse.get_pos()    
        surface.blit(self.cursor, self.cursor_rect)
        
    def update(self, surface, keys, dt):
        self.draw(surface)