# Get The Idol Game Mode

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
            self.log = logging.getLogger('ij.get_the_idol')
            
            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Get The Idol Timer'])

            self.score_layer = ModeScoreLayer(0, -1, self.game.fonts['07x5'], self)
            #self.timer_layer = dmd.TimerLayer(128, -1, self.game.fonts['07x5'],self.timer)
            #self.award_layer = dmd.TextLayer(128/2, 12, self.game.fonts['6x6_bold'], "center", opaque=False)
            self.award_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            self.award_layer.composite_op ="blacksrc"

            #sound setup
            self.game.sound.register_music('gti_play', music_path+"get_the_idol_2.aiff")
            self.game.sound.register_sound('target_hit', sound_path+"outlane.aiff")
            self.game.sound.register_sound('gti_speech0', speech_path+"nothing_to_fear_here.aiff")
            self.game.sound.register_sound('gti_speech11', speech_path+"thats_what_scares_me.aiff")
            self.game.sound.register_sound('gti_speech1', speech_path+"throw_me_the_idol.aiff")
            self.game.sound.register_sound('gti_speech12', speech_path+"no_time_to_argue.aiff")
            self.game.sound.register_sound('gti_speech2', speech_path+"give_me_the_whip.aiff")
            self.game.sound.register_sound('gti_speech3', speech_path+"adious_senoir.aiff")

            #var setup
            self.count = 0
            
            self.score_value_boost = 5000000
            self.score_value_start = 5000000
            #self.load_anim(0)
            self.progression_anim_posn = 1
            
            if self.game.user_settings['Gameplay (Feature)']['Get The Idol Difficulty']=='Easy':
                self.hits = 2 #number of hits required to keep drops down
                self.progression_amount = 5 #number of frames to move the animation forward per hit
            elif self.game.user_settings['Gameplay (Feature)']['Get The Idol Difficulty']=='Medium':
                self.hits = 3
                self.progression_amount = 3
            elif self.game.user_settings['Gameplay (Feature)']['Get The Idol Difficulty']=='Hard':
                self.hits = 5
                self.progression_amount = 2
                
                
            self.reset()


        def reset(self):
           pass

#        def load_anim(self,count):
#            self.bgnd_anim = "dmd/get_the_idol_bgnd_"+str(count)+".dmd"
#            anim = dmd.Animation().load(game_path+self.bgnd_anim)
#            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
        
        def load_bgnd_anim(self):
            large_spider_frames = dmd.Animation().load("dmd/gti_lge_spider_sprites.dmd").frames
            sml_spider_frames = dmd.Animation().load("dmd/gti_sml_spider_sprites.dmd").frames
            
            self.large_spider_layer = dmd.AnimatedLayer(frames=large_spider_frames,hold=False,repeat=True,frame_time=6)
            #self.large_spider_layer.target_x=50
            self.large_spider_layer.target_y=10
            self.large_spider_layer.composite_op ="blacksrc"
            
            self.sml_spider_layer1 = dmd.AnimatedLayer(frames=sml_spider_frames,hold=False,repeat=True,frame_time=6)
            self.sml_spider_layer1.target_x=-50
            #self.sml_spider_layer1.target_y=0
            self.sml_spider_layer1.composite_op ="blacksrc"
            
            self.sml_spider_layer2 = dmd.AnimatedLayer(frames=sml_spider_frames,hold=False,repeat=True,frame_time=6)
            self.sml_spider_layer2.target_x=50
            #self.sml_spider_layer2.target_y=0
            self.sml_spider_layer2.composite_op ="blacksrc"

            self.reset_sprites()
            
            self.log.info("spider sprites created")

            self.bgnd_anim = dmd.Animation().load(game_path+"dmd/get_the_idol_bgnd.dmd")
            self.bgnd_layer = dmd.FrameLayer(frame=self.bgnd_anim.frames[0])
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sml_spider_layer1,self.sml_spider_layer2,self.large_spider_layer,self.score_layer,self.timer_layer,self.award_layer])

        def load_progression_anim(self):
            
            
            self.bgnd_anim = dmd.Animation().load(game_path+"dmd/get_the_idol_bgnd.dmd")
            self.bgnd_layer = dmd.AnimatedLayer(frames=self.bgnd_anim.frames[self.progression_anim_posn:self.progression_anim_posn+self.progression_amount],hold=True,opaque=False,repeat=False,frame_time=6)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sml_spider_layer1,self.sml_spider_layer2,self.large_spider_layer,self.score_layer,self.timer_layer,self.award_layer])

            self.progression_anim_posn +=self.progression_amount
            
            
        def reset_sprites(self):
            self.large_spider_layer.target_x =64
            self.sml_spider_layer1.target_y = 18
            self.sml_spider_layer2.target_y = 28
        
        def move_sprites(self):
            self.large_spider_layer.target_x -=6
            self.sml_spider_layer1.target_y -=2
            self.sml_spider_layer2.target_y -=3
            
            self.delay(name='move_sprites',delay=0.2,handler=self.move_sprites)

            if self.large_spider_layer.target_x<-100:
                #self.cancel_delayed('move_sprites')
                self.reset_sprites()
                
        def mode_started(self):
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, -1, self.game.fonts['07x5'],self.timer)
            
            #create animation
            self.load_bgnd_anim()
            self.move_sprites()
            
            self.game.sound.play_music('gti_play', loops=-1)

            self.reset_drops()

            self.delay(name='mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=self.count)


        def voice_call(self,count):
            self.game.sound.play_voice("gti_speech"+str(count))

            self.delay(name='mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=11+count)



        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True),color=dmd.YELLOW)


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

                self.load_progression_anim()
                
                score_value = self.score_value_boost*self.count +self.score_value_start
                self.game.set_player_stats('get_the_idol_score',score_value)
                self.game.set_player_stats('last_mode_score',self.game.get_player_stats('get_the_idol_score' ))
                #set text layers
                self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3, color=dmd.MAGENTA)

                self.game.score(score_value)
                
                #play sounds/speech
                self.game.sound.play('target_hit')
                self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.voice_call, param=self.count)
           
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
