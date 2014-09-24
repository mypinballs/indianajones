# Castle Grunwald Game Mode

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
		super(ModeScoreLayer, self).__init__(x, y, font,justify)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


class Castle_Grunwald(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Castle_Grunwald, self).__init__(game, priority)
            
            #logging
            self.log = logging.getLogger('ij.castle_grunwald')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Castle Grunwald Timer'])
            self.log.info("CG Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['07x5'], self)
            self.award_layer = dmd.TextLayer(128/2, 4, self.game.fonts['23x12'], "center", opaque=False)
            self.award_layer.composite_op ="blacksrc"
            
            #sound setup
            self.game.sound.register_music('castle_grunwald_play', music_path+"castle_grunwald.aiff")
            self.game.sound.register_sound('cg_target_hit', sound_path+"rubble.aiff")
            self.game.sound.register_sound('cg_speech0', speech_path+"i_came_here_to_save_you.aiff")
            self.game.sound.register_sound('cg_speech1', speech_path+"you_call_this_archeology.aiff")
            self.game.sound.register_sound('cg_speech2', sound_path+"machine_gun.aiff")
            self.game.sound.register_sound('cg_speech3', speech_path+"come_on_dad.aiff")

            self.game.sound.register_sound('cg_speech11', speech_path+"whos_gonna_save_you_junior.aiff")
            self.game.sound.register_sound('cg_speech12', speech_path+"mailed_to_marx_bros.aiff")
            self.game.sound.register_sound('cg_speech13', speech_path+"i_told_you.aiff")
            self.game.sound.register_sound('cg_speech14', speech_path+"dont_call_me_junior.aiff")
            self.game.sound.register_sound('cg_speech15', sound_path+"motorbike.aiff")




            #var setup
            self.count = 0
            self.hits = 3
            self.score_value_boost = 5000000
            self.score_value_start = 5000000
            self.score_value_extra = 2000000
            
            
            self.reset()


        def reset(self):
           pass

        def load_scene_anim(self,count):
            self.bgnd_anim = "dmd/castle_grunwald_scene_"+str(count)+".dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False,frame_time=6)
            self.layer = self.bgnd_layer #dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.award_layer,self.info_layer])

            #cancel extra speech calls queued
            self.cancel_delayed('aux_mode_speech_delay')

            if self.count==1:
                self.voice_call(count,1)
            else:
                self.voice_call(count)

            if self.count<self.hits:
                if self.count==2:
                    self.delay(name='animation_end_delay', event_type=None, delay=4, handler=self.load_bgnd_anim)
                else:
                    self.bgnd_layer.add_frame_listener(-1, self.load_bgnd_anim)
            else:
                self.bgnd_layer.add_frame_listener(-1,self.clear)#added to stop mutliple calls of end scene from hold=true animation
                self.bgnd_layer.add_frame_listener(-1,self.mode_select.end_scene)


        def load_bgnd_anim(self):
            self.bgnd_anim = "dmd/castle_grunwald_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])


        def mode_started(self):
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, -1, self.game.fonts['07x5'],self.timer)
            self.info_layer = dmd.TextLayer(128/2, 26, self.game.fonts['07x5'], "center", opaque=False)
            self.info_layer.set_text("HIT CAPTIVE BALL", blink_frames=10, color=dmd.PURPLE)

            #load animation
            self.load_bgnd_anim()
            
            #start mode music & speech
            self.game.sound.play_music('castle_grunwald_play', loops=-1)
            self.delay(name='mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=self.count)

            #knock target down if needed
            self.log.debug("Setup Drop Target for cg")
            if self.game.switches.singleDropTop.is_inactive():
                self.game.coils.totemDropDown.pulse(30)
                self.log.debug("drop target should be down")

        def voice_call(self,count,delay=None):
            if delay==None:
                self.game.sound.play_voice("cg_speech"+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

            #additional speech calls
            if count==0:
                self.delay(name='aux_mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=11)
                self.delay(name='aux_mode_speech_delay', event_type=None, delay=6, handler=self.voice_call, param=12)
            if count==2:
                self.delay(name='aux_mode_speech_delay', event_type=None, delay=1.2, handler=self.voice_call, param=13)
                self.delay(name='aux_mode_speech_delay', event_type=None, delay=2.5, handler=self.voice_call, param=14)
            if count==3:
                self.delay(name='aux_mode_speech_delay', event_type=None, delay=1, handler=self.voice_call, param=15)



        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)


        def mode_tick(self):
            pass

        def mode_stopped(self):
            #update mode select list - get the idol is mode 0 in list
#            current_list = self.game.get_player_stats('mode_status_tracking');
#            updated_list =current_list
#            updated_list[0]=1
#
#            self.game.set_player_stats('mode_status_tracking',updated_list)

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #reset music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)
            
            #clear display
            self.clear()

            #reset drop target
            self.game.coils.totemDropUp.pulse()
            

        def mode_progression(self):

            self.count+=1

            score_value = self.score_value_boost*self.count +self.score_value_start
            self.game.set_player_stats('castle_grunwald_score',score_value)
            self.game.set_player_stats('last_mode_score',self.game.get_player_stats('castle_grunwald_score' ))
            #set text layers
            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=2, color=dmd.CREAM)

            self.delay(name='scene_anim_delay', event_type=None, delay=2, handler=self.load_scene_anim, param=self.count)
            
            self.game.score(score_value)
            self.game.sound.play('cg_target_hit')
            


        def update_lamps(self):
            pass

        def clear(self):
            self.layer = None


        def sw_singleDropTop_active(self, sw):
            return procgame.game.SwitchStop

        def sw_captiveBallFront_active(self, sw):
            return procgame.game.SwitchStop

        def sw_captiveBallFront_active_for_200ms(self, sw):
            self.mode_progression()

            return procgame.game.SwitchStop
        

        def sw_captiveBallBack_active(self, sw):
            #add extra points for hitting ball to back of capture ball area
            self.score_value_boost+=self.score_value_extra

            return procgame.game.SwitchStop
 