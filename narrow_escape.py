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

#locale.setlocale(locale.LC_ALL, 'en_GB')

class Narrow_Escape(game.Mode):

	def __init__(self, game, priority):
            super(Narrow_Escape, self).__init__(game, priority)

            self.text_layer = dmd.TextLayer(80, 18, self.game.fonts['num_09Bx7'], "center", opaque=False)
            self.dmd_image = "dmd/narrow_escape.dmd"
            self.escape_value_start = 3000000
            self.escape_value_boost = 1000000
            self.count = 0

            self.game.sound.register_sound('escape', sound_path+"narrow_escape.aiff")

            
            self.reset()


        def reset(self):
           pass


        def mode_started(self):
            pass

        def mode_tick(self):
            pass


        def escaped(self):

            escape_value = self.escape_value_boost*self.count +self.escape_value_start

            #self.bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+self.dmd_image).frames[0])
            anim = dmd.Animation().load(game_path+self.dmd_image)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            #set text layers
            self.text_layer.set_text(locale.format("%d",escape_value,True),blink_frames=10)
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.text_layer])

            self.game.score(escape_value)
            self.game.sound.play('escape')
            
            self.count+=1

            #set clear time
            self.delay(name='clear', event_type=None, delay=1.5, handler=self.clear)

        def update_lamps(self):
            print("Update Lamps")

        def clear(self):
            self.layer = None

        
        def sw_rightOutlaneTop_active(self, sw):
            self.delay(name='escape', event_type=None, delay=0.8, handler=self.escaped)


        def sw_rightOutlaneBottom_active(self, sw):
            #cancel animation call if ball actually drains
            self.cancel_delayed('escape')