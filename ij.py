import sys
sys.path.append(sys.path[0]+'/../..') # Set the path so we can find procgame.  We are assuming (stupidly?) that the first member is our directory.
import procgame
import pinproc
from layers import *
from idol import *
from mini_playfield import *
from effects import *
from extra_ball import *
from info import *
from bonus import *
from tilt import *
from match import *
from pops import *
from narrow_escape import *
from loops import *
from poa import *
from hand_of_fate import *
from totem import *
from ij_modes import *
from indy_lanes import *
from plane_chase import *
from mode_select import *
from skillshot import *
from multiball import *
from procgame import *
from threading import Thread
from random import *
from time import strftime
import string
import time
import locale
import math
import copy
import yaml
import random
import logging


logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

#os.chdir("/Users/jim/Documents/Pinball/p-roc/p-roc system/src/pyprocgame/")

game_locale = config.value_for_key_path('std_locale')
locale.setlocale(locale.LC_ALL, game_locale) # en_GB Used to put commas in the score.

#base_path = "/Users/jim/Documents/Pinball/p-roc/p-roc system/src/"
base_path = config.value_for_key_path('base_path')
logging.info("Base Path is: "+base_path)

game_path = base_path+"games/indyjones/"
fonts_path = base_path+"shared/dmd/"
shared_sound_path = base_path+"shared/sound/"

machine_config_path = game_path + "config/machine.yaml"
settings_path = game_path +"config/settings.yaml"
game_data_path = game_path +"config/game_data.yaml"
game_data_template_path = game_path +"config/game_data_template.yaml"
settings_template_path = game_path +"config/settings_template.yaml"

voice_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"
font_tiny7 = dmd.Font(fonts_path+"04B-03-7px.dmd")
font_jazz18 = dmd.Font(fonts_path+"Jazz18-18px.dmd")
font_14x10 = dmd.Font(fonts_path+"Font14x10.dmd")
font_18x12 = dmd.Font(fonts_path+"Font18x12.dmd")
font_07x4 = dmd.Font(fonts_path+"Font07x4.dmd")
font_07x5 = dmd.Font(fonts_path+"Font07x5.dmd")
font_09Bx7 = dmd.Font(fonts_path+"Font09Bx7.dmd")
font_6x6_bold = dmd.Font(fonts_path+"Font_6x6_bold.dmd")

#lampshow_files = [game_path +"lamps/attract_show_test.lampshow"]
lampshow_files = [game_path +"lamps/general/colours.lampshow", \
                  game_path +"lamps/general/updown.lampshow", \
                  game_path +"lamps/general/downup.lampshow", \
                  game_path +"lamps/general/leftright.lampshow", \
                  game_path +"lamps/general/rightleft.lampshow", \
                  game_path +"lamps/general/quickwindmills.lampshow", \
                  game_path +"lamps/general/windmills.lampshow", \
                  game_path +"lamps/general/rollleft.lampshow", \
                  game_path +"lamps/general/rollright.lampshow"]

