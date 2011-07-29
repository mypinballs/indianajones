# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
from procgame import *

import locale
import random

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Match(game.Mode):

	def __init__(self, game, priority):
            super(Match, self).__init__(game, priority)

            self.match_layer = dmd.TextLayer(24, 11, self.game.fonts['num_09Bx7'], "left", opaque=False)
            self.p1_layer = dmd.TextLayer(0, 0, self.game.fonts['6x6_bold'], "left", opaque=False)
            self.p2_layer = dmd.TextLayer(20, 0, self.game.fonts['6x6_bold'], "left", opaque=False)
            self.p3_layer = dmd.TextLayer(108, 0, self.game.fonts['6x6_bold'], "right", opaque=False)
            self.p4_layer = dmd.TextLayer(128, 0, self.game.fonts['6x6_bold'], "right", opaque=False)
            self.dmd_image = "dmd/match.dmd"
            self.value_range = 9
            self.player_digits = [0,0,0,0]

            self.game.sound.register_sound('see_you', speech_path+"see_you_tomorrow.aiff")
            self.game.sound.register_sound('top_men', speech_path+"top_men.aiff")
            
            self.reset()


        def reset(self):
            pass


        def mode_started(self):
            self.generate_digits()
            self.generate_match()
            self.play_anim()


        def mode_stopped(self):
            #set the status
            self.game.system_status='game_over'
            
            #add the attact mode and play the see you tommorow sample
            self.game.modes.add(self.game.attract_mode)
            self.game.sound.play_voice('see_you')


        def play_anim(self):

            anim = dmd.Animation().load(game_path+self.dmd_image)
            self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,frame_time=2)
            self.animation_layer.composite_op = "blacksrc"
            self.animation_layer.add_frame_listener(-1,self.clear)
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.match_layer,self.p1_layer,self.p2_layer,self.p3_layer,self.p4_layer,self.animation_layer])
            #play speech 
            self.game.sound.play_voice('top_men')
           

        def generate_match(self):
        #create the match value for comparison

            value = (random.randint(0, self.value_range))*10
            if value==0:
                display = "0"+str(value)
            else:
                display = str(value)

            #set text
            self.match_layer.set_text(display)

            #set clear time
            #self.delay(name='clear', event_type=None, delay=1.5, handler=self.clear)


        def generate_digits(self):
        #extract and display the last 2 score digits for each player

            player_layers=[self.p1_layer,self.p2_layer,self.p3_layer,self.p4_layer]

            for i in range(len(self.game.players)):
                score = self.game.players[i].score
                digit = str(score)[-2:-1]
                player_layers[i].set_text(digit)
                #set var for comparison
                self.player_digits[i]=digit
            

        def clear(self):
            self.layer = None
            self.game.modes.remove(self)
