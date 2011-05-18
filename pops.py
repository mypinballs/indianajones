# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *
import random

base_path = "/Users/jim/Documents/Pinball/p-roc/p-roc system/src/"
game_path = base_path+"games/indyjones/"


class Pops(game.Mode):

	def __init__(self, game, priority):
            super(Pops, self).__init__(game, priority)
            self.text_layer = dmd.TextLayer(95, 0, self.game.fonts['num_14x10'], "left", opaque=False)

            self.super_pops_count = 0
            self.super_pops_default = 50
            self.super_pops_raise = 25
            self.level =1
            self.super_score = 1000000
            self.score = 1000
            self.animation_status='ready'

            self.reset()

        def reset(self):
            self.super_pops_count =  self.super_pops_default + (self.super_pops_raise*self.level)

        def mode_started(self):
            print("Pops Mode Started")
            pass

        def play_sound(self):
            pass


        def play_animation(self,opaque=False, repeat=False, hold=False, frame_time=3):

            list=["dmd/pops.dmd","dmd/indy_punch.dmd","dmd/badguy_punch.dmd"]

            i= random.randint(0, len(list)-1)
            anim = dmd.Animation().load(game_path+list[i])

            if self.animation_status=='ready':

                self.animation_layer = dmd.AnimatedLayer(frames=anim.frames, opaque=opaque, repeat=repeat, hold=hold, frame_time=frame_time)
                self.animation_layer.add_frame_listener(-1, self.animation_ended)
                self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer])
                self.animation_status = 'running'

        def animation_ended(self):
            self.set_animation_status('ready')
            self.layer = None
            
        def set_animation_status(self,status):
            self.animation_status = status

        def update_count(self):
            self.super_pops_count -=1
            self.text_layer.set_text(str(self.super_pops_count))
    
        def score(self):
            if self.super_pops_count==0:
                self.game.score(self.super_score)
            else:
                self.game.score(self.score)
        
        def sw_leftJet_active(self, sw):
            self.update_count()

            self.play_sound()
            self.play_animation()

        def sw_rightJet_active(self, sw):
            self.update_count()

            self.play_sound()
            self.play_animation()

        def sw_bottomJet_active(self, sw):
            self.update_count()

            self.play_sound()
            self.play_animation()