class Attract(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game):
		super(Attract, self).__init__(game, 1)
                self.log = logging.getLogger('ij.attract')
                self.display_order = [0,1,2,3,4,5,6,7,8,9]
		self.display_index = 0
		self.game.sound.register_sound('burp', voice_path+'burp.wav')
 
	def mode_topmost(self):
		pass

	def mode_started(self):

		# Blink the start button to notify player about starting a game.
		self.game.lamps.startButton.schedule(schedule=0x00ff00ff, cycle_seconds=0, now=False)

                # Turn on GI lamps
		self.delay(name='stuck_balls', event_type=None, delay=0, handler=self.gi)

                self.log.info("attract mode after gi turn on")

                # run feature lamp patterns
                self.change_lampshow()

                #debug subway release issues
                self.game.coils.subwayRelease.pulse(100)

                #check for stuck balls
                #self.release_stuck_balls()
                self.delay(name='stuck_balls', event_type=None, delay=2, handler=self.release_stuck_balls)

                #empty idol if trough not full
                if not self.game.trough.is_full():
                    self.game.idol.empty()

                print("Trough is full:" +str(self.game.trough.is_full()))
                #reset mini playfield code

                #create dmd attract screens
                self.mypinballs_logo = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/mypinballs_logo.dmd').frames[0])
                #self.mypinballs_logo.transition = dmd.CrossFadeTransition(width=128,height=32)
                self.mypinballs_logo.transition = dmd.ExpandTransition(direction='horizontal')

                #self.williams_logo = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/williams_animated.dmd').frames[0])
                self.williams_logo = dmd.AnimatedLayer(frames=dmd.Animation().load(game_path+'dmd/williams_animated.dmd').frames,frame_time=1,hold=True)
                #self.williams_logo.transition = dmd.ExpandTransition(direction='vertical')

                self.indy_logo = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/indy_logo.dmd').frames[0])
                self.indy_logo.transition = dmd.ExpandTransition(direction='vertical')

                self.press_start = dmd.TextLayer(128/2, 18, font_09Bx7, "center", opaque=True).set_text("PRESS START")
                #self.press_start.transition = dmd.PushTransition(direction='north')

                self.free_play = dmd.TextLayer(128/2, 6, font_09Bx7, "center", opaque=False).set_text("FREE PLAY")
                #self.free_play.transition = dmd.PushTransition(direction='south')

                self.coins_layer = dmd.GroupedLayer(128, 32, [self.free_play, self.press_start])
                #self.coins_layer.transition = dmd.PushTransition(direction='south')

                self.game_over_layer = dmd.TextLayer(128/2, 10, font_09Bx7, "center", opaque=True).set_text("GAME OVER")
                self.game_over_layer.transition = dmd.CrossFadeTransition(width=128,height=32)

                self.scores_layer = dmd.TextLayer(128/2, 11, font_09Bx7, "center", opaque=True).set_text("HIGH SCORES")
		self.scores_layer.transition = dmd.PushTransition(direction='west')

                #setup date & time info
                self.day_layer = dmd.DateLayer(128/2, 5, font_tiny7,"day", "center", opaque=False)
                self.date_layer = dmd.DateLayer(128/2, 13, font_tiny7,"date", "center", opaque=False)
                self.time_layer = dmd.DateLayer(128/2, 21, font_tiny7,"time", "center", opaque=False)
                self.date_time_layer = dmd.GroupedLayer(128, 32, [self.day_layer,self.date_layer,self.time_layer])
        

                self.date_time_layer.transition = dmd.PushTransition(direction='west')

                #run attract dmd screens
                self.attract_display()

        def gi(self):
            self.game.lamps.gi01.pulse(0)
            self.game.lamps.gi02.pulse(0)
            self.game.lamps.gi03.pulse(0)
            self.game.lamps.gi04.pulse(0)

        def gi_off(self):
            self.game.lamps.gi01.disable()
            self.game.lamps.gi02.disable()
            self.game.lamps.gi03.disable()
            self.game.lamps.gi04.disable()

        def release_stuck_balls(self):
            #Release Stuck Balls code
            if self.game.switches.leftEject.is_active():
               self.game.coils.leftEject.pulse(15)

            #popper
            if self.game.switches.rightPopper.is_active():
                self.game.coils.ballPopper.pulse(50)

            #subway
            if self.game.switches.subwayLockup.is_active():
                self.game.coils.subwayRelease.pulse(30)

            #reset drops
            if self.game.switches.dropTargetLeft.is_active() or self.game.switches.dropTargetMiddle.is_active() or self.game.switches.dropTargetRight.is_active():
                self.game.coils.centerDropBank.pulse(100)

            if self.game.switches.singleDropTop.is_active():
                self.game.coils.totemDropUp.pulse()

            #check shooter lane
            if self.game.switches.shooterLane.is_active():
                self.game.coils.ballLaunch.pulse()

            if self.game.switches.topPost.is_active():
                self.game.coils.topLockupMain.pulse()
                self.game.coils.topLockupHold.pulse(200)


        def change_lampshow(self):
		shuffle(self.game.lampshow_keys)
                
                #turn gi on or off depending on lampshow chosen from shuffle
                if self.game.lampshow_keys[0].find('flasher',0)>0:
                    self.gi_off()
                else:
                    self.gi()

		self.game.lampctrl.play_show(self.game.lampshow_keys[0], repeat=True)
		self.delay(name='lampshow', event_type=None, delay=10, handler=self.change_lampshow)


        def attract_display(self):
                script = list()
      
                script.append({'seconds':5.0, 'layer':self.mypinballs_logo})
                script.append({'seconds':7.0, 'layer':self.williams_logo})
                script.append({'seconds':3.0, 'layer':self.indy_logo})
		script.append({'seconds':3.0, 'layer':self.coins_layer})
		#script.append({'seconds':20.0, 'layer':self.credits_layer})
		script.append({'seconds':3.0, 'layer':None})

                script.append({'seconds':3.0, 'layer':self.scores_layer})
		for frame in highscore.generate_highscore_frames(self.game.highscore_categories):
                    new_layer = dmd.FrameLayer(frame=frame)
                    new_layer.transition = dmd.PushTransition(direction='west')
                    script.append({'seconds':2.0, 'layer':new_layer})

                if self.game.user_settings['Machine (Standard)']['Show Date and Time'].startswith('Y'):
                    script.append({'seconds':10.0, 'layer':self.date_time_layer})

                #add in the game over screen
                index=3
                time=3
                if self.game.system_status=='game_over':
                    index=0
                    time=10
                    self.game.system_status='attract'

                script.insert(index,{'seconds':time, 'layer':self.game_over_layer})

		self.layer = dmd.ScriptedLayer(width=128, height=32, script=script)
                #self.layer = dmd.ScriptedLayer(128, 32, [{'seconds':10.0, 'layer':self.mypinballs_logo}, {'seconds':2.0, 'layer':self.press_start}, {'seconds':2.0, 'layer':None}])
                #self.game.set_status("V1.0")

            

	def mode_stopped(self):
		self.game.lampctrl.stop_show()

	def mode_tick(self):
		pass


	# Enter service mode when the enter button is pushed.
	def sw_enter_active(self, sw):
		for lamp in self.game.lamps:
			lamp.disable()
		self.game.modes.add(self.game.service_mode)
		return True

	def sw_exit_active(self, sw):
		return True

	# Outside of the service mode, up/down control audio volume.
	def sw_down_active(self, sw):
		volume = self.game.sound.volume_down()
		self.game.set_status("Volume Down : " + str(volume))
		return True

	def sw_up_active(self, sw):
		volume = self.game.sound.volume_up()
		self.game.set_status("Volume Up : " + str(volume))
		return True

	# Start button starts a game if the trough is full.  Otherwise it
	# initiates a ball search.
	# This is probably a good place to add logic to detect completely lost balls.
	# Perhaps if the trough isn't full after a few ball search attempts, it logs a ball
	# as lost?
	def sw_startButton_active(self, sw):
		if self.game.trough.is_full:
			# Remove attract mode from mode queue - Necessary?
			self.game.modes.remove(self)
			# Initialize game
			self.game.start_game()
			# Add the first player
			self.game.add_player()
			# Start the ball.  This includes ejecting a ball from the trough.
			self.game.start_ball()
		else:

			self.game.set_status("Ball Search!")
			self.game.ball_search.perform_search(5)
		return True


