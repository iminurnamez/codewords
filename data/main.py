from . import tools, prepare
from .states import game



def main():
    run_it = tools.Control(prepare.ORIGINAL_CAPTION)
    state_dict = {"GAME": game.Game()}       
    run_it.setup_states(state_dict, "GAME")
    run_it.main()
