# Mini Playfield Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:38 PM$"

import procgame
import locale
import random

from procgame import *
from random import *


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"

class Loops(game.Mode):

	def __init__(self, game, priority):
            super(Loops, self).__init__(game, priority)

            self.text_layer = dmd.TextLayer(128/2, 1, self.game.fonts['18x12'], "center", opaque=False)
            #self.text_layer.transition = dmd.ExpandTransition(direction='vertical')

            self.game.sound.register_sound('unlit', sound_path+"loop_unlit.aiff")
            self.game.sound.register_sound('multiplier', sound_path+"loop_multiplier.aiff")

            self.game.sound.register_sound('horse', sound_path+"horse_gallap.aiff")
            self.game.sound.register_sound('car', sound_path+"car.aiff")
            self.game.sound.register_sound('dingy', sound_path+"dingy.aiff")
            self.game.sound.register_sound('truck', sound_path+"truck.aiff")
            self.game.sound.register_sound('motorbike', sound_path+"motorbike.aiff")


            self.loop_unlit_value = 100000
            self.loop_value = 0

            self.loops_completed=self.game.get_player_stats('loops_completed')
            self.loops_made=self.game.get_player_stats('loops_made')
            self.ramps_made=self.game.get_player_stats('ramps_made')
            self.friends_collected=self.game.get_player_stats('friends_collected')

            self.loop_lamps = ['leftLoop','rightLoop']
            self.loop_flag = [False,False]




            #setup loop collection order
            self.vehicles = ['horse','car','dingy','truck','motorbike']
            shuffle(self.vehicles)
            

            self.reset()

        def reset(self):
            self.loop_active = False
            self.loop_multiplier=1
            self.side=None
            
            self.game.coils.leftControlGate.disable()
            self.game.coils.rightControlGate.disable()
            
            self.reset_lamps()
            

        def mode_started(self):
            self.loops_completed=self.game.get_player_stats('loops_completed')
            self.loops_made=self.game.get_player_stats('loops_made')
            self.ramps_made=self.game.get_player_stats('ramps_made')
            self.friends_collected=self.game.get_player_stats('friends_collected')
            self.loop_value = self.game.get_player_stats('loop_value')

        def mode_stopped(self):
            pass


        def reset_lamps(self):
            for i in range(len(self.loop_lamps)):
                self.game.effects.drive_lamp(self.loop_lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.loop_lamps)):
                if self.loop_flag[i]:
                    self.game.effects.drive_lamp(self.loop_lamps[i],'on')

        def timeout_lamps(self,time):
            for i in range(len(self.loop_lamps)):
                if self.loop_flag[i]:
                    self.game.effects.drive_lamp(self.loop_lamps[i],'timeout',time)

        def clear(self):
            self.layer = None


        def sequence(self,side):
            if self.loop_active:

                self.open_gate(side)
                
                if self.loops_completed==5:
                    self.jackpot()
                    
                elif self.loops_completed<=self.friends_collected:
                    anim = dmd.Animation().load(game_path+"dmd/loop_"+side+"_"+self.vehicles[self.loops_completed]+".dmd")
                    self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=2)
                    self.animation_layer.add_frame_listener(-10,self.score_display)
                    self.animation_layer.add_frame_listener(-1,self.clear)
                    self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer])
                    self.game.sound.play(self.vehicles[self.loops_completed])
                    #self.game.lampctrl.play_show('success', repeat=False,callback=self.game.update_lamps)#self.restore_lamps
                    self.loops_made+=1
                    self.loops_made=self.game.get_player_stats('loops_made')

                   
                    
            else:
                self.loop_stall()

        def score_display(self):
            #calc score
            score = (self.loop_value)*self.loop_multiplier
            self.text_layer.set_text(locale.format("%d",score,True),blink_frames=20)

            self.game.score(score)

            if self.loop_multiplier>1: #announce multiple loops achieved
                for i in range(self.loop_multiplier-1):
                    self.game.sound.play('multiplier')

        def multiplier(self):
            self.loop_multiplier +=1

            if self.loop_multiplier==2:#set the loops progress store only on first successful loop
                self.loops_completed+=1
                self.game.set_player_stats('loops_completed',self.loops_completed)

        def jackpot(self):
            pass

        def open_gate(self,side):
            if side=='left':
                 self.game.coils.rightControlGate.pulse(0)
            elif side=='right':
                 self.game.coils.leftControlGate.pulse(0)

        def loop_stall(self):
            self.game.score(self.loop_unlit_value)
            self.game.sound.play('unlit')
            self.loop_multiplier=1

        def enable_loop(self,num):
            self.friends_collected = self.game.get_player_stats('friends_collected')
            
            if self.friends_collected>0:
                self.loop_active=True
                self.loop_flag[num]=True
                self.update_lamps()
                self.delay(name='expired', event_type=None, delay=self.game.user_settings['Gameplay (Feature)']['Loop Lit Timer'], handler=self.reset)
                lamp_timeout_offset = 2
                self.delay(name='lamp_timeout', event_type=None, delay=self.game.user_settings['Gameplay (Feature)']['Loop Lit Timer']-lamp_timeout_offset, handler=self.timeout_lamps,param=lamp_timeout_offset)


        #switch events
        
        def sw_leftLoopBottom_active(self,sw):
            self.delay(name='stalled', event_type=None, delay=0.5, handler=self.loop_stall)
            self.side='left'


        def sw_leftLoopTop_active(self,sw):
            if self.side=='left':
                self.cancel_delayed('stalled')
            
                if self.game.switches.rightLoopTop.time_since_change()<=1.5 and self.game.switches.rightLoopBottom.time_since_change()<=1.5:
                    self.multiplier()

                self.sequence(self.side)


        def sw_rightLoopBottom_active(self,sw):
            self.delay(name='stalled', event_type=None, delay=0.5, handler=self.loop_stall)
            self.side='right'

        def sw_rightLoopTop_active(self,sw):
            if self.side=='right':
                self.cancel_delayed('stalled')

                if self.game.switches.leftLoopTop.time_since_change()<=1.5 and self.game.switches.leftLoopBottom.time_since_change()<=1.5:
                    self.multiplier()

                self.sequence(self.side)


        def sw_leftInlane_active(self,sw):
            self.enable_loop(1)

        def sw_rightInlane_active(self,sw):
            self.enable_loop(0)

      


        