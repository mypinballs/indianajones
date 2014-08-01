# Choose Wisely Game Mode

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import logging
import random
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

#locale.setlocale(locale.LC_ALL, 'en_GB')

class Choose_Wisely(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Choose_Wisely, self).__init__(game, priority)

            self.log = logging.getLogger('ij.chooseWisely')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #sound setup
            self.game.sound.register_music('cw_background_play', music_path+"choose_wisely.aiff")
            self.game.sound.register_sound('cw_select', sound_path+"choose_cup.aiff")
            self.game.sound.register_sound('cw_speech0', speech_path+"choose_wisely.aiff")
            self.game.sound.register_sound('cw_speech1', speech_path+"chosen_wisely.aiff")
            self.game.sound.register_sound('cw_speech2', speech_path+"chosen_poorly.aiff")
            self.game.sound.register_sound('cw_speech3', speech_path+"burning_scream.aiff")

            #lamps setup
            self.lamps = []
            
            self.reset()


        def reset(self):
            #var setup

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Choose Wisely Choice Timer'])
            print("Choose Wisely Timer is:"+str(self.timer))

            self.count =0
            self.score_value_boost = 5000000
            self.score_value_start = 15000000
            self.score_value_extra = 2000000
            self.score_value =0

            self.sequence_index = 0
            self.correct_choice = 3
            self.user_choice = 3
            self.choose_ready = False


        def load_intro_anim(self):
            self.intro_anim = "dmd/choose_wisely_intro.dmd"
            anim = dmd.Animation().load(game_path+self.intro_anim)
            self.intro_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=False,frame_time=3)
            self.intro_layer.add_frame_listener(-1, self.sequence_start)
            self.layer = self.intro_layer

        def sequence_start(self):
            bgnd_anim = dmd.Animation().load(game_path+"dmd/grail_cups_fixed.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=bgnd_anim.frames,opaque=False,repeat=True,frame_time=3)

            grail_cup = dmd.Animation().load(game_path+"dmd/grail_cup.dmd")
            grail_cup_layer = dmd.AnimatedLayer(frames=grail_cup.frames,opaque=False,repeat=True,frame_time=2)
            grail_cup_layer.composite_op ="blacksrc"
            grail_cup_layer.target_x=56
            grail_cup_layer.target_y=8

            self.info_layer.set_text("FOLLOW FLASHING GRAIL",blink_frames=6)
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,grail_cup_layer,self.info_layer])

            self.generate_sequence()
            self.delay(name='start_sequence_delay', delay=4,handler=self.run_sequence)


        def generate_sequence(self):
            #self.sequence_data=[3,2,1,2,3,4,5,4,5,4,3,2,1,2,3,4,5,4,5,4] # make this randomly created

            self.sequence_data=[]
            value = 3
            self.sequence_data.append(value)
            for i in range(1,10+(self.level*10)):
                value = self.sequence_data[i-1]

                a=value-1
                b=value+1

                if a==0:
                    a=2
                    b=2
                if b==6:
                    a=4
                    b=4
                
                list =[a,b]
                x = random.choice(list)

                self.sequence_data.append(x)

            self.log.info("random sequence is:%s",self.sequence_data)

        def run_sequence(self):
            self.correct_choice = self.sequence_data[len(self.sequence_data)-1]
            self.log.info("Correct Choice is:%s",self.correct_choice)

            if self.sequence_index<len(self.sequence_data)-1:
                start = self.sequence_data[self.sequence_index]
                end = self.sequence_data[self.sequence_index+1]

                calc = start+end
                value=0
            
                if calc==7:
                    value=1
                elif calc==5 or calc==9:
                    value=0
                elif calc==3:
                    value==2
          
                self.load_sequence_anim(value)
                self.sequence_index+=1
            else:
                self.load_choose_anim()


        def load_sequence_anim(self,num):
            level_time = 4
            self.scene_anim = "dmd/grail_cups_move_"+str(num)+".dmd"
            anim = dmd.Animation().load(game_path+self.scene_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=False,frame_time=level_time)
            self.scene_layer.add_frame_listener(-1, self.run_sequence)
            self.layer = self.scene_layer

        def load_choose_anim(self):
            bgnd_anim = dmd.Animation().load(game_path+"dmd/grail_cups_fixed.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=bgnd_anim.frames,opaque=False,repeat=False,frame_time=3)

            arrow_anim = dmd.Animation().load(game_path+"dmd/arrow.dmd")
            self.arrow_layer = dmd.AnimatedLayer(frames=arrow_anim.frames,opaque=False,repeat=False,frame_time=3)
            self.arrow_layer.composite_op = "blacksrc"
            self.arrow_layer.target_x = 64
            self.arrow_layer.target_y =0

            grail_cup = dmd.Animation().load(game_path+"dmd/grail_cup.dmd")
            self.grail_cup_layer = dmd.AnimatedLayer(frames=grail_cup.frames,opaque=False,repeat=True,frame_time=2)
            self.grail_cup_layer.composite_op ="blacksrc"
            self.grail_cup_layer.target_x=-50
            self.grail_cup_layer.target_y=8

            self.info_layer.set_text("FLIPPERS MOVE. GUN PICKS.",blink_frames=6)
            self.choose_ready = True

            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,self.grail_cup_layer,self.info_layer,self.timer_layer,self.arrow_layer])

        def move_left(self):
            if self.arrow_layer.target_x>5:
                self.arrow_layer.target_x -=28
                self.user_choice-=1
            else:
                self.arrow_layer.target_x = 117
                self.user_choice=5

            self.log.info("User choice is:%s",self.user_choice)


        def move_right(self):
            if self.arrow_layer.target_x<117:
                self.arrow_layer.target_x +=28
                self.user_choice+=1
            else:
                self.arrow_layer.target_x = 5
                self.user_choice=1

            self.log.info("User choice is:%s",self.user_choice)


        def load_sucess_anim1(self):
            #cancel the mode timeout
            self.mode_select.cancel_timeout()
            timer=0.9

            #show fixed frame
            scene_anim = dmd.Animation().load(game_path+"dmd/chosen_wisely_speech.dmd")
            scene_layer = item_layer1 = dmd.FrameLayer(frame=scene_anim.frames[0])
            self.layer = scene_layer

            #play speech
            self.voice_call(1)

            #delay for running next anim to sync to speech
            self.delay(name='next_anim_delay', event_type=None, delay=timer, handler=self.load_sucess_anim2)


        def load_sucess_anim2(self):
            #cancel the mode timeout
            self.mode_select.cancel_timeout()

            scene_anim = dmd.Animation().load(game_path+"dmd/chosen_wisely_speech.dmd")
            scene_layer = dmd.AnimatedLayer(frames=scene_anim.frames,opaque=False,repeat=False,frame_time=4)
            scene_layer.add_frame_listener(-1, self.award_score)
            self.layer = scene_layer

            
        def load_fail_anim1(self):
            #play animation
            scene_anim = dmd.Animation().load(game_path+"dmd/face_melt.dmd")
            scene_layer = dmd.AnimatedLayer(frames=scene_anim.frames,opaque=False,repeat=False,frame_time=4)
            scene_layer.add_frame_listener(-1, self.load_fail_anim2)
            #queue speech
            scene_layer.add_frame_listener(5, lambda:self.voice_call(3))
            self.layer = scene_layer


        def load_fail_anim2(self):
            #cancel the mode timeout
            self.mode_select.cancel_timeout()

            #play animation
            scene_anim = dmd.Animation().load(game_path+"dmd/chosen_poorly_speech.dmd")
            scene_layer = dmd.AnimatedLayer(frames=scene_anim.frames,opaque=False,repeat=False,frame_time=6)
            scene_layer.add_frame_listener(-1,lambda:self.end_scene_delay(0.5))
            self.layer = scene_layer

            #play speech
            self.voice_call(2)

            self.score_value = self.score_value_extra
            self.game.score(self.score_value)

        def award_score(self):
            self.score_value = self.score_value_start+(self.score_value_boost*self.level)

            award_layer = dmd.TextLayer(128/2, 4, self.game.fonts['23x12'], "center", opaque=True)
            award_layer.set_text(locale.format("%d",self.score_value,True),blink_frames=2)
            self.layer = award_layer

            self.game.score(self.score_value)
            #up the level for succesfull completion
            self.level+=1

            self.end_scene_delay(2)
             

        def end_scene_delay(self,timer):
            self.delay(name='scene_cleanup', event_type=None, delay=timer, handler=self.mode_select.end_scene)


        def chosen(self):
            
            timer=2
            cup_posns = [0,28,56,84,112]

            #play sound
            self.game.sound.play('gun_shot')

            #show correct cup
            self.grail_cup_layer.target_x=cup_posns[self.correct_choice-1]

            #compare user choice
            if self.user_choice==self.correct_choice:
                self.delay(name='next_anim_delay', event_type=None, delay=timer, handler=self.load_sucess_anim1)
            else:
                self.delay(name='next_anim_delay', event_type=None, delay=timer, handler=self.load_fail_anim1)


        def mode_started(self):
            #load player stats
            self.level = self.game.get_player_stats('choose_wisely_level');

            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, -1, self.game.fonts['07x5'],self.timer,"right")
            self.info_layer = dmd.TextLayer(128/2, -1, self.game.fonts['07x5'], "center", opaque=False)
            #self.info_layer.set_text("SHOOT LIT SHOTS",blink_frames=1000)

            #load animation
            self.load_intro_anim()
            
            #start mode music & speech
            self.game.sound.play_music('cw_background_play', loops=-1)
            self.voice_call(0)

            #update_lamps
            self.update_lamps()

            #turn off flippers
            self.game.enable_flippers(enable=False)

        def mode_stopped(self):
            self.game.set_player_stats('choose_wisely_level',self.level)

            self.game.set_player_stats('choose_wisely_score',self.score_value)
            self.game.set_player_stats('last_mode_score',self.score_value)

            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #reset music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)

            #clear display
            self.clear()

            #turn on flippers
            self.game.enable_flippers(enable=True)

            #eject ball
            self.game.coils.leftEject.pulse()

            #reset lamps
            self.reset_lamps()

        def mode_tick(self):
            pass
        

        def voice_call(self,count,delay=None):
            if delay==None:
                self.game.sound.play("cw_speech"+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'on')

        def clear(self):
            self.layer = None


        def sw_flipperLwL_active(self, sw):

            if self.choose_ready:
                self.move_left()

            return procgame.game.SwitchStop

        def sw_flipperLwR_active(self, sw):

            if self.choose_ready:
                self.move_right()

            return procgame.game.SwitchStop

        def sw_gunTrigger_active(self, sw):

            if self.choose_ready:
                self.chosen()
            return procgame.game.SwitchStop


      
 