# Well Of Souls Game Mode

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
	def __init__(self, x, y, font,mode, opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,mode)
		self.mode = mode
                self.justify="center"
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()
            
class BallsInPlayLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, opaque=False):
		super(BallsInPlayLayer, self).__init__(x, y, font,mode)
		self.mode = mode
                self.justify="center"
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_bip()

		return super(BallsInPlayLayer, self).next_frame()




class Well_Of_Souls(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Well_Of_Souls, self).__init__(game, priority)

            self.log = logging.getLogger('ij.wellOfSouls')
            #setup link back to mode_select mode
            self.mode_select = mode_select

            #user defined game settings config
            self.bip_start = int(self.game.user_settings['Gameplay (Feature)']['Well Of Souls BIP Start'])
            self.ball_save_time = int(self.game.user_settings['Gameplay (Feature)']['Well Of Souls Ball Save Timer'])
            self.log.info("Well Of Souls BIP Start is: "+str(self.bip_start))
            self.log.info("Well Of Souls Ball Save Time is: "+str(self.ball_save_time))

            #screen setup
            self.score_layer = ModeScoreLayer(43, 2, self.game.fonts['num_09Bx7'], self)
            self.bip_layer = BallsInPlayLayer(43, 12, self.game.fonts['07x5'], self)
            self.info_layer = dmd.TextLayer(128/2, 20, self.game.fonts['07x5'], "center", opaque=False)
            self.award_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            #self.award_layer.composite_op='blacksrc'
            
            #sound setup
            self.game.sound.register_music('wos_background_play', music_path+"well_of_souls.aiff")
            self.game.sound.register_sound('wos_shot_hit', sound_path+"flames.aiff")
            self.game.sound.register_sound('wos_s0', speech_path+"you_go_first.aiff")
            self.game.sound.register_sound('wos_s1', speech_path+"why_snakes.aiff")
            self.game.sound.register_sound('wos_s2', sound_path+"snake2.aiff")
            self.game.sound.register_sound('wos_s3', sound_path+"torch.aiff")

            #lamps setup
            self.lamps = ['centerLock']
            
            self.reset()


        def reset(self):
            #var setup
            self.count = 0
            self.score_value_boost = 1000000
            self.score_value_start = 2000000
            self.score_value_bonus = 2000000
            self.running_score_value = 0
            self.mode_running=False
            self.reset_drop_count = 6

        def load_scene_anim(self,count):

            #set the scene number to load depending on shots made
            #only 1 scene for this mode
            scene_num=1

            self.scene_anim = "dmd/wos_scene_"+str(scene_num)+".dmd"
            anim = dmd.Animation().load(game_path+self.scene_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
            self.scene_layer.add_frame_listener(-1,self.award_score)
            self.scene_layer.add_frame_listener(-1, self.load_bgnd_anim)
            self.layer = self.scene_layer

            #cancel any queued sounds from other anims
            self.cancel_delayed('snake_sounds_delay')
            self.cancel_delayed('torch_sounds_delay')

        def load_bgnd_anim(self):
            self.bgnd_anim = "dmd/wos_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.bip_layer,self.info_layer,self.award_layer])

            #loads sounds linked to anim
            self.bgnd_layer.add_frame_listener(64,self.torch_sounds)
            self.bgnd_layer.add_frame_listener(133,self.torch_sounds)

            self.bgnd_layer.add_frame_listener(10,self.snake_sounds)
            #self.bgnd_layer.add_frame_listener(22,self.snake_sounds)
            self.bgnd_layer.add_frame_listener(94,self.snake_sounds)
            self.bgnd_layer.add_frame_listener(115,self.snake_sounds)

            #self.snake_sounds(8)
            #self.torch_sounds(6)

        def mode_started(self):
            #load player stats
            self.snakes_torched = self.game.get_player_stats('snakes_torched');

            #set mode player stats
            self.game.set_player_stats('multiball_mode_started',True)
        
            #setup additonal layers
            #self.info_layer.set_text("SHOOT LIT SHOTS",blink_frames=1000)

            #load animation
            self.load_bgnd_anim()
            
            #start mode music, speech & sounds
            self.game.sound.play_music('wos_background_play', loops=-1)
            self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.voice_call, param=self.count)
            

            #launch required number of balls
            if self.game.idol.balls_in_idol>0:
                 self.game.idol.empty()
                 
            self.game.trough.launch_balls(self.bip_start-self.game.idol.balls_in_idol-1, self.ball_launch_callback, False)
            #debug trough
            #self.game.trough.debug()

            #start ball save
            self.game.ball_save.start(time=5)


            #update_lamps
            self.update_lamps()



        def mode_stopped(self):
            #save player stats
            self.snakes_torched+=self.count
            self.game.set_player_stats('snakes_torched',self.snakes_torched)

            score_value = self.running_score_value
            self.game.set_player_stats('well_of_souls_score',score_value)
            self.game.set_player_stats('last_mode_score',score_value)

            #update poa & mode player stats
            self.game.set_player_stats("multiball_mode_started",False)
            self.game.set_player_stats("poa_queued",False)

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')
            self.cancel_delayed('snake_sounds_delay')
            self.cancel_delayed('torch_sounds_delay')

            #reset music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)

            #update idol state
            self.game.idol.home()

            #clear display
            self.clear()

            #reset drops
            self.reset_drops()

            #reset lamps
            self.reset_lamps()

        def mode_tick(self):
            if self.game.trough.num_balls_in_play==1 and self.mode_running:
                self.mode_select.end_scene()


        def ball_launch_callback(self):

            if self.game.trough.num_balls_to_launch==0:
                self.mode_running=True
                self.log.info("WOS: Mode Running")

            self.game.ball_save.start(num_balls_to_save=self.bip_start, time=self.ball_save_time, now=True, allow_multiple_saves=True)

                

        def reset_drops(self):
            self.game.coils.centerDropBank.pulse(100)


        def voice_call(self,count,delay=None,label="wos_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

            #additional speech calls
            if count==0:
                self.delay(name='aux_mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=1)

        def sound_call(self,count,delay=None,label="wos_s"):
            if delay==None:
                self.game.sound.play(label+str(count))
            else:
                self.delay(name='mode_sound_delay', event_type=None, delay=delay, handler=self.sound_call, param=count)


        def snake_sounds(self,delay=None):
            #method that repeats a series of sound/voice calls at a preset time until cancelled
            start_delay = 0
           # interval = 1
            self.sound_call(2,start_delay)
            #self.sound_call(2,start_delay+interval)
           
            #self.delay(name='snake_sounds_delay', event_type=None, delay=delay, handler=self.snake_sounds, param=delay)

        def torch_sounds(self,delay=None):
            #method that repeats a series of sound/voice calls at a preset time until cancelled
            #start_delay = 0.1
            #interval = 2.5
            #self.sound_call(3,start_delay)
            #self.sound_call(3,start_delay+interval)

            #self.delay(name='torch_sounds_delay', event_type=None, delay=delay, handler=self.torch_sounds, param=delay)

            self.sound_call(3)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)

        def update_bip(self):
            balls_in_play = self.game.trough.num_balls_in_play
            self.bip_layer.set_text(locale.format("%d", balls_in_play)+" BALLS IN PLAY", True, color=dmd.MAGENTA)

     

        def mode_progression(self):

            self.count+=1

            #load progression animation
            self.load_scene_anim(self.count)
            
            #play sound
            self.game.sound.play('wos_shot_hit')

            #update idol state
            self.game.idol.nolock()

            #reset drops after certain amount of succesfull shots
            if self.count>=self.reset_drop_count:
                self.reset_drops()



        def award_score(self,score_value=0):
            score_value = self.score_value_start * self.game.trough.num_balls_in_play

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3)
            self.game.score(score_value)
            
            #update runing total - needed for this mode as can't be calculated at end
            self.running_score_value +=score_value


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'on')

        def clear(self):
            self.layer = None


        def sw_centerEnter_active(self, sw):
            self.mode_progression()

            return procgame.game.SwitchStop

        def sw_shooterLane_active_for_500ms(self,sw):
            self.game.coils.ballLaunch.pulse(50)
            #debug
            self.log.info("WOS Debug: Balls in Trough is:,%s",self.game.trough.num_balls())
            self.log.info("WOS Debug: Balls in Play %s",self.game.trough.num_balls_in_play)
            return procgame.game.SwitchStop

