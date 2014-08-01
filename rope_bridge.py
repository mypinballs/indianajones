# Monkey Brains Game Mode

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

#locale.setlocale(locale.LC_ALL, 'en_GB')
class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="center", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,mode)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


class Rope_Bridge(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Rope_Bridge, self).__init__(game, priority)

            self.log = logging.getLogger('ij.ropeBridge')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Rope Bridge Timer'])
            self.log.info("Rope Bridge Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['07x5'], self)
            self.award_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            
            #sound setup
            self.game.sound.register_music('background_play', music_path+"rope_bridge.aiff")
            self.game.sound.register_sound('rb_shot_hit', sound_path+"run_breathing.aiff")
            self.game.sound.register_sound('rb_s0', speech_path+"come_on_indy.aiff")
            self.game.sound.register_sound('rb_s1', sound_path+"sword_chop.aiff")

            #lamps setup
            self.lamps = ['leftRampArrow','rightRampArrow']
            
            self.reset()


        def reset(self):
            #var setup
            self.count = 0
            self.score_value_boost = 1000000
            self.score_value_start = 10000000
            self.score_value_completed = self.score_value_start*2
            self.score_value_extra = 2000000

        def load_scene_anim(self,count):

            if count<4:
                self.scene_anim = "dmd/rope_bridge_scene_"+str(count)+".dmd"
                anim = dmd.Animation().load(game_path+self.scene_anim)
                self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=2)
                self.scene_layer.add_frame_listener(-1,self.award_score)
                self.scene_layer.add_frame_listener(-1, self.load_bgnd_anim)
                self.layer = self.scene_layer
            else:
                self.completed()

        def completed(self):
            self.bgnd_anim = "dmd/rope_bridge_completed.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=2)
            self.scene_layer.add_frame_listener(-1,self.award_completed_score)
            self.scene_layer.add_frame_listener(-1,self.end_scene_delay)
            self.layer = self.scene_layer

        def end_scene_delay(self):
            self.delay(name='end_scene_delay', event_type=None, delay=2, handler=self.mode_select.end_scene)


        def load_bgnd_anim(self):
            self.bgnd_anim = "dmd/rope_bridge_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=33)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])


        def mode_started(self):
            #load player stats
            self.rope_bridge_distance = self.game.get_player_stats('rope_bridge_distance');
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(0, -1, self.game.fonts['07x5'],self.timer,"left")
            self.info_layer = dmd.TextLayer(128/2, 20, self.game.fonts['07x5'], "center", opaque=False)
            #self.info_layer.set_text("SHOOT LIT SHOTS",blink_frames=1000)

            #load animation
            self.load_bgnd_anim()
            
            #start mode music & speech
            self.game.sound.play_music('background_play', loops=-1)
            self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.voice_call, param=self.count)

            #open gates
            self.open_gates('left')
            self.open_gates('right')

            #update_lamps
            self.update_lamps()

        def mode_stopped(self):
            #save player stats
#            current_list = self.game.get_player_stats('mode_status_tracking');
#            updated_list =current_list
#            updated_list[0]=1
#
#            self.game.set_player_stats('mode_status_tracking',updated_list)

            self.rope_bridge_distance+=self.count
            self.game.set_player_stats('rope_bridge_distance',self.rope_bridge_distance)

            score_value = self.score_value_start*self.count
            self.game.set_player_stats('rope_bridge_score',score_value)
            self.game.set_player_stats('last_mode_score',score_value)


            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #reset music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)

            #clear display
            self.clear()

            #close gates
            self.close_gates('left')
            self.close_gates('right')

            #reset lamps
            self.reset_lamps()

        def mode_tick(self):
            pass


        def open_gates(self,side):
            if side=='left':
                 self.game.coils.rightControlGate.pulse(0)
            elif side=='right':
                 self.game.coils.leftControlGate.pulse(0)

        def close_gates(self,side):
            if side=='left':
                 self.game.coils.rightControlGate.disable()
            elif side=='right':
                 self.game.coils.leftControlGate.disable()


        def voice_call(self,count,delay=None,label="rb_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

            #additional speech calls
#            if count==0:
#                self.delay(name='aux_mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=1)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True))
     

        def mode_progression(self):

            self.count+=1

            #load progression animation
            #self.delay(name='scene_anim_delay', event_type=None, delay=2, handler=self.load_scene_anim, param=self.count)
            self.load_scene_anim(self.count)
            
            #play sound
            self.game.sound.play('rb_shot_hit')


        def award_score(self,score_value=0):
            score_value = self.score_value_start

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3)
            self.game.score(score_value)

        def award_completed_score(self,score_value=0):
            score_value = self.score_value_completed

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3)
            self.game.score(score_value)

            
        def mode_bonus(self):
            self.game.score(score_value_bonus)


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'on')

        def clear(self):
            self.layer = None


        def sw_leftRampMade_active(self, sw):
            self.mode_progression()

            return procgame.game.SwitchStop

        def sw_rightRampMade_active(self, sw):
            self.mode_progression()

            return procgame.game.SwitchStop
        