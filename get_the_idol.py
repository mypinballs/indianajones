# Get The Idol Game Mode

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
	def __init__(self, x, y, font,mode, justify="left", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,justify)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


class Get_The_Idol(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Get_The_Idol, self).__init__(game, priority)

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            timer = int(self.game.user_settings['Gameplay (Feature)']['Get The Idol Timer'])

            self.score_layer = ModeScoreLayer(0, -1, self.game.fonts['07x5'], self)
            self.timer_layer = dmd.TimerLayer(128, -1, self.game.fonts['07x5'],timer)
            #self.text_layer = dmd.TextLayer(128/2, 12, self.game.fonts['6x6_bold'], "center", opaque=False)
            self.text_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            self.text_layer.composite_op ="blacksrc"


            #sound setup
            self.game.sound.register_music('gti_play', music_path+"get_the_idol_2.aiff")
            self.game.sound.register_sound('target_hit', sound_path+"outlane.aiff")
            self.game.sound.register_sound('gti_speech0', speech_path+"nothing_to_fear_here.aiff")
            self.game.sound.register_sound('gti_speech11', speech_path+"thats_what_scares_me.aiff")



            #var setup
            self.count = 0
            self.hits = 3
            self.score_value_boost = 5000000
            self.score_value_start = 5000000
            self.load_anim(0)
            
            self.reset()


        def reset(self):
           pass

        def load_anim(self,count):
            self.bgnd_anim = "dmd/get_the_idol_bgnd_"+str(count)+".dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)


        def mode_started(self):
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.text_layer])
            self.game.sound.play_music('gti_play', loops=-1)

            self.reset_drops()

            self.delay(name='mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=self.count)


        def voice_call(self,count):
            self.game.sound.play_voice("gti_speech"+str(count))

            if count==0:
                self.delay(name='mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=11)



        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True))


        def mode_tick(self):
            pass

        def mode_stopped(self):
            #update mode select list - get the idol is mode 0 in list
#            current_list = self.game.get_player_stats('mode_status_tracking');
#            updated_list =current_list
#            updated_list[0]=1
#
#            self.game.set_player_stats('mode_status_tracking',updated_list)

            #stop music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)
            
            #clear display
            self.clear()

        def mode_progression(self,type):

            if self.count<self.hits:
                self.count+=1

                self.load_anim(self.count)
                #self.voice_call("gti_speech"+str(self.count))

                score_value = self.score_value_boost*self.count +self.score_value_start
                self.game.set_player_stats('get_the_idol_score',score_value)
                self.game.set_player_stats('last_mode_score',self.game.get_player_stats('get_the_idol_score' ))
                #set text layers
                self.text_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3, color=dmd.MAGENTA)

            
                self.game.score(score_value)
                self.game.sound.play('target_hit')
            
           
                self.reset_drops()

                
            elif self.count==self.hits and type==1:
                self.completed()

        def completed(self):
            self.bgnd_anim = "dmd/get_the_idol_completed.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,hold=True,frame_time=6)
            #self.layer.transition = dmd.CrossFadeTransition(width=128,height=32)
            #end scene when animation completes
            self.layer.add_frame_listener(-1,self.mode_select.end_scene)
            #self.delay(name='end_delay', event_type=None, delay=1, handler=self.mode_select.end_scene)

            


        def update_lamps(self):
            print("Update Lamps")

        def clear(self):
            self.layer = None

        def reset_drops(self):
            self.game.coils.centerDropBank.pulse(100)


        
        def sw_dropTargetLeft_active(self, sw):
            self.mode_progression(0)

        def sw_dropTargetMiddle_active(self, sw):
            self.mode_progression(0)

        def sw_dropTargetRight_active(self, sw):
            self.mode_progression(0)

        def sw_centerEnter_active(self, sw):
            self.mode_progression(1)
