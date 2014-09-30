import os
from math import atan2
import pygame as pg


class Control(object):
    def __init__(self, caption):
        self.screen = pg.display.get_surface()
        self.screen_size = self.screen.get_size()
        self.caption = caption
        self.done = False
        self.clock = pg.time.Clock()
        self.show_fps = False
        self.keys = pg.key.get_pressed()
        self.state_dict = {}
        self.state_name = None
        self.state = None
        self.fullscreen = False
        self.dt = 0.0
        self.fps = 60

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.keys, self.dt)


    def flip_state(self):
        previous,self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(persist)
        self.state.previous = previous

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            self.state.get_event(event)

    def toggle_show_fps(self, key):
        if key == pg.K_F5:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pg.display.set_caption(self.caption)
    
    def main(self):
        while not self.done:
            self.dt = self.clock.tick(self.state.fps)
            self.event_loop()
            self.update()
            pg.display.update()
            if self.show_fps:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
                pg.display.set_caption(with_fps)
            

class _State(object):
    def __init__(self):
        self.fps = 60
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.persist = {}
        self.persist["sounds"] = True
        self.persist["fullscreen"] = False

    def get_event(self, event):
        pass

    def startup(self, persistent):
        self.persist = persistent

    def cleanup(self):
        self.done = False
        return self.persist

    def update(self, surface, keys):
        pass




    
def load_all_gfx(directory,colorkey=(0,0,0,255),accept=(".png",".jpg",".bmp")):
    graphics = {}
    for pic in os.listdir(directory):
        name,ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic)).convert()
            img.set_colorkey(colorkey)
            graphics[name]=img
    return graphics


def load_all_music(directory, accept=(".wav", ".mp3", ".ogg", ".mdi")):
    songs = {}
    for song in os.listdir(directory):
        name,ext = os.path.splitext(song)
        if ext.lower() in accept:
            songs[name] = os.path.join(directory, song)
    return songs

def load_all_sfx(directory, accept=(".wav", ".mp3", ".ogg", ".mdi")):
    sfx = {}
    for fx in os.listdir(directory):
        name,ext = os.path.splitext(fx)
        if ext.lower() in accept:
            sfx[name] = pg.mixer.Sound(os.path.join(directory, fx))
    return sfx

def load_all_fonts(directory, accept=(".ttf")):
    return load_all_music(directory, accept)
