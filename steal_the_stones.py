# Steal The Stones Game Mode

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
class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="center", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,mode)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


class Steal_The_Stones(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Steal_The_Stones, self).__init__(game, priority)

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Steal The Stones Timer'])
            print("Monkey Brains Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(60, 10, self.game.fonts['num_09Bx7'], self)
            self.award_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)
            
            #sound setup
            self.game.sound.register_music('sts_background_play', music_path+"steal_the_stones.aiff")
            self.game.sound.register_sound('sts_shot_hit', sound_path+"poa_start.aiff")
            self.game.sound.register_sound('sts_s0', speech_path+"the_stones_are_mine.aiff")
            self.game.sound.register_sound('sts_s1', speech_path+"what_a_vivid_imagination.aiff")
            self.game.sound.register_sound('sts_s2', speech_path+"moran_prepare_to_meet_kali.aiff")
            self.game.sound.register_sound('sts_s3', speech_path+"you_dare_not_do_that.aiff")

            #lamps setup
            self.lamps = ['leftLoop','rightLoop','leftRampArrow','rightRampArrow']
            
            self.reset()


        def reset(self):
            #var setup
            self.count = 0
            self.score_value_boost = 1000000
            self.score_value_start = 8000000
            self.score_value_extra = 2000000

        def load_scene_anim(self,count):
            scene_num=1

            self.scene_anim = "dmd/sts_scene_"+str(scene_num)+".dmd"
            anim = dmd.Animation().load(game_path+self.scene_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=True,frame_time=2)
            info_layer_1 = dmd.TextLayer(128/2, 8, self.game.fonts['07x5'], "center", opaque=False)
            info_layer_1.set_text("GET ALL LIT LANES",blink_frames=10000)
            self.layer = dmd.GroupedLayer(128, 32, [self.scene_layer,info_layer_1,self.timer_layer])

        def load_mp_instructions(self):
            anim = dmd.Animation().load(game_path+"dmd/poa_instructions.dmd")
            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=2)


        def load_bgnd_anim(self):
            self.bgnd_anim = "dmd/steal_the_stones_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=2)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])


        def mode_started(self):
            #load player stats
            self.stones_collected = self.game.get_player_stats('stones_collected');
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, 25, self.game.fonts['07x5'],self.timer,"right")
            self.info_layer = dmd.TextLayer(80, 20, self.game.fonts['07x5'], "center", opaque=False)
            self.info_layer.set_text("SHOOT RIGHT RAMP",blink_frames=100000)

            #turn on coils and flashers
            self.game.coils.flasherPOA.schedule(0x30003000, cycle_seconds=0, now=True)
            self.game.coils.divertorMain.pulse(50)
            self.game.coils.divertorHold.pulse(0)

            #load animation
            self.load_bgnd_anim()
            
            #start mode music & speech
            self.game.sound.play_music('sts_background_play', loops=-1)
            #self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.play_dialog)
            self.play_dialog(0.5)

            #update_lamps
            self.update_lamps()

        def mode_stopped(self):
            #save player stats
            self.stones_collected+=self.count
            self.game.set_player_stats('stones_collected',self.stones_collected)

            score_value = self.score_value_start*self.count
            self.game.set_player_stats('steal_the_stones_score',score_value)
            self.game.set_player_stats('last_mode_score',score_value)

            #turn off coils & flashers
            self.game.coils.flasherPOA.disable()
            self.game.coils.divertorHold.disable()

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #reset music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)

            #clear display
            self.clear()

            #reset lamps
            self.reset_lamps()

        def mode_tick(self):
            pass


        def voice_call(self,count,delay=None,label="sts_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

        def play_dialog(self,delay):
            #play mode speech calls at various points
            interval = 0.5
            self.voice_call(0,delay)
            self.voice_call(1,delay+interval)
            self.voice_call(2,delay+(interval*10))
            self.voice_call(3,delay+(interval*20))


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True))
     

        def mode_progression(self):

            self.count+=1
            
            if (self.count==1):
                self.game.mini_playfield.path_sequence()

            #turn off flasher
            self.game.coils.flasherPOA.disable()
            
            #load progression animations
            self.load_mp_instructions()
            self.delay(name='scene_anim_delay', event_type=None, delay=2, handler=self.load_scene_anim, param=self.count)

            #release ball
            self.delay(name='release_ball', event_type=None, delay=4, handler=self.release_ball)

            #play sound
            self.game.sound.play('sts_shot_hit')




        def award_score(self,score_value=0):
            score_value = self.score_value_start

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3)
            self.game.score(score_value)

        def release_ball(self):
            self.game.coils.topLockupMain.pulse()
            self.game.coils.topLockupHold.pulse(200)

            #clear display
            #self.clear()

        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'on')

        def clear(self):
            self.layer = None


        def sw_topPost_active(self, sw):

            self.mode_progression()
            return procgame.game.SwitchStop

        def sw_miniBottomLeft_active(self, sw):
            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)

        def sw_miniBottomRight_active(self, sw):
            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)

        def sw_miniTopHole_active(self, sw):
            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)
            return procgame.game.SwitchStop

        def sw_miniBottomHole_active(self, sw):
            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)
            return procgame.game.SwitchStop
