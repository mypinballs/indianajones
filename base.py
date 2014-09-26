# Attract Mode

import procgame
import locale
import logging
import audits
import time

from procgame import *
from random import *
from service import *
from bonus import *
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

from time import strftime



base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


class BaseGameMode(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game):
		super(BaseGameMode, self).__init__(game, 2)

                self.log = logging.getLogger('ij.base')

		self.layer = None # Presently used for tilt layer

                #register music files
                self.game.sound.register_music('general_play', music_path+"general_play.aiff")
                #register speech call files
                self.game.sound.register_sound('dont_touch_anything', speech_path+"dont_touch_anything.aiff")

                self.game.sound.register_sound('slingshot', sound_path+"sling_1.aiff")
                self.game.sound.register_sound('slingshot', sound_path+"sling_2.aiff")
                self.game.sound.register_sound('slingshot', sound_path+"sling_3.aiff")
                self.game.sound.register_sound('slingshot', sound_path+"sling_4.aiff")

                self.game.sound.register_sound('inlane', sound_path+"inlane.aiff")
                self.game.sound.register_sound('gun_shot', sound_path+"gun_shot_deep.aiff")
                self.game.sound.register_sound('outlane_sound', sound_path+"outlane.aiff")
                self.game.sound.register_sound('electricity', sound_path+"electricity.aiff")
                self.game.sound.register_sound('extra_ball_collected', sound_path+"extra_ball_lit_ff.aiff")
                self.game.sound.register_sound('extra_ball_lit', sound_path+"extra_ball_lit_ff.aiff")

                self.game.sound.register_sound('outlane_speech', speech_path+"goodbye.aiff")
                self.game.sound.register_sound('outlane_speech', speech_path+"argh.aiff")
                self.game.sound.register_sound('outlane_speech', speech_path+"why_snakes.aiff")
                self.game.sound.register_sound('outlane_speech', speech_path+"blank.aiff")
                self.game.sound.register_sound('extra_ball_speech', speech_path+"extra_ball.aiff")

                #setup flags
                self.ball_starting = True
                self.ball_served= False
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
		self.game.tilt.reset()

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

            #medium priority basic modes
            self.totem = Totem(self.game, 51)
            self.plane_chase = Plane_Chase(self.game, 52)
            self.skillshot = Skillshot(self.game, 54)

            #higher priority basic modes
            self.mode_select = Mode_Select(self.game, 60)
            self.multiball = Multiball(self.game, 61)
            self.poa = POA(self.game, 95)

            #modes with links to other modes
            self.indy_lanes = Indy_Lanes(self.game, 42, self.mode_select)
            self.loops = Loops(self.game, 43, self.indy_lanes)


            #start modes
            self.game.modes.add(self.pops)
            self.game.modes.add(self.narrow_escape)
            self.game.modes.add(self.indy_lanes)
            self.game.modes.add(self.loops)
            self.game.modes.add(self.totem)
            self.game.modes.add(self.plane_chase)
            self.game.modes.add(self.mode_select)
            self.game.modes.add(self.multiball)
            self.game.modes.add(self.poa)

            #set idol - should be here already?
            #if self.game.ball==1:
                #self.game.idol.home()


        def ball_save_callback(self):
            anim = dmd.Animation().load(game_path+"dmd/eternal_life.dmd")
            self.layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=3)
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
                self.game.modes.remove(self.totem)
                self.game.modes.remove(self.plane_chase)
                self.game.modes.remove(self.mode_select)
                self.game.modes.remove(self.multiball)
                self.game.modes.remove(self.poa)

	def ball_drained_callback(self):
                # temp addition of ball_served flag checking to try and resolve trough ball launch bounce in
		if self.game.trough.num_balls_in_play == 0 and self.ball_served:
                    # End the ball
                    self.finish_ball()

	def finish_ball(self):

                #music fadeout
                self.game.sound.fadeout_music()

                # Create the bonus mode so bonus can be calculated.
		self.bonus = Bonus(self.game, 98)
		self.game.modes.add(self.bonus)

		# Only compute bonus if it wasn't tilted away. 23/02/2011
		if not self.game.tilt.get_status():
                    self.bonus.calculate(self.end_ball)
		else:
                    self.end_ball()
                    self.layer = None


	def end_ball(self):
                #remove bonus mode
                self.game.modes.remove(self.bonus)

                #reset ball served flag
                self.ball_served=False

		# Tell the game object it can process the end of ball
		# (to end player's turn or shoot again)
		self.game.end_ball()


	def sw_startButton_active(self, sw):
		if self.game.ball == 1 and len(self.game.players)<self.game.max_players:
			p = self.game.add_player()
			self.log.info(p.name + " added!")

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

        def sw_shooterLane_active_for_150ms(self,sw):
            self.ball_served = True

        def sw_shooterLane_active_for_500ms(self,sw):
            if self.ball_saved:
                self.game.coils.ballLaunch.pulse()
                self.ball_saved = False

	# Note: Game specific item
	# Set the switch name to the launch button on your game.
	# If manual plunger, remove the whole section.
	def sw_gunTrigger_active(self, sw):
		if self.game.switches.shooterLane.is_active():
			self.game.coils.ballLaunch.pulse()
                        self.game.coils.flasherRightSide.schedule(0x00003333, cycle_seconds=2, now=True)
                        self.game.sound.play("gun_shot")
                if self.game.switches.flipperLwL.is_active() and self.ball_starting:
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
            self.game.set_player_stats('slingshot_hits',self.game.get_player_stats('slingshot_hits')+1)

        def inlane(self):
            self.game.score(100000)
            self.game.sound.play("inlane")

        def outlane(self):
            self.game.score(200000)

            if not self.game.ball_save.is_active() and not self.game.get_player_stats("multiball_started") and not self.game.get_player_stats("quick_multiball_started") and not self.game.get_player_stats('multiball_mode_started'):
                self.game.sound.play("outlane_sound")
                self.game.sound.play("outlane_speech")


        #pause game logic
        def sw_buyInButton_active_for_250ms(self,sw): 
             if self.game.ball>0: 
                if self.game.switches.flipperLwR.is_active(0.5) and not self.game.paused:
                    self.game.utility.pause_game(True)
                elif self.game.paused:
                    self.game.utility.pause_game(False)
            
