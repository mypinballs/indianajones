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

locale.setlocale(locale.LC_ALL, 'en_US')

class Skillshot(game.Mode):

	def __init__(self, game, priority):
            super(Skillshot, self).__init__(game, priority)

            self.text_layer = dmd.TextLayer(43, 22, self.game.fonts['num_09Bx7'], "center", opaque=False)
            self.dmd_image = "dmd/skillshot_bgnd.dmd"

            self.game.sound.register_sound('skillshot_made', speech_path+"excellent.aiff")
            self.game.sound.register_sound('skillshot_made', speech_path+'well_done.aiff')
            self.game.sound.register_sound('skillshot_made', speech_path+'incredible.aiff')

            self.lamps = ['rightRampArrow','rightPlaneTop']#,'rightPlaneMiddle','rightPlaneBottom'
            self.skill_timer =8
            self.skill_value_start = 5000000
            self.skill_value_boost = 5000000
            self.count = 0
            
            self.reset()


        def reset(self):
           pass


        def mode_started(self):
            self.activate_lamps()
            self.game.coils.leftControlGate.pulse(0)
            self.game.status = 'skillshot'
            self.delay(name='clear', event_type=None, delay=self.skill_timer, handler=self.clear)

        def mode_ended(self):
            pass

        def mode_tick(self):
            pass

            
        def activate_lamps(self):
             print("activate skillshot lamps")
             for i in range(len(self.lamps)):
                self.game.drive_lamp(self.lamps[i],'superfast')

        def clear_lamps(self):
            print("stop skillshot lamps")
            for i in range(len(self.lamps)):
                self.game.drive_lamp(self.lamps[i],'off')


        def shot_made(self):

            skill_value = self.skill_value_boost*self.count +self.skill_value_start

            #self.bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+self.dmd_image).frames[0])
            anim = dmd.Animation().load(game_path+self.dmd_image)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            self.bgnd_layer.add_frame_listener(-1, self.clear)

            #set text layers
            self.text_layer.set_text(locale.format("%d",skill_value,True),blink_frames=10)
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.text_layer])
            
            self.count+=1

            self.game.sound.play('skillshot_made')
            self.game.score(skill_value)

            #lamp show - and restore previous lamps
            self.game.lampctrl.save_state('game')
            self.game.lampctrl.play_show('success', repeat=False,callback=self.restore_lamps)

            self.clear()

        def restore_lamps(self):
            self.game.lampctrl.restore_state('game')

        def update_lamps(self):
            pass

        def clear(self):
            self.layer = None
            self.clear_lamps()
            self.game.coils.leftControlGate.disable()
            self.game.status = None
            self.game.modes.remove(self)

        
        def sw_rightRampMade_active(self,sw):
            self.shot_made()

        def sw_singleDropTop_active(self,sw):
            self.clear()

#        def sw_adventureT_active(self,sw):
#            self.clear()

        def sw_rightLoopBottom_active(self,sw):
            self.clear()