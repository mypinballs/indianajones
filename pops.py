# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *
import random

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


class Pops(game.Mode):

	def __init__(self, game, priority):
            super(Pops, self).__init__(game, priority)
            self.text_layer = dmd.TextLayer(104, 0, self.game.fonts['num_14x10'], "center", opaque=False)

            self.game.sound.register_sound('punch1', sound_path+"punch_1.aiff")
            self.game.sound.register_sound('punch2', sound_path+"punch_2.aiff")
            self.game.sound.register_sound('punch3', sound_path+"punch_3.aiff")
            self.game.sound.register_sound('punch4', sound_path+"punch_4.aiff")
            self.game.sound.register_sound('punch5', sound_path+"punch_5.aiff")
            self.game.sound.register_sound('super1', sound_path+"super_jets_1.aiff")
            self.game.sound.register_sound('super2', sound_path+"super_jets_2.aiff")
            self.game.sound.register_sound('super3', sound_path+"super_jets_3.aiff")
            self.game.sound.register_sound('super4', sound_path+"super_jets_4.aiff")
            self.game.sound.register_sound('super5', sound_path+"super_jets_5.aiff")

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

            list=["punch1","punch2","punch3","punch4","punch5"]
            super_list =["super1","super2","super3","super4","super5"]

            if self.super_pops_count==0:
                i= random.randint(0, len(super_list)-1)
            else:
                i= random.randint(0, len(list)-1)

            self.game.sound.play(list[i])


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
    
        def pops_score(self):
            if self.super_pops_count==0:
                self.game.score(self.super_score)
            else:
                self.game.score(self.score)
        
        def sw_leftJet_active(self, sw):
            self.update_count()

            self.pops_score()
            self.play_sound()
            self.play_animation()

        def sw_rightJet_active(self, sw):
            self.update_count()

            self.pops_score()
            self.play_sound()
            self.play_animation()

        def sw_bottomJet_active(self, sw):
            self.update_count()

            self.pops_score()
            self.play_sound()
            self.play_animation()

