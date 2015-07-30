# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Screens(game.Mode):

	def __init__(self, game):
            super(Screens, self).__init__(game, 100)

            self.game.sound.register_sound('collect', sound_path+"mode_bonus_jingle.aiff")
            

        def mode_bonus(self,timer,value):

            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
            name_layer = dmd.TextLayer(128/2, 7, self.game.fonts['8x6'], "center")
            info_layer = dmd.TextLayer(128/2, 15, self.game.fonts['num_09Bx7'], "center")

            name_layer.set_text('Mode Bonus'.upper(),color=dmd.BROWN)
            info_layer.set_text(locale.format("%d",value,True),color=dmd.GREEN)

            #play sound
            self.game.sound.play('collect')

            #score
            self.game.score(value)

            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,name_layer,info_layer])


            self.delay(name='clear_display_delay', event_type=None, delay=timer, handler=self.clear)

        def raise_jackpot(self,timer,value):

            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
            name_layer = dmd.TextLayer(128/2, 7, self.game.fonts['8x6'], "center")
            info_layer = dmd.TextLayer(128/2, 15, self.game.fonts['num_09Bx7'], "center")

            name_layer.set_text('Add To Jackpot'.upper(),color=dmd.BROWN)
            info_layer.set_text(locale.format("%d",value,True),color=dmd.GREEN,blink_frames=2)

            #play sound
            self.game.sound.play('collect')

            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,name_layer,info_layer])

            self.delay(name='clear_display_delay', event_type=None, delay=timer, handler=self.clear)

        def add_ball(self,timer,value):

            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
            name_layer = dmd.TextLayer(128/2, 12, self.game.fonts['8x6'], "center")

            name_layer.set_text('Ball Added!'.upper(),color=dmd.RED,blink_frames=2)

            #play sound
            self.game.sound.play('collect')

            #score
            self.game.score(value)

            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,name_layer])


            self.delay(name='clear_display_delay', event_type=None, delay=timer, handler=self.clear)


        def clear(self):
            self.layer = None