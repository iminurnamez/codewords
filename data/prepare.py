import os
from collections import OrderedDict
import pygame as pg
from . import tools



ORIGINAL_CAPTION = "Code Words"

SETTINGS = OrderedDict([((1920, 1080), {"slot width": 350,
                                                               "slot length": 750,
                                                               "slot height": 25,
                                                               "font size": 24,
                                                                "sm font size": 16,
                                                                "lg font size": 128,
                                                                "score box size": (300, 300)}),
                                        ((1600, 900), {"slot width": 300,
                                                             "slot length": 750,
                                                             "font size": 20,
                                                             "sm font size": 16,
                                                             "lg font size": 128,
                                                             "score box size": (300, 300),
                                                             "slot height": 25}),
                                        ((1366, 768), {"slot width": 300,
                                                             "slot length": 600,
                                                             "font size": 18,
                                                             "sm font size": 14,
                                                             "lg font size": 128,
                                                             "score box size": (300, 300),
                                                             "slot height": 20}),
                                        ((1024, 768), {"slot width": 250,
                                                             "slot length": 600,
                                                             "font size": 16,
                                                             "sm font size": 14,
                                                             "lg font size": 96,
                                                             "score box size": (200, 250),
                                                             "slot height": 20}),
                                        ((800, 600), {"slot width": 200,
                                                             "slot length": 500,
                                                             "font size": 12,
                                                             "sm font size": 12,
                                                             "lg font size": 64,
                                                             "score box size": (150, 200),
                                                             "slot height": 14}),
                                        ((640, 480), {"slot width": 150,
                                                           "slot length": 420,
                                                           "font size": 12,
                                                           "sm font size": 10,
                                                           "lg font size": 64,
                                                           "score box size": (150, 200),
                                                           "slot height": 14})])  
                                            
for size in SETTINGS:
    SETTINGS[size]["wheel offset"] = (86, 136)                                            
pg.init()
info = pg.display.Info()


SCREEN_SIZE = (info.current_w, info.current_h)
#print SCREEN_SIZE
if SCREEN_SIZE not in SETTINGS:
    for size in SETTINGS:
        #print size, "SCREENSIZE: ", SCREEN_SIZE
        if SCREEN_SIZE[0] >= size[0] and SCREEN_SIZE[1] >= size[1]:
            SCREEN_SIZE = size
            break 
#print  "SCREENSIZE: ", SCREEN_SIZE           
os.environ['SDL_VIDEO_CENTERED'] = "TRUE"
pg.mouse.set_visible(False)
pg.display.set_caption(ORIGINAL_CAPTION)

SCREEN = pg.display.set_mode(SCREEN_SIZE)
SCREEN_RECT = SCREEN.get_rect()
                  

#Resource loading (Fonts and music just contain path names).
FONTS = tools.load_all_fonts(os.path.join("resources", "fonts"))
MUSIC = tools.load_all_music(os.path.join("resources", "music"))
SFX   = tools.load_all_sfx(os.path.join("resources", "sound"))
GFX   = tools.load_all_gfx(os.path.join("resources", "graphics"))

if SCREEN_SIZE in ((800, 600), (640, 480)):
    scale_mod = 2
    for img in GFX:
        GFX[img] = pg.transform.scale(GFX[img], (int(GFX[img].get_width() // scale_mod), 
                                                                        int(GFX[img].get_height() // scale_mod)))
    SETTINGS[SCREEN_SIZE]["wheel offset"]  =  (int(SETTINGS[SCREEN_SIZE]["wheel offset"][0] // scale_mod) + 1,
                                                                         int(SETTINGS[SCREEN_SIZE]["wheel offset"][1] // scale_mod))
