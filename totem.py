# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *

base_path = "/Users/jim/Documents/Pinball/p-roc/p-roc system/src/"
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

locale.setlocale(locale.LC_ALL, 'en_US')

class Totem(game.Mode):

	def __init__(self, game, priority):
            super(Totem, self).__init__(game, priority)

            self.text_layer = dmd.TextLayer(14, 18, self.game.fonts['num_09Bx7'], "left", opaque=False)
            self.totem_ani = "dmd/totem.dmd"
            self.quick_multi_ani = "dmd/qm_bgnd.dmd"

            self.game.sound.register_sound('rubble', sound_path+"rubble.aiff")

            self.totem_value_start = 2000000
            self.totem_value_boost = 1000000
            self.count = 0
            
            self.reset()


        def reset(self):
           pass


        def mode_started(self):
            pass

        def mode_tick(self):
            pass


        def hit(self):

            totem_value = self.totem_value_boost*self.count +self.totem_value_start

            #self.bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+self.dmd_image).frames[0])
            anim = dmd.Animation().load(game_path+self.totem_ani)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            self.bgnd_layer.add_frame_listener(-1, self.clear)

            #set text layers
            self.text_layer.set_text(locale.format("%d",totem_value,True),blink_frames=10)
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.text_layer])
            
            #set target
            self.delay(name='reset_target', event_type=None, delay=1, handler=self.setup_target)

            #base calls
            self.game.sound.play('rubble')
            self.game.score(totem_value)
            self.game.lampctrl.play_show('hit', repeat=False,callback=self.game.update_lamps)

            self.count+=1





        def update_lamps(self):
            print("Update Lamps")

        def clear(self):
            self.layer = None

        def setup_target(self):
            if self.count<4:
                self.game.coils.totemDropUp.pulse()
            else:
                self.start_multiball()

        def start_multiball(self):
            anim = dmd.Animation().load(game_path+self.quick_multi_ani)
            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            self.layer.add_frame_listener(-1, self.clear)

        def sw_singleDropTop_active(self, sw):
            self.hit()