class BaseGameMode(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game):
		super(BaseGameMode, self).__init__(game, 2)
		self.tilt_layer = dmd.TextLayer(128/2, 7, font_jazz18, "center").set_text("TILT!")
		self.layer = None # Presently used for tilt layer
		self.ball_starting = True

                #register music files
                self.game.sound.register_music('general_play', music_path+"general_play.aiff")
                #register speech call files
                self.game.sound.register_sound('dont_touch_anything', speech_path+"dont_touch_anything.aiff")

                self.game.sound.register_sound('slingshot', sound_path+"sling_1.aiff")
                self.game.sound.register_sound('slingshot', sound_path+"sling_2.aiff")
                self.game.sound.register_sound('slingshot', sound_path+"sling_3.aiff")
                self.game.sound.register_sound('slingshot', sound_path+"sling_4.aiff")

                self.game.sound.register_sound('inlane', sound_path+"inlane.aiff")
                self.game.sound.register_sound('gun_shot', sound_path+"gun_shot.aiff")
                self.game.sound.register_sound('outlane_sound', sound_path+"outlane.aiff")
                self.game.sound.register_sound('electricity', sound_path+"electricity.aiff")
                self.game.sound.register_sound('extra_ball_collected', sound_path+"extra_ball_lit_ff.aiff")
                self.game.sound.register_sound('extra_ball_lit', sound_path+"extra_ball_lit_ff.aiff")

                self.game.sound.register_sound('outlane_speech', speech_path+"goodbye.aiff")
                self.game.sound.register_sound('outlane_speech', speech_path+"argh.aiff")
                self.game.sound.register_sound('outlane_speech', speech_path+"blank.aiff")
                self.game.sound.register_sound('outlane_speech', speech_path+"blank.aiff")
                self.game.sound.register_sound('extra_ball_speech', speech_path+"extra_ball.aiff")

                self.ball_saved = False


	def mode_started(self):

                #debug
                print("Basic Game Mode Started, Ball "+str(self.game.ball))
                #set player status
                self.game.set_player_stats('status','general')
                
		#Disable any previously active lamp
		for lamp in self.game.lamps:
			lamp.disable()
                        
                #Update lamp status's for all modes
                self.game.update_lamps()

		# Turn on the GIs
		# Some games don't have controllable GI's (ie Stern games)
		self.game.lamps.gi01.pulse(0)
		self.game.lamps.gi02.pulse(0)
		self.game.lamps.gi03.pulse(0)
		self.game.lamps.gi04.pulse(0)

		# Enable the flippers
                #print "Game Config: "+str(self.game.config)
		self.game.enable_flippers(True)

                # Each time this mode is added to game Q, set this flag true.
		self.ball_starting = True

                #setup basic modes
                self.add_basic_modes(self);

		# Put the ball into play and start tracking it.
		self.game.trough.launch_balls(1, self.ball_launch_callback)

                # Enable ball search in case a ball gets stuck during gameplay.
		self.game.ball_search.enable()

		# Reset tilt warnings and status
		self.times_warned = 0;
		self.tilt_status = 0

		# In case a higher priority mode doesn't install it's own ball_drained
		# handler.
		self.game.trough.drain_callback = self.ball_drained_callback

		

                #ball save callback - exp
                self.game.ball_save.callback = self.ball_save_callback

                #reset drop targets
                self.game.coils.centerDropBank.pulse(100)

        def add_basic_modes(self,ball_in_play):

           
        #if self.game.ball==1:
            #lower priority basic modes
            self.pops = Pops(self.game, 40)
            self.narrow_escape = Narrow_Escape(self.game, 41)
            self.indy_lanes = Indy_Lanes(self.game, 42)
            self.loops = Loops(self.game, 43)

            #medium priority basic modes
            self.poa = POA(self.game, 50)
            self.totem = Totem(self.game, 51)
            self.plane_chase = Plane_Chase(self.game, 52)
            self.skillshot = Skillshot(self.game, 54)

            #higher priority basic modes
            self.mode_select = Mode_Select(self.game, 60)
            self.multiball = Multiball(self.game, 61)

            #start modes
            self.game.modes.add(self.pops)
            self.game.modes.add(self.narrow_escape)
            self.game.modes.add(self.indy_lanes)
            self.game.modes.add(self.loops)
            self.game.modes.add(self.poa)
            self.game.modes.add(self.totem)
            self.game.modes.add(self.plane_chase)
            self.game.modes.add(self.mode_select)
            self.game.modes.add(self.multiball)

            #set idol - should be here already?
            if self.game.ball==1:
                self.game.idol.home()


        def ball_save_callback(self):
            anim = dmd.Animation().load(game_path+"dmd/eternal_life.dmd")
            self.layer = dmd.AnimatedLayer(frames=anim.frames,hold=False)
            self.game.sound.play_voice('dont_touch_anything')
            #self.game.sound.play('electricity')

            self.ball_saved = True


	def ball_launch_callback(self):
            #print("Debug - Ball Starting var is:"+str(self.ball_starting))
            if self.ball_starting:
                #print("Debug - Starting Ball Save Lamp")
                #self.game.ball_save.start_lamp()
                #start background music
                #print("Debug - Starting General Play Music")
                self.game.sound.play_music('general_play', loops=-1)

        def mode_tick(self):
            if self.game.switches.startButton.is_active(1) and self.game.switches.flipperLwL.is_active(1) and self.game.switches.flipperLwR.is_active():
                print("reset button code entered")
                self.game.sound.stop_music()
                self.game.end_run_loop()

		while len(self.game.dmd.frame_handlers) > 0:
                    del self.game.dmd.frame_handlers[0]
                    
		del self.game.proc

	def mode_stopped(self):

                print("Basic Game Mode Ended, Ball "+str(self.game.ball))

		# Ensure flippers are disabled
		self.game.enable_flippers(enable=False)

		# Deactivate the ball search logic so it won't search due to no
		# switches being hit.
		self.game.ball_search.disable()

            #if self.game.ball==0:
                self.game.modes.remove(self.pops)
                self.game.modes.remove(self.narrow_escape)
                self.game.modes.remove(self.indy_lanes)
                self.game.modes.remove(self.loops)
                self.game.modes.remove(self.poa)
                self.game.modes.remove(self.totem)
                self.game.modes.remove(self.plane_chase)
                self.game.modes.remove(self.mode_select)
                self.game.modes.remove(self.multiball)

	def ball_drained_callback(self):
		if self.game.trough.num_balls_in_play == 0:
                    # End the ball
                    self.finish_ball()

	def finish_ball(self):

                #music fadeout
                self.game.sound.fadeout_music()

                # Create the bonus mode so bonus can be calculated.
		self.bonus = Bonus(self.game, 98)
		self.game.modes.add(self.bonus)

		# Only compute bonus if it wasn't tilted away. 23/02/2011
		if not self.tilt_status:
                    self.bonus.calculate(self.end_ball)
		else:
                    self.end_ball()


		# Turn off tilt display (if it was on) now that the ball has drained.
		if self.tilt_status and self.layer == self.tilt_layer:
                    self.layer = None

		#self.end_ball()

	def end_ball(self):
                #remove bonus mode
                self.game.modes.remove(self.bonus)
                
		# Tell the game object it can process the end of ball
		# (to end player's turn or shoot again)
		self.game.end_ball()

                
	def sw_startButton_active(self, sw):
		if self.game.ball == 1 and len(self.game.players)<self.game.max_players:
			p = self.game.add_player()
			self.game.set_status(p.name + " added!")

        def sw_startButton_active_for_2s(self, sw):
		if self.game.ball > 1 and self.game.user_settings['Machine (Standard)']['Game Restart']:
			self.game.set_status("Reset!")

			# Need to build a mechanism to reset AND restart the game.  If one ball
			# is already in play, the game can restart without plunging another ball.
			# It would skip the skill shot too (if one exists).

			# Currently just reset the game.  This forces the ball(s) to drain and
			# the game goes to AttractMode.  This makes it painfully slow to restart,
			# but it's better than nothing.
			self.game.reset()
			return True

	def sw_shooterLane_open_for_1s(self,sw):
		if self.ball_starting:
			self.ball_starting = False
			ball_save_time = 10
			self.game.ball_save.start(num_balls_to_save=1, time=ball_save_time, now=True, allow_multiple_saves=False)
		#else:
		#	self.game.ball_save.disable()

        def sw_shooterLane_active_for_500ms(self,sw):
            if self.ball_saved:
                self.game.coils.ballLaunch.pulse(50)
                self.ball_saved = False

	# Note: Game specific item
	# Set the switch name to the launch button on your game.
	# If manual plunger, remove the whole section.
	def sw_gunTrigger_active(self, sw):
		if self.game.switches.shooterLane.is_active():
			self.game.coils.ballLaunch.pulse(50)
                        self.game.coils.flasherRightSide.schedule(0x00003333, cycle_seconds=1.5, now=True)
                        self.game.sound.play("gun_shot")
                if self.game.switches.flipperLwL.is_active():
                        self.game.modes.add(self.skillshot)

        #skillshot preview
        def sw_flipperLwL_active_for_500ms(self, sw):
            if self.ball_starting and self.game.switches.shooterLane.is_active():
                self.skillshot.activate_lamps()

        #skillshot preview
        def sw_flipperLwL_inactive(self, sw):
            if self.ball_starting and self.game.switches.shooterLane.is_active():
                self.skillshot.clear_lamps()


	# Allow service mode to be entered during a game.
	def sw_enter_active(self, sw):
		self.game.modes.add(self.game.service_mode)
		return True

	def sw_tilt_active(self, sw):
		if self.times_warned == self.game.user_settings['Machine (Standard)']['Tilt Warnings']:
			self.tilt()
		else:
			self.times_warned += 1
			#play sound
			#add a display layer and add a delayed removal of it.
			self.game.set_status("Tilt Warning " + str(self.times_warned) + "!")

	def tilt(self):
		# Process tilt.
		# First check to make sure tilt hasn't already been processed once.
		# No need to do this stuff again if for some reason tilt already occurred.
		if self.tilt_status == 0:

			# Display the tilt graphic
			self.layer = self.tilt_layer

			# Disable flippers so the ball will drain.
			self.game.enable_flippers(enable=False)

			# Make sure ball won't be saved when it drains.
			self.game.ball_save.disable()
			#self.game.modes.remove(self.ball_save)

			# Make sure the ball search won't run while ball is draining.
			self.game.ball_search.disable()

			# Ensure all lamps are off.
			for lamp in self.game.lamps:
				lamp.disable()

			# Kick balls out of places it could be stuck.
			if self.game.switches.shooterLane.is_active():
				self.game.coils.ballLaunch.pulse(50)
			if self.game.switches.leftEject.is_active():
				self.game.coils.leftEject.pulse(20)
			self.tilt_status = 1
			#play sound
			#play video

       
                        
        def sw_leftSlingshot_active(self,sw):
            self.sling()

        def sw_rightSlingshot_active(self,sw):
            self.sling()

        def sw_leftInlane_active(self,sw):
            self.inlane()

        def sw_rightInlane_active(self,sw):
            self.inlane()

        def sw_rightOutlaneBottom_active(self,sw):
            self.outlane()
            
        def sw_leftOutlane_active(self,sw):
            self.outlane()

        def sling(self):
            self.game.score(110)
            self.game.sound.play('slingshot')

        def inlane(self):
            self.game.score(100000)
            self.game.sound.play("inlane")

        def outlane(self):
            self.game.score(200000)
            self.game.sound.play("outlane_sound")
            self.game.sound.play("outlane_speech")





