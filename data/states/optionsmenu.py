import pygame as pg
from .. import tools, prepare
from ..components.labels import Label, Button, PayloadButton

class OptionsMenu(tools._State):
    def __init__(self):
        super(OptionsMenu, self).__init__()
        self.next = "GAME"
        self.font = prepare.FONTS["Fixedsys500c"]
        
        
    def startup(self, persistent):
        self.persist = persistent
        self.resize()
        
    def resize(self):    
        self.cursor = prepare.GFX["pythoncursor"]
        self.cursor_rect = self.cursor.get_rect()
        screen = pg.display.get_surface().get_rect()
        margin = screen.height // 40
        self.font_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["font size"]
        self.lg_font_size = prepare.SETTINGS[prepare.SCREEN_SIZE]["lg font size"]
        self.title = Label(self.font, self.lg_font_size, "Options", "steelblue4",
                                 {"midtop": (screen.centerx, screen.top + margin)})        
        m_string = "Sound {}".format("Off" if self.persist["sounds"] else "On")
        m_label = Label(self.font, self.font_size, m_string, "steelblue4",
                                 {"center": (0,0)})
        b_width = m_label.rect.width + (margin * 2)
        b_height = m_label.rect.height + margin
        b_left = screen.centerx - (int(b_width * 1.5))
        top = self.title.rect.bottom + (margin * 2)
        self.music_button = Button(screen.centerx - (b_width//2), top, b_width, b_height, m_label) 
        top += self.music_button.rect.height + (margin * 2)
        full_label = Label(self.font, self.font_size, "Fullscreen" if not self.persist["fullscreen"] else "Windowed", 
                                  "steelblue4", {"center": (0, 0)})
        self.fullscreen_button = Button(screen.centerx - (b_width // 2), top, b_width, b_height, full_label)
        top += self.fullscreen_button.rect.height + (margin * 2)
        self.size_header = Label(self.font, self.lg_font_size // 2, "Screen Size", "steelblue4",
                                            {"midtop": (screen.centerx, top)})
        top += self.size_header.rect.height + margin                                            
        
        
        self.size_buttons = []
        for i, size in enumerate(prepare.SETTINGS):
            label = Label(self.font, self.font_size, "{} x {}".format(size[0], size[1]),
                                "steelblue4", {"center": (0, 0)})
            button = PayloadButton(b_left + ((b_width * 2) * (i % 2)), top, b_width, b_height, label, size)
            self.size_buttons.append(button)
            top += (b_height + (margin * 2)) * (i % 2)
      
        done = Label(self.font, self.font_size, "DONE", "steelblue4",
                            {"center": (0, 0)})
        self.done_button = Button(screen.centerx - (b_width//2), screen.bottom - ((margin * 2) + b_height),
                                                b_width, b_height, done)        
        
    
    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.done_button.rect.collidepoint(event.pos):
                self.done = True
            elif self.music_button.rect.collidepoint(event.pos):
                self.persist["sounds"] = not self.persist["sounds"]
                if self.persist["sounds"]:
                    pg.mixer.music.play(-1)
                else:
                    pg.mixer.music.stop()
                m_string = "Sound {}".format("Off" if self.persist["sounds"] else "On")
                m_label = Label(self.font, self.font_size, m_string, "steelblue4",
                                         {"center": self.music_button.rect.center})
                self.music_button.label = m_label
            elif self.fullscreen_button.rect.collidepoint(event.pos):
                self.persist["fullscreen"] = not self.persist["fullscreen"]
                if self.persist["fullscreen"]:
                    pg.display.set_mode(prepare.SCREEN_SIZE, pg.FULLSCREEN)
                else:
                    pg.display.set_mode(prepare.SCREEN_SIZE)
                full_label = Label(self.font, self.font_size, "Fullscreen" if not self.persist["fullscreen"] else "Windowed",
                                          "steelblue4", {"center": (0, 0)})
                self.fullscreen_button = Button(self.fullscreen_button.rect.x, self.fullscreen_button.rect.y, 
                                                               self.fullscreen_button.rect.width,
                                                               self.fullscreen_button.rect.height, full_label)
            else:
                for button in self.size_buttons:
                    if button.rect.collidepoint(event.pos):
                        if button.payload != prepare.SCREEN_SIZE:
                            prepare.SCREEN_SIZE = button.payload
                            if self.persist["fullscreen"]:
                                pg.display.set_mode(prepare.SCREEN_SIZE, pg.FULLSCREEN)
                            else:
                                pg.display.set_mode(prepare.SCREEN_SIZE)
                            self.resize()
            
    def update(self, surface, keys, dt):
        self.cursor_rect.center = pg.mouse.get_pos()
        self.draw(surface)
    
    def draw(self, surface):
        surface.fill(pg.Color("gold3"))
        self.title.draw(surface)
        self.music_button.draw(surface)
        self.fullscreen_button.draw(surface)
        self.size_header.draw(surface)
        for button in self.size_buttons:
            button.draw(surface)
        self.done_button.draw(surface)
        surface.blit(self.cursor, self.cursor_rect)       
            
            
            
            