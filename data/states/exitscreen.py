import pygame as pg
from .. import tools, prepare
from ..components.labels import GroupLabel

class ExitScreen(tools._State):
    def __init__(self):
        super(ExitScreen, self).__init__()
     
    def startup(self, persistent):    
        pg.mixer.music.stop()
        self.persist = persistent
        self.cursor = prepare.GFX["pythoncursor"]
        self.cursor_rect = self.cursor.get_rect()
        screen = pg.display.get_surface().get_rect()
        center = screen.centerx
        font = prepare.FONTS["Fixedsys500c"]        
        font_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["font size"]
        lg_font_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["lg font size"] // 2
        spacer = prepare.SCREEN_SIZE[1] // 20
        top = spacer * 3
        text_lines = ["if you enjoyed this game:",
                            "    please consider supporting Python",
                            "    the FREE and OPEN SOURCE language",
                            "    that made it possible",
                            "",
                            "elif you didn't enjoy the game:",
                            "    you could still toss 'em a few bucks",
                            "",
                            "",
                            "https://www.python.org/psf/donations/"
                            ]
        self.labels = []
        for line in text_lines:
            if line:
                label = GroupLabel(self.labels, font, font_size, line, "steelblue4",
                                             {"topleft": (screen.centerx - (spacer * 4), top)})
            top += label.rect.height
        top = screen.bottom - (spacer * 2)
    
    def get_event(self, event):
        if event.type in (pg.KEYDOWN, pg.MOUSEBUTTONDOWN):
            self.done = True
            self.quit = True
        
    def update(self, surface, keys, dt):
        self.cursor_rect.center = pg.mouse.get_pos()
        self.draw(surface)
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        for label in self.labels:
            label.draw(surface)
        surface.blit(self.cursor, self.cursor_rect)    