class Game(game.BasicGame):
	"""docstring for Game"""
	def __init__(self, machine_type):
		super(Game, self).__init__(machine_type)
		self.sound = procgame.sound.SoundController(self)
		self.lampctrl = procgame.lamps.LampController(self)
		self.settings = {}

	def save_settings(self):
		#self.write_settings(settings_path)
                super(Game, self).save_settings(settings_path)
		#pass

        def save_game_data(self):
		super(Game, self).save_game_data(game_data_path)

        def create_player(self, name):
		return mpcPlayer(name)
                

	def setup(self):
		"""docstring for setup"""
		self.load_config(self.yamlpath)

                self.load_settings(settings_template_path, settings_path)
		self.sound.music_volume_offset = self.user_settings['Sound']['Music volume offset']
		self.sound.set_volume(self.user_settings['Sound']['Initial volume'])
		self.load_game_data(game_data_template_path, game_data_path)

                #define system status var
                self.system_status='power_up'

#		print "Stats:"
#		print self.game_data
#		print "Settings:"
#		print self.settings

		print("Initial switch states:")
		for sw in self.switches:
			print("  %s:\t%s" % (sw.name, sw.state_str()))

                self.balls_per_game = self.user_settings['Machine (Standard)']['Balls Per Game']
		self.setup_ball_search()
                self.score_display.set_left_players_justify(self.user_settings['Display']['Left side score justify'])


		# Note - Game specific item:
		# The last parameter should be the name of the game's ball save lamp
		self.ball_save = procgame.modes.BallSave(self, self.coils.flasherEternalLife, 'shooterLane')

		trough_switchnames = []
		# Note - Game specific item:
		# This range should include the number of trough switches for
		# the specific game being run.  In range(1,x), x = last number + 1.
		for i in range(1,7):
			trough_switchnames.append('trough' + str(i))
		early_save_switchnames = ['rightOutlaneTop', 'leftOutlane']

		# Note - Game specific item:
		# Here, trough6 is used for the 'eject_switchname'.  This must
		# be the switch of the next ball to be ejected.  Some games
		# number the trough switches in the opposite order; so trough1
		# might be the proper switchname to user here.
		self.trough = procgame.modes.Trough(self,trough_switchnames,'trough6','trough', early_save_switchnames, 'shooterLane', self.drain_callback)

		# Link ball_save to trough
		self.trough.ball_save_callback = self.ball_save.launch_callback
		self.trough.num_balls_to_save = self.ball_save.get_num_balls_to_save
		self.ball_save.trough_enable_ball_save = self.trough.enable_ball_save

		# Setup and instantiate service mode
		self.sound.register_sound('service_enter', sound_path+"menu_in.wav")
		self.sound.register_sound('service_exit', sound_path+"menu_out.wav")
		self.sound.register_sound('service_next', sound_path+"next_item.wav")
		self.sound.register_sound('service_previous', sound_path+"previous_item.wav")
		self.sound.register_sound('service_switch_edge', sound_path+"switch_edge.wav")
		self.sound.register_sound('service_save', sound_path+"save.wav")
		self.sound.register_sound('service_cancel', sound_path+"cancel.wav")
		self.service_mode = procgame.service.ServiceMode(self,100,font_tiny7,[])

		# Setup fonts
		self.fonts = {}
		self.fonts['tiny7'] = font_tiny7
		self.fonts['jazz18'] = font_jazz18
        	self.fonts['18x12'] = font_18x12
 		self.fonts['07x5'] = font_07x5
                self.fonts['num_14x10'] = font_14x10
		self.fonts['num_07x4'] = font_07x4
                self.fonts['num_09Bx7'] = font_09Bx7
                self.fonts['6x6_bold'] = font_6x6_bold

                #setup paths
                self.paths = {}
                self.paths['game'] = game_path
                self.paths['sound'] = sound_path
                self.paths['speech'] = voice_path
                self.paths['music'] = music_path


                # Register lampshow files for attact
		self.lampshow_keys = []
		key_ctr = 0
		for file in lampshow_files:
                    if file.find('flasher',0)>0:
                        key = 'attract_flashers_' + str(key_ctr)
                    else:
                        key = 'attract_lamps_' + str(key_ctr)
                    self.lampshow_keys.append(key)
                    self.lampctrl.register_show(key, file)
                    key_ctr += 1

                #register game play lamp show
                self.lampctrl.register_show('success', game_path +"lamps/game/success.lampshow")
                self.lampctrl.register_show('ball_lock', game_path +"lamps/game/ball_lock.lampshow")
                self.lampctrl.register_show('hit', game_path +"lamps/game/success.lampshow")
                self.lampctrl.register_show('jackpot', game_path +"lamps/game/success.lampshow")

                # Setup High Scores
		self.highscore_categories = []
		
		cat = highscore.HighScoreCategory()
                cat.game_data_key = 'ClassicHighScoreData'
		self.highscore_categories.append(cat)

                for category in self.highscore_categories:
			category.load_from_game(self)


                #Setup Date & Time Display
                self.show_date_time = self.user_settings['Machine (Standard)']['Show Date and Time']

                #Maximum Players
                self.max_players = 4;

                #add basic modes
                #------------------
                #attract mode
		self.attract_mode = Attract(self)
                #basic game control mode
		self.base_game_mode = BaseGameMode(self)
                #effects mode
                self.effects = Effects(self)
                #extra ball mode
                self.extra_ball = Extra_Ball(self)
                #match mode
                self.match = Match(self,10)
                #add idol mode for idol logic and control
                self.idol = Idol(self,15)
                #setup mini_playfield
                self.mini_playfield = Mini_Playfield(self,16)
                #------------------

		# Instead of resetting everything here as well as when a user
		# initiated reset occurs, do everything in self.reset() and call it
		# now and during a user initiated reset.
		self.reset()

        def set_player_stats(self,id,value):
            p = self.current_player()
            p.player_stats[id]=value

        def get_player_stats(self,id):
            p = self.current_player()
            return p.player_stats[id]

	def reset(self):
		# Reset the entire game framework
		super(Game, self).reset()

		# Add the basic modes to the mode queue
		self.modes.add(self.attract_mode)
		self.modes.add(self.ball_search)
                self.modes.add(self.effects)
		self.modes.add(self.ball_save)
                self.modes.add(self.idol)
                self.modes.add(self.mini_playfield)
		self.modes.add(self.trough)
                self.modes.add(self.extra_ball)
                
    

		# Make sure flippers are off, especially for user initiated resets.
		self.enable_flippers(enable=False)



	# Empty callback just incase a ball drains into the trough before another
	# drain_callback can be installed by a gameplay mode.
	def drain_callback(self):
		pass


        def start_game(self):
		super(Game, self).start_game()
		self.game_data['Audits']['Games Started'] += 1
                
	def ball_starting(self):
		super(Game, self).ball_starting()
		self.modes.add(self.base_game_mode)

	def ball_ended(self):
		self.modes.remove(self.base_game_mode)
		super(Game, self).ball_ended()

	def game_ended(self):
		super(Game, self).game_ended()
     
                #for mode in self.modes:
                    #self.modes.remove(mode)

                self.modes.remove(self.base_game_mode)

		#self.set_status("Game Over")
		#self.modes.add(self.attract_mode)

                self.modes.add(self.match)

	def set_status(self, text):
		self.dmd.set_message(text, 3)
		print(text)

	def extra_ball_count(self):
		p = self.current_player()
		p.extra_balls += 1
                

	def setup_ball_search(self):
		# No special handlers in starter game.
		special_handler_modes = []
		self.ball_search = procgame.modes.BallSearch(self, priority=100, \
                                     countdown_time=10, coils=self.ballsearch_coils, \
                                     reset_switches=self.ballsearch_resetSwitches, \
                                     stop_switches=self.ballsearch_stopSwitches, \
                                     special_handler_modes=special_handler_modes)

