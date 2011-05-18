# Mini Playfield Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:38 PM$"

import procgame
import locale
from procgame import *
from pops import *
from narrow_escape import *
from poa import *
from hand_of_fate import *
from ij_modes import *

base_path = "/Users/jim/Documents/Pinball/p-roc/p-roc system/src/"
game_path = base_path+"games/indyjones/"

class General_Play(game.Mode):

	def __init__(self, game, priority):
            super(General_Play, self).__init__(game, priority)

            self.reset()


        def reset(self):
            self.pops = Pops(self, 45)
            self.narrow_escape = Narrow_Escape(self, 46)
            self.poa = POA(self, 50)
            self.hof = Hand_Of_Fate(self, 55)
            self.indy_lanes = Indy_Lanes(self, 56)
            self.plane_chase = Plane_Chase(self, 57)
            self.mode_select = Mode_Select(self, 58)


        def mode_started(self):
            #add modes active for full game
            self.modes.add(self.pops)
            self.modes.add(self.narrow_escape)
            self.modes.add(self.poa)
            self.modes.add(self.hof)
            self.modes.add(self.indy_lanes)
            self.modes.add(self.plane_chase)
            self.modes.add(self.mode_select)

            #set idol - should be here already?
            self.game.idol.home()

        
        def mode_ended(self):
            self.modes.remove(self.pops)
            self.modes.remove(self.narrow_escape)
            self.modes.remove(self.poa)
            self.modes.remove(self.hof)
            self.modes.remove(self.indy_lanes)
            self.modes.remove(self.plane_chase)
            self.modes.remove(self.mode_select)
        
