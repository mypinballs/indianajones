# The Three Challenges Game Mode

__author__="jim"
__date__ ="$31/12/12$"


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
		super(ModeScoreLayer, self).__init__(x, y, font,justify)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


class The_Three_Challenges(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(The_Three_Challenges, self).__init__(game, priority)

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['The 3 Challenges Timer'])
            print("3 Challenges Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(86, 9, self.game.fonts['num_09Bx7'],self)
            
            #sound setup
            self.game.sound.register_music('ttc_background_play', music_path+"the_three_challenges.aiff")
            self.game.sound.register_sound('ttc_shot_hit', sound_path+"poa_start.aiff")
            self.game.sound.register_sound('ttc_s0', speech_path+"meddling_with_powers.aiff")
            self.game.sound.register_sound('ttc_s1', speech_path+"the_breath_of_god.aiff")
            self.game.sound.register_sound('ttc_s2', speech_path+"the_word_of_god.aiff")
            self.game.sound.register_sound('ttc_s3', speech_path+"the_path_of_god.aiff")

            #lamps setup
            self.lamps = ['leftRampArrow']
            
            self.reset()


        def reset(self):
            #var setup
            self.count = 0
            self.score_value_boost = 1000000
            self.score_value_start = 5000000
            self.score_value_extra = 2000000
            self.poa_lanes_needed = 1

        def load_scene_anim(self,count):
            scene_num=1

            bgnd_anim = dmd.Animation().load(game_path+"dmd/ttc_scene_"+str(scene_num)+".dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=bgnd_anim.frames,hold=False,opaque=False,repeat=True,frame_time=2)

            item1 = dmd.Animation().load(game_path+"dmd/ttc_breath.dmd")
            item2 = dmd.Animation().load(game_path+"dmd/ttc_word.dmd")
            item3 = dmd.Animation().load(game_path+"dmd/ttc_path.dmd")

            #set all items to blank initially
            item_layer1 = dmd.FrameLayer(frame=item1.frames[1])
            item_layer1.composite_op ="blacksrc"
            item_layer2 = dmd.FrameLayer(frame=item2.frames[1])
            item_layer2.composite_op ="blacksrc"
            item_layer3 = dmd.FrameLayer(frame=item3.frames[1])
            item_layer3.composite_op ="blacksrc"

            if self.count>=1:
                 item_layer1 =  dmd.FrameLayer(frame=item1.frames[0])
                 item_layer1.composite_op ="blacksrc"
                 item_layer1.target_x=8
                 item_layer1.target_y=18
            if self.count>=2:
                 item_layer2 =  dmd.FrameLayer(frame=item2.frames[0])
                 item_layer2.composite_op ="blacksrc"
                 item_layer2.target_x=55
                 item_layer2.target_y=18
            if self.count>=3:
                 item_layer3 =  dmd.FrameLayer(frame=item3.frames[0])
                 item_layer3.composite_op ="blacksrc"
                 item_layer3.target_x=94
                 item_layer3.target_y=16

            info_layer_1 = dmd.TextLayer(128/2, 8, self.game.fonts['07x5'], "center", opaque=False)
            info_layer_1.set_text("GET ALL LIT LANES",blink_frames=4, color=dmd.PURPLE)
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,item_layer1,item_layer2,item_layer3,info_layer_1,self.timer_layer])

        def load_mp_instructions(self):
            anim = dmd.Animation().load(game_path+"dmd/poa_instructions.dmd")
            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=2)


        def load_bgnd_anim(self):
            if self.count<3:
                self.bgnd_anim = "dmd/the_three_challenges_bgnd.dmd"
                anim = dmd.Animation().load(game_path+self.bgnd_anim)
                self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=9)
                self.score_layer.justify='center'
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.info_layer])
            else:
                self.mode_select.end_scene()

        def mode_started(self):
            #load player stats
            self.challenges_collected = self.game.get_player_stats('challenges_collected');
            #update path mode var
            self.game.set_player_stats("path_mode_started",True)
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, 25, self.game.fonts['07x5'],self.timer,"right")
            self.info_layer = dmd.TextLayer(86, 18, self.game.fonts['07x5'], "center", opaque=False)
            self.info_layer.set_text("SHOOT RIGHT RAMP",blink_frames=4,color=dmd.PURPLE)

            #turn on coils and flashers
            self.game.coils.flasherPOA.schedule(0x30003000, cycle_seconds=0, now=True)
            self.game.coils.divertorMain.pulse(50)
            self.game.coils.divertorHold.pulse(0)

            #load animation
            self.load_bgnd_anim()
            
            #start mode music & speech
            self.game.sound.play_music('ttc_background_play', loops=-1)
            #play speech
            self.voice_call(0,0.5)

            #update_lamps
            self.update_lamps()

        def mode_stopped(self):
            #save player stats
            self.challenges_collected+=self.count
            self.game.set_player_stats('challenges_collected',self.challenges_collected)

            score_value = self.score_value_start*self.count
            self.game.set_player_stats('the_three_challenges_score',score_value)
            self.game.set_player_stats('last_mode_score',score_value)

            #turn off coils & flashers
            self.game.coils.flasherPOA.disable()
            self.game.coils.divertorHold.disable()

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #update poa player stats
            self.game.set_player_stats("path_mode_started",False)
            self.game.set_player_stats("poa_queued",False)


            #reset music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)

            #clear display
            self.clear()

            #reset lamps
            self.reset_lamps()

        def mode_tick(self):
            pass


        def voice_call(self,count,delay=None,label="ttc_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)
     

        def mode_progression(self):

            self.game.mini_playfield.sts_path_sequence(self.poa_lanes_needed)

            #turn off flasher
            self.game.coils.flasherPOA.disable()
            
            #load progression animations
            self.load_mp_instructions()
            self.delay(name='scene_anim_delay', event_type=None, delay=2, handler=self.load_scene_anim, param=self.count)

            #release ball
            self.delay(name='release_ball', event_type=None, delay=4, handler=self.release_ball)

            #play speech
            self.voice_call(self.count+1,4)

            #award basic score
            self.game.score(self.score_value_start)


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
            self.count+=1
            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)

        def sw_miniBottomRight_active(self, sw):
            self.count+=1
            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)

        def sw_miniTopHole_active(self, sw):
            self.count+=1
            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)
            return procgame.game.SwitchStop

        def sw_miniBottomHole_active(self, sw):
            self.count+=1
            self.delay(name='load_bgnd_anim', event_type=None, delay=2, handler=self.load_bgnd_anim)
            return procgame.game.SwitchStop


        