#       def enable_flippers(self, enable=True):
#		super(Game, self).enable_flippers(enable)
#		#self.flipper_workaround_mode.enable_flippers(enable)

        def drive_lamp(self, lamp_name, style='on'):
		if style == 'slow':
			self.lamps[lamp_name].schedule(schedule=0x00ff00ff, cycle_seconds=0, now=True)
		elif style == 'medium':
			self.lamps[lamp_name].schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
		elif style == 'fast':
			self.lamps[lamp_name].schedule(schedule=0x55555555, cycle_seconds=0, now=True)
                elif style == 'superfast':
			self.lamps[lamp_name].schedule(schedule=0x99999999, cycle_seconds=0, now=True)
		elif style == 'on':
			self.lamps[lamp_name].enable()
		elif style == 'off':
			self.lamps[lamp_name].disable()
                elif style == 'smarton':
			self.lamps[lamp_name].schedule(schedule=0x88888888, cycle_seconds=0, now=True)
                        self.lamps[lamp_name].enable()
                        #self.mode.delay(name='lamp_on', event_type=None, delay=0.5, handler=self.lamps[lamp_name].enable)

class mpcPlayer(game.Player):

	def __init__(self, name):
		super(mpcPlayer, self).__init__(name)

                #create player stats
                self.player_stats = {}

                #set player stats defaults
                self.player_stats['status']=''
                self.player_stats['bonus_x']=1
                self.player_stats['friends_collected']=0
                self.player_stats['loops_completed']=0
                self.player_stats['loops_made']=0
                self.player_stats['loop_value']=1000000 #1M default
                self.player_stats['ramps_made']=0
                self.player_stats['adventure_letters_collected']=0
                self.player_stats['burps_collected']=0
                self.player_stats['current_mode_num']=0
                self.player_stats['mode_enabled']=False
                self.player_stats['mode_running'] = False
                self.player_stats['mode_status_tracking']= [0,0,0,0,0,0,0,0,0,0,0,0]
                self.player_stats['lock_lit'] = False                
                self.player_stats['multiball_running'] = False
                self.player_stats['balls_locked'] = 0
                self.player_stats['pit_value'] = 0
                self.player_stats['indy_lanes_flag']= [False,False,False,False]
                self.player_stats['indy_lanes_letters_spotted'] = 0
                self.player_stats['poa_flag']= [False,False,False,False,False,False,False,False,False]
                self.player_stats['adventure_letters_spotted']=0
                self.player_stats['last_mode_score']=0
                self.player_stats['get_the_idol_score']=0
                self.player_stats['castle_grunwald_score']=0
                self.player_stats['monkey_brains_score']=0




                



def main():

	config = yaml.load(open(machine_config_path, 'r'))
        print("Using config at: %s "%(machine_config_path))
	machine_type = config['PRGame']['machineType']
	config = 0
	game = None
	try:
	 	game = Game(machine_type)
		game.yamlpath = machine_config_path
		game.setup()
		game.run_loop()
                
	finally:
		del game


if __name__ == '__main__': main()
