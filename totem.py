# Totem Mode
# Quick Mulitball, single drop & captive ball

__author__="jim"
__date__ ="$14/12/2012$"

import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="center", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,mode)
		self.mode = mode

	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()

class Totem(game.Mode):

	def __init__(self, game, priority):
            super(Totem, self).__init__(game, priority)
            self.log = logging.getLogger('ij.totem')
            
            self.totem_ani = "dmd/totem.dmd"

            self.game.sound.register_sound('rubble', sound_path+"rubble.aiff")
            self.game.sound.register_sound('explosion', sound_path+"explosion.aiff")
            self.game.sound.register_music('qm_ready', music_path+"quick_multiball_ready.aiff")
            self.game.sound.register_music('qm_running', music_path+"quick_multiball_play.aiff")
            self.game.sound.register_sound('qm_jackpot0', speech_path+"the_idol_of_the_incas.aiff")
            self.game.sound.register_sound('qm_jackpot1', speech_path+"the_diamond_of_shanghai.aiff")
            self.game.sound.register_sound('qm_jackpot2', speech_path+"the_remains_of_nurachi.aiff")
            self.game.sound.register_sound('qm_jackpot3', speech_path+"the_cross_of_coronado.aiff")
            self.game.sound.register_sound('qm_jackpot4', speech_path+"the_fish_of_tales.aiff")
            self.game.sound.register_sound('excellent', speech_path+"excellent.aiff")

            self.totem_value_start = 2000000
            self.totem_value_boost = 1000000

            self.jackpot_base_value = 10000000
            self.jackpot_boost_value = 5000000

            self.add_ball_value = 1000000

            self.mulitball_started = False
            self.multiball_running = False
            self.balls_needed = 2


        def reset(self):
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Captive Multiball Start Timer'])
            self.hits_needed = int(self.game.user_settings['Gameplay (Feature)']['Captive Multiball Start'])
            self.count = 0
            self.jackpot_count = 0
            self.multiball_started= False
            self.game.coils.totemDropUp.pulse()
            self.game.effects.drive_flasher('flasherTotem','off')

        def mode_started(self):
            self.reset()

            self.text_layer = dmd.TextLayer(14, 11, self.game.fonts['num_09Bx7'], "left", opaque=False)
            self.score_layer = ModeScoreLayer(90, 1, self.game.fonts['num_09Bx7'], self)


        def mode_stopped(self):
            pass

        def mode_tick(self):
            if self.multiball_started:
                self.balls_in_play = self.game.trough.num_balls_in_play

                if self.balls_in_play==self.balls_needed and self.multiball_running==False:
                    #start tracking
                    self.multiball_running = True;
                    self.game.set_player_stats('quick_multiball_running',self.multiball_running)

                if self.multiball_running:
                    self.multiball_tracking()

        def hit(self):

            totem_value = self.totem_value_boost*self.count +self.totem_value_start

            #self.bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+self.dmd_image).frames[0])
            anim = dmd.Animation().load(game_path+self.totem_ani)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)
            self.bgnd_layer.add_frame_listener(-1, self.clear)

            #set text layers
            self.text_layer.set_text(locale.format("%d",totem_value,True),blink_frames=4)
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.text_layer])
            
            #set target
            self.delay(name='reset_target', event_type=None, delay=1, handler=self.setup_target)

            #base calls
            self.game.sound.play('rubble')
            self.game.score(totem_value)
            self.game.lampctrl.play_show('hit', repeat=False,callback=self.game.update_lamps)

            self.count+=1


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True))

        def update_lamps(self):
            #print("Update Lamps")
            pass

        def clear(self):
            self.layer = None

        def setup_target(self):
            if self.count<self.hits_needed:
                self.game.coils.totemDropUp.pulse()
            elif not self.game.get_player_stats('multiball_running'):
                self.multiball_ready()


        def multiball_ready(self):
            bgnd_anim = dmd.Animation().load(game_path+"dmd/qm_bgnd.dmd")
            bgnd_layer = dmd.FrameLayer(frame=bgnd_anim.frames[0])

            ball_anim = dmd.Animation().load(game_path+"dmd/ball.dmd")
            ball_layer = dmd.AnimatedLayer(frames=ball_anim.frames,repeat=True,frame_time=6)
            ball_layer.composite_op ="blacksrc"
            ball_layer.target_x=92
            ball_layer.target_y=4

            self.score_layer.x = 42
            self.score_layer.y=0
            self.score_layer.justify='center'
            info_layer1 = dmd.TextLayer(42, 11, self.game.fonts['8x6'], "center", opaque=False)
            info_layer2 = dmd.TextLayer(42, 19, self.game.fonts['07x5'], "center", opaque=False)

            info_layer1.set_text("HIT BALL")
            info_layer2.set_text("FOR MULTIBALL")

            timer_layer = dmd.TimerLayer(128, -1, self.game.fonts['07x5'],self.timer,"right")

            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_layer1,info_layer2,ball_layer,self.score_layer,timer_layer])
            
            self.game.effects.drive_flasher('flasherTotem','fast',time=0)

            self.game.sound.stop_music()
            self.game.sound.play_music('qm_ready', loops=-1)
            self.delay(name='timeout_delay', delay=self.timer, handler=self.timeout)


        def timeout(self):
            self.log.info("timeout called")
            self.clear()
            self.reset()

            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)


        def multiball(self):
            #cancel timeout delay
            self.cancel_delayed("timeout_delay")
            #update status & tracking vars
            self.multiball_started = True
            self.game.set_player_stats('quick_multiball_started',self.multiball_started)

            #setup display
            bgnd = dmd.Animation().load(game_path+"dmd/qm_bgnd_running.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=bgnd.frames,repeat=True,frame_time=6)

            treasure1 = dmd.Animation().load(game_path+"dmd/treasure_ioti.dmd")
            treasure2 = dmd.Animation().load(game_path+"dmd/treasure_dos.dmd")
            treasure3 = dmd.Animation().load(game_path+"dmd/treasure_ron.dmd")
            treasure4 = dmd.Animation().load(game_path+"dmd/treasure_coc.dmd")
            treasure5 = dmd.Animation().load(game_path+"dmd/treasure_fot.dmd")

            #set all items to blank initially
            item_layer1 = dmd.FrameLayer(frame=treasure1.frames[1])
            item_layer1.composite_op ="blacksrc"
            item_layer2 = dmd.FrameLayer(frame=treasure2.frames[1])
            item_layer2.composite_op ="blacksrc"
            item_layer3 = dmd.FrameLayer(frame=treasure3.frames[1])
            item_layer3.composite_op ="blacksrc"
            item_layer4 = dmd.FrameLayer(frame=treasure4.frames[1])
            item_layer4.composite_op ="blacksrc"
            item_layer5 = dmd.FrameLayer(frame=treasure5.frames[1])
            item_layer5.composite_op ="blacksrc"


            if self.jackpot_count>=1:
                 item_layer1 =  dmd.FrameLayer(frame=treasure1.frames[0])
                 item_layer1.composite_op ="blacksrc"
                 item_layer1.target_x=2
                 item_layer1.target_y=7
            if self.jackpot_count>=2:
                 item_layer2 =  dmd.FrameLayer(frame=treasure2.frames[0])
                 item_layer2.composite_op ="blacksrc"
                 item_layer2.target_x=20
                 item_layer2.target_y=1
            if self.jackpot_count>=3:
                 item_layer3 =  dmd.FrameLayer(frame=treasure3.frames[0])
                 item_layer3.composite_op ="blacksrc"
                 item_layer3.target_x=113
                 item_layer3.target_y=6
            if self.jackpot_count>=4:
                 item_layer4 =  dmd.FrameLayer(frame=treasure4.frames[0])
                 item_layer4.composite_op ="blacksrc"
                 item_layer4.target_x=85
                 item_layer4.target_y=1
            if self.jackpot_count>=5:
                 item_layer5 =  dmd.FrameLayer(frame=treasure5.frames[0])
                 item_layer5.composite_op ="blacksrc"
                 item_layer5.target_x=40
                 item_layer5.target_y=0

            self.score_layer.x = 64
            self.score_layer.y=15
            self.score_layer.justify='center'

            info_layer1 = dmd.TextLayer(64, 25, self.game.fonts['07x5'], "center", opaque=False)
            info_layer1.set_text("HIT BALL")


            #update display
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,item_layer1,item_layer2,item_layer3,item_layer4,item_layer5,info_layer1,self.score_layer])

        
            if self.multiball_running==False:

                #start the main multiball music
                self.game.sound.stop_music()
                self.game.sound.play_music('qm_running', loops=-1)

                #launch balls
                self.launch_ball()
                
            #store the balls_in idol here for reference
            self.balls_in_idol = self.game.idol.balls_in_idol
            

        def launch_ball(self):
            self.game.trough.launch_balls(1,callback=self.launch_callback,stealth=False) #stealth false, bip +1
            self.game.ball_save.start(time=5)
            
            
        def launch_callback(self):
            pass
        
        
        def multiball_tracking(self):

            #end check
            if self.balls_in_play==1 and self.multiball_running and not self.game.get_player_stats('lock_in_progress'):
                #end tracking
                self.multiball_running=False
                self.game.set_player_stats('quick_multiball_running',self.multiball_running)

                #self.game.sound.stop_music()
                #self.game.sound.play_music('general_play', loops=-1)

                self.timeout()

        def jackpot_explode(self):
            anim = dmd.Animation().load(game_path+"dmd/exploding_wall.dmd")
            animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=6)
            if self.jackpot_count<5:
                animation_layer.add_frame_listener(-1,self.jackpot)
            else:
                animation_layer.add_frame_listener(-1,self.treasure_bonus)
            self.layer = animation_layer
            self.game.sound.play("explosion")

        def jackpot(self):
            bgnd = dmd.Animation().load(game_path+"dmd/qm_jackpot_bgnd.dmd")
            bgnd_layer = dmd.FrameLayer(frame=bgnd.frames[0])

            treasure_graphic = ['ioti','dos','ron','coc','fot']
            treasure_x = [98,99,101,96,87]
            treasure_y = [5,10,4,10,8]
            info_line1 = ['IDOL OF','DIAMOND OF','REMAINS OF','CROSS OF','FISH OF']
            info_line2 = ['THE INCAS','SHANGHAI','NURHACHI','CORONADO','TAYLES']

            treasure = dmd.Animation().load(game_path+"dmd/treasure_"+treasure_graphic[self.jackpot_count]+".dmd")
            treasure_layer = dmd.FrameLayer(frame=treasure.frames[0])
            treasure_layer.target_x=treasure_x[self.jackpot_count]
            treasure_layer.target_y=treasure_y[self.jackpot_count]
            treasure_layer.composite_op="blacksrc"

            info_layer1 = dmd.TextLayer(43,0, self.game.fonts['8x6'], "center", opaque=False)
            info_layer2 = dmd.TextLayer(43,8, self.game.fonts['8x6'], "center", opaque=False)

            info_layer1.set_text(info_line1[self.jackpot_count])
            info_layer2.set_text(info_line2[self.jackpot_count])

            award_layer = dmd.TextLayer(43,16, self.game.fonts['num_14x10'], "center", opaque=False)
            #calc award
            award = self.jackpot_base_value+self.jackpot_boost_value*self.jackpot_count
            award_layer.set_text(locale.format("%d",award,True),blink_frames=2)

            #set display
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,treasure_layer,info_layer1,info_layer2,award_layer])

            #score points
            self.game.score(award)

            #speech call
            self.game.sound.play_voice("qm_jackpot"+str(self.jackpot_count))

            #inc the counter
            self.jackpot_count+=1

            self.delay(name='reset_display',delay=3,handler=self.multiball)


        def treasure_bonus(self):

            anim = dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd")
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)

            info_layer = dmd.TextLayer(64,5, self.game.fonts['8x6'], "center", opaque=False)
            info_layer.set_text("TREASURE BONUS")

            award_layer = dmd.TextLayer(64,14, self.game.fonts['num_14x10'], "center", opaque=False)
            #calc award
            award = self.jackpot_base_value+self.jackpot_boost_value*self.jackpot_count+self.jackpot_boost_value
            award_layer.set_text(locale.format("%d",award,True),blink_frames=2)

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,info_layer,award_layer])

            #score points
            self.game.score(award)

            #speech call
            self.game.sound.play_voice('excellent')

            #set target
            self.delay(name='reset_display',delay=3,handler=self.multiball)

        def sw_leftEject_active(self, sw):
            if self.multiball_running and not self.game.get_player_stats('multiball_running'): #only do this is the main multiball is not running also
                self.game.screens.add_ball(2,self.add_ball_value)
                self.launch_ball()


        def sw_singleDropTop_active(self, sw):
            self.hit()


        def sw_captiveBallFront_active_for_200ms(self, sw):
            if not self.multiball_running and not self.game.get_player_stats('multiball_running'): #only allow stacking of multiballs if this multiball is started first
                self.multiball()
            elif self.multiball_running:
                self.jackpot_explode()

            return procgame.game.SwitchStop


        def sw_shooterLane_active_for_500ms(self,sw):
            if self.multiball_started:
                self.game.coils.ballLaunch.pulse()

            return procgame.game.SwitchStop