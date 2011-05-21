# Mini Playfield Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:38 PM$"

import procgame
import locale
from procgame import *

base_path = "/Users/jim/Documents/Pinball/p-roc/p-roc system/src/"
game_path = base_path+"games/indyjones/"


class Plane_Chase(game.Mode):

	def __init__(self, game, priority):
            super(Plane_Chase, self).__init__(game, priority)

            self.text_layer = dmd.TextLayer(128/2, 5, self.game.fonts['18x12'], "center", opaque=False)
            #self.text_layer.transition = dmd.ExpandTransition(direction='vertical')

            self.ramp_made_score = 1000000
            self.ramp_entered_score = 5000
            self.dog_fight_value = 40000000
            self.dog_fight_min_value = 3000000

            self.bottom_left_wings = False
            self.middle_left_wings = False
            self.top_left_wings = False
            self.bottom_right_wings = False
            self.middle_right_wings = False
            self.top_right_wings = False

            self.plane_lamps = ['leftPlaneBottom','rightPlaneBottom','leftPlaneMiddle','rightPlaneMiddle','leftPlaneTop','rightPlaneTop','leftRampArrow','rightRampArrow']
            self.ramps_made=self.game.get_player_stats('ramps_made')
            self.total_ramps_made = 0

            #flags to enable shot sequence to be progressed
            self.left_ramp_enabled = False
            self.right_ramp_enabled = False

            self.reset()

        def reset(self):
            self.reset_lamps()

            self.left_ramp_enabled = True
            self.game.effects.drive_lamp('leftRampArrow','superfast')
            self.game.effects.drive_lamp(self.plane_lamps[0],'fast')

        def reset_lamps(self):
            for i in range(len(self.plane_lamps)):
                self.game.effects.drive_lamp(self.plane_lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.plane_lamps)):
                if i<=self.ramps_made:
                    self.game.effects.drive_lamp(self.plane_lamps[i],'on')
                elif i==(self.ramps_made+1):
                    self.game.effects.drive_lamp(self.plane_lamps[i],'fast')
                else:
                    self.game.effects.drive_lamp(self.plane_lamps[i],'off')

        def sequence(self,number):
            print("sequence: "+str(number))
            if number>0 and number<6:
                self.game.effects.drive_lamp(self.plane_lamps[number-1],'on')
                self.game.effects.drive_lamp(self.plane_lamps[number],'fast')

                if self.left_ramp_enabled:
                    self.right_ramp_enabled = True
                    self.left_ramp_enabled = False
                    self.game.effects.drive_lamp('leftRampArrow','off')
                    self.game.effects.drive_lamp('rightRampArrow','superfast')

                elif self.right_ramp_enabled:
                    self.right_ramp_enabled = False
                    self.left_ramp_enabled = True
                    self.game.effects.drive_lamp('rightRampArrow','off')
                    self.game.effects.drive_lamp('leftRampArrow','superfast')

                #self.game.lampctrl.save_state('game')

                anim = dmd.Animation().load(game_path+"dmd/plane_chase.dmd")
                self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=2)
                self.animation_layer.add_frame_listener(-10,self.ramp_made_text)
                self.animation_layer.add_frame_listener(-1,self.clear)
                #self.text_layer.set_text(str(self.ramp_made_score),seconds=2)
                self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer])
                #self.delay(name='score', event_type=None, delay=2.5, handler=self.text_layer.set_text(str(self.ramp_made_score),seconds=2))

                self.game.lampctrl.play_show('success', repeat=False,callback=self.game.update_lamps)#self.restore_lamps
                self.game.score(self.ramp_made_score)

            else:
                self.dog_fight()
                self.game.coils.flasherDogFight.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
                self.delay(name='expired', event_type=None, delay=self.game.user_settings['Gameplay (Feature)']['Dog Fight Timer'], handler=self.reset)

        def ramp_made_text(self):
            self.text_layer.set_text(locale.format("%d",self.ramp_made_score,True),blink_frames=20)

        #def restore_lamps(self):
        #    self.game.lampctrl.restore_state('game')

        def dog_fight(self):
            self.text_layer.set_text(str(self.dog_fight_value))

            if self.dog_fight_value>self.dog_fight_min_value:
                self.dog_fight_value -=15275

            self.delay(name='update_time', event_type=None, delay=0.5, handler=self.dog_fight)

        def mode_started(self):
            pass

        
        def mode_ended(self):
            #turn off all mini playfield lamps
            pass

        def clear(self):
            self.layer = None

        def sw_leftRampEnter_active(self,sw):
            self.game.score(self.ramp_entered_score)

        def sw_rightRampEnter_active(self,sw):
            self.game.score(self.ramp_entered_score)


        def sw_leftRampMade_active(self,sw):
            if self.left_ramp_enabled:
                self.ramps_made+=1
                self.sequence(self.ramps_made)
            else:
                self.game.score(self.ramp_made_score/2)

            self.game.set_player_stats('ramps_made',self.ramps_made)



        def sw_rightRampMade_active(self,sw):
            if self.right_ramp_enabled:
                self.ramps_made+=1
                self.sequence(self.ramps_made)
            else:
                self.game.score(self.ramp_made_score/2)

            self.game.set_player_stats('ramps_made',self.ramps_made)