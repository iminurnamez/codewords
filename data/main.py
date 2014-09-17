from . import tools, prepare
from .states import (game, helpscreen, optionsmenu, verdantsplash,
                                pysplash, exitscreen)


def main():
    run_it = tools.Control(prepare.ORIGINAL_CAPTION)
    state_dict = {"SPLASH": verdantsplash.VerdantSplash(),
                        "PYSPLASH": pysplash.PySplash(),
                        "HELP": helpscreen.HelpScreen(),
                        "OPTIONS": optionsmenu.OptionsMenu(),
                        "GAME": game.Game(),
                        "EXITSCREEN": exitscreen.ExitScreen()}
                        
    run_it.setup_states(state_dict, "PYSPLASH")
    run_it.main()
