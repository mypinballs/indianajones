import sys
sys.path.append(sys.path[0]+'/../..') # Set the path so we can find procgame.  We are assuming (stupidly?) that the first member is our directory.
import procgame
import pinproc
import string
import time
import datetime
import locale
import math
import copy
import yaml
import random
import os
import logging
import audits
import diagnostics
import ep

from procgame import *
from threading import Thread

from scoredisplay import *
from player import *
from idol import *
from mini_playfield import *
from moonlight import *
from trough import *
from effects import *
from extra_ball import *
from screens import *
from mpcballsearch import *
from service import *
from utility import *
from tilt import *

from attract import *
from base import *
from match import *

from random import *
from time import strftime

serial = config.value_for_key_path('game_serial')

game_locale = config.value_for_key_path('std_locale')
locale.setlocale(locale.LC_ALL, game_locale) # en_GB Used to put commas in the score.

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
displayed_audits_path = game_path +"config/audits_display.yaml"
dots_path = game_path + "dots/"
images_path = game_path + "images/"

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
font_6x6_bold = dmd.Font(fonts_path+"font_6x6_bold.dmd")
font_23x12 = dmd.font_named("font_23x12_bold.dmd")
font_8x6_bold = dmd.font_named("font_8x6_bold.dmd")

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




class Game(game.BasicGame):
	"""docstring for Game"""
	def __init__(self, machine_type):
		super(Game, self).__init__(machine_type)

                self.log = logging.getLogger('ij.game')
		self.sound = procgame.sound.SoundController(self)
		self.lampctrl = procgame.lamps.LampController(self)
		self.settings = {}

                #set the dmd colour map - level 1 is mask and set to 0
                #dmd_map = [0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                dmd_map = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4, 5, 11, 12, 13, 14, 15]
                self.proc.set_dmd_color_mapping(dmd_map)

                use_desktop = config.value_for_key_path(keypath='use_desktop', default=True)
                self.color_desktop = config.value_for_key_path(keypath='colour_desktop', default=False)
                if use_desktop:
                    # if not color, run the old style pygame
                    if not self.color_desktop:
                        self.log.info("Standard Desktop")
                        from procgame.desktop import Desktop
                        self.desktop = Desktop()
                    # otherwise run the color display
                    else:
                        self.log.info("Color Desktop")
                        from ep import EP_Desktop
                        self.desktop = EP_Desktop()

                #debug
                for coil in self.coils:
                    self.log.debug("Game Config:"+str(coil.name)+" "+str(coil.number))
                for lamp in self.lamps:
                    self.log.debug("Game Config:"+str(lamp.name)+" "+str(lamp.number))


                #setup score display
                self.score_display = ScoreDisplay(self, 0)
                
                #create displayed audits dict
                self.displayed_audits = yaml.load(open(displayed_audits_path, 'r'))
                #load and update audits database
		audits.load(self)

                #setup diagnostics
                self.health_status = ''
                self.switch_error_log =[]
                self.device_error_log=[]


	def save_settings(self):
		#self.write_settings(settings_path)
                super(Game, self).save_settings(settings_path)
		#pass

        def save_game_data(self):
		super(Game, self).save_game_data(game_data_path)

        def create_player(self, name):
		return Player(name)
                

	def setup(self):
		"""docstring for setup"""
		self.load_config(self.yamlpath)

                self.load_settings(settings_template_path, settings_path)
		self.sound.music_volume_offset = self.user_settings['Sound']['Music volume offset']
		self.sound.set_volume(self.user_settings['Sound']['Initial volume'])
		self.load_game_data(game_data_template_path, game_data_path)

                #define system status var
                self.system_status='power_up'
                self.system_version='0.5.3'
                self.system_name='Indiana Jones 2'.upper()

                #update audit data on boot up time
                audits.record_value(self,'bootUp')

                #set start time game var
                self.start_time = time.time()

#		print "Stats:"
#		print self.game_data
#		print "Settings:"
#		print self.settings

		self.log.info("Initial switch states:")
		for sw in self.switches:
			self.log.info("  %s:\t%s" % (sw.name, sw.state_str()))
                
                #balls per game setup
                self.balls_per_game = self.user_settings['Machine (Standard)']['Balls Per Game']
                
                #moonlight setup
                self.moonlight_minutes = self.user_settings['Gameplay (Feature)']['Moonlight Mins to Midnight']
                self.moonlight_flag = False
                
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
		early_save_switchnames = ['rightOutlaneBottom', 'leftOutlane']

		# Note - Game specific item:
		# Here, trough6 is used for the 'eject_switchname'.  This must
		# be the switch of the next ball to be ejected.  Some games
		# number the trough switches in the opposite order; so trough1
		# might be the proper switchname to user here.

                #setup trough
                self.trough = Trough(game=self,drain_callback=self.drain_callback)
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

                #change this to my own version
                #self.service_mode = procgame.service.ServiceMode(self,100,font_tiny7,[])
                self.service_mode = ServiceMode(self,100,font_07x5,font_8x6_bold,[])

		# Setup fonts
		self.fonts = {}
		#self.fonts['jazz18'] = font_jazz18
        	self.fonts['18x12'] = font_18x12
                self.fonts['num_14x10'] = font_14x10
		self.fonts['num_07x4'] = font_07x4

                self.fonts['tiny7'] = font_tiny7
                self.fonts['6x6_bold'] = font_6x6_bold
                self.fonts['07x5'] = font_07x5
                self.fonts['7x4'] = dmd.font_named("Font07x4.dmd")
                self.fonts['8x6'] = dmd.font_named("font_8x6_bold.dmd")
                self.fonts['num_09Bx7'] = dmd.font_named("Font09Bx7.dmd")
                self.fonts['9x7_bold'] = dmd.font_named("Font09Bx7.dmd")
                self.fonts['10x7_bold'] = dmd.font_named("font_10x7_bold.dmd")
                self.fonts['23x12'] = dmd.font_named("font_23x12_bold.dmd")
                
                self.fonts['5px_az'] = dmd.font_named("Font_3_CactusCanyon.dmd")
                self.fonts['6px_az'] = dmd.font_named("Font_19_CactusCanyon.dmd")
                self.fonts['7px_az'] = dmd.font_named("Font_2_CactusCanyon.dmd")
                self.fonts['7px_bold_az'] = dmd.font_named("Font_14_CactusCanyon.dmd")
                self.fonts['9px_az'] = dmd.font_named("Font_15_CactusCanyon.dmd")
                self.fonts['10px_az'] = dmd.font_named("Font_Custom_10px_AZ.dmd")
                
            
                #setup paths
                self.paths = {}
                self.paths['game'] = game_path
                self.paths['sound'] = sound_path
                self.paths['speech'] = voice_path
                self.paths['music'] = music_path
                self.log.info(self.paths)


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
		self.setup_highscores()
                        
                


                #Setup Date & Time Display
                self.show_date_time = self.user_settings['Machine (Standard)']['Show Date and Time']

                #Maximum Players
                self.max_players = 4;
                
                #setup paused flag
                self.paused = False

                #add basic modes
                #------------------
                #attract mode
		self.attract_mode = Attract(self)
                #basic game control mode
		self.base_game_mode = BaseGameMode(self)
                #moonlight mode - special
                self.moonlight = Moonlight(self,2)
                #effects mode
                self.effects = Effects(self,4)
                #utility mode
                self.utility = Utility(self)
                #tilt mode
                self.tilt = Tilt(self,5)
                #extra ball mode
                self.extra_ball = Extra_Ball(self)
                #screens mode
                self.screens = Screens(self)
                #match mode
                self.match = Match(self,10)
                #add idol mode for idol logic and control
                self.idol = Idol(self,15)
                #setup mini_playfield
                self.mini_playfield = Mini_Playfield(self,16)
                #------------------


                # set up the color desktop if we're using that
                if self.color_desktop:
                    self.desktop.draw_window(self.user_settings['Machine (Standard)']['Color Display Pixel Size'],self.user_settings['Machine (Standard)']['Color Display X Offset'],self.user_settings['Machine (Standard)']['Color Display Y Offset'])
                    # load the images for the colorized display
                    self.desktop.load_images(dots_path)


		# Instead of resetting everything here as well as when a user
		# initiated reset occurs, do everything in self.reset() and call it
		# now and during a user initiated reset.
		self.reset()
        
        def setup_highscores(self):
		self.highscore_categories = []

                #regular high scores
		cat = highscore.HighScoreCategory()
		cat.game_data_key = 'ClassicHighScoreData'
                self.highscore_categories.append(cat)

                #POA Champion
		cat = highscore.HighScoreCategory()
		cat.game_data_key = 'POAChampionData'
		cat.titles = ['Adventure Champ']
		cat.score_suffix_singular = ' Adventure'
		cat.score_suffix_plural = ' Adventures'
                cat.score_for_player = lambda player: player.player_stats['adventures_started']
		self.highscore_categories.append(cat)
#
                #Treasure Champion
		cat = highscore.HighScoreCategory()
		cat.game_data_key = 'TreasureChampionData'
		cat.titles = ['Treasure Champ']
		cat.score_suffix_singular = ' Artifact'
		cat.score_suffix_plural = ' Artifacts'
                cat.score_for_player = lambda player: player.player_stats['treasures_collected']
		self.highscore_categories.append(cat)

		for category in self.highscore_categories:
			category.load_from_game(self)

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
                self.modes.add(self.utility)
                self.modes.add(self.effects)
		self.modes.add(self.ball_save)
                self.modes.add(self.idol)
                self.modes.add(self.mini_playfield)
		self.modes.add(self.trough)
                self.modes.add(self.tilt)
                self.modes.add(self.extra_ball)
                self.modes.add(self.screens)


		# Make sure flippers are off, especially for user initiated resets.
		self.enable_flippers(enable=False)
                
                #temp addition -testing for Gerry
                #self.coils.swCol9Coil.pulse(0)
                #self.log.info('%s On',self.coils.swCol9Coil.label)


	# Empty callback just incase a ball drains into the trough before another
	# drain_callback can be installed by a gameplay mode.
	def drain_callback(self):
		pass


        def start_game(self,force_moonlight=False):
		super(Game, self).start_game()

                #update game start audits
                self.start_time = time.time()
                audits.record_value(self,'gameStarted')
                if self.user_settings['Machine (Standard)']['Free Play'].startswith('N'):
                    credits =  audits.display(self,'general','creditsCounter')
                    audits.update_counter(self,'credits',credits-1)
                    
                #moonlight check - from Eric P of CCC fame
                #-----------------------------------------
                # Check the time
                now = datetime.datetime.now()
                self.log.info("Hour:%s Minutes:%s",now.hour,now.minute)
                # subtract the window minutes from 60
                window = 60 - self.moonlight_minutes
                self.log.info("Moonlight window time:%s",window)
                # check for moonlight - always works at straight up midnight
                if now.hour == 0 and now.minute == 0:
                    self.moonlight_flag = True
                # If not exactly midnight - check to see if we're within the time window
                elif now.hour == 23 and now.minute >= window:
                    self.moonlight_flag = True
                # if force was passed - start it no matter what
                elif force_moonlight:
                    self.moonlight_flag = True
                else:
                    self.moonlight_flag = False

                self.log.info("Moonlight Flag:%s",self.moonlight_flag)
                #-----------------------------------------
                
	def ball_starting(self):
		super(Game, self).ball_starting()
		
                #check for moonlight
                if self.moonlight_flag and not self.get_player_stats('moonlight_status'):
                    self.modes.add(self.moonlight)
                #else add normal base mode
                else:
                    self.modes.add(self.base_game_mode)

	def ball_ended(self):
		self.modes.remove(self.base_game_mode)
		super(Game, self).ball_ended()

	def game_ended(self):
		super(Game, self).game_ended()

                self.modes.remove(self.base_game_mode)

                self.modes.add(self.match)

                #record audits
                #-------------
                self.game_time = time.time()-self.start_time
                p = self.current_player()
                audits.record_value(self,'gameTime',self.game_time)
                audits.record_value(self,'gamePlayed')
                audits.record_value(self,'gameScore',p.score)
                #-------------

                #update diagnostics
                #--------------------
                self.update_diagnostics()
                #--------------------


        def update_diagnostics(self):
            if self.game_time:
                diagnostics.update_switches(self,self.game_time)
                self.switch_error_log = diagnostics.broken_switches(self)
            else:
                self.switch_error_log = diagnostics.broken_switches(self)

            self.log.debug('Switch Errors:%s',self.switch_error_log)

            
	def set_status(self, text):
		self.dmd.set_message(text, 3)
		print(text)

	def extra_ball_count(self):
		p = self.current_player()
		p.extra_balls += 1
                

	def setup_ball_search(self):
		# No special handlers in starter game.
		special_handler_modes = []
		self.ball_search = mpcBallSearch(self, priority=100, \
                                     countdown_time=10, coils=self.ballsearch_coils, \
                                     reset_switches=self.ballsearch_resetSwitches, \
                                     stop_switches=self.ballsearch_stopSwitches, \
                                     special_handler_modes=special_handler_modes) #procgame.modes.BallSearch



        def enable_flippers(self, enable):
		
		"""Enables or disables the flippers AND bumpers."""
                #wpc flippers
		for flipper in self.config['PRFlippers']:
			self.logger.info("Programming flipper %s", flipper)
			main_coil = self.coils[flipper+'Main']
			hold_coil = self.coils[flipper+'Hold']
			switch_num = self.switches[flipper].number

			drivers = []
			if enable:
				drivers += [pinproc.driver_state_pulse(main_coil.state(), main_coil.default_pulse_time)]
				drivers += [pinproc.driver_state_pulse(hold_coil.state(), 0)]
			self.proc.switch_update_rule(switch_num, 'closed_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
			
			drivers = []
			if enable:
				drivers += [pinproc.driver_state_disable(main_coil.state())]
				if not self.paused or flipper=='FlipperLwL':
					drivers += [pinproc.driver_state_disable(hold_coil.state())]
	
			self.proc.switch_update_rule(switch_num, 'open_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)

			if not enable:
				main_coil.disable()
				hold_coil.disable()

		#bumpers
		self.enable_bumpers(enable)

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



                



def main():
        VAR_PATH='./var'
        if not os.path.exists(VAR_PATH):
            os.mkdir(VAR_PATH)

        LOG_PATH='./var/logs'
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

        root_logger = logging.getLogger()
	root_logger.setLevel(logging.INFO)

        #setup console logging
        from colorlogging import ColorizingStreamHandler
        handler = ColorizingStreamHandler()
        handler.setLevel(logging.INFO)
	handler.setFormatter(logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        #setup logging to file
        datetime = str(time.strftime("%Y-%m-%d %H-%M-%S"))
        file_handler = logging.FileHandler(game_path +'var/logs/'+serial+' Game Log '+datetime+'.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        root_logger.addHandler(handler)
        root_logger.addHandler(file_handler)

        #set invidivual log levels here
        logging.getLogger('ij.idol').setLevel(logging.DEBUG)
        logging.getLogger('ij.trough').setLevel(logging.DEBUG)
        logging.getLogger('ij.base').setLevel(logging.DEBUG)
        logging.getLogger('ij.poa').setLevel(logging.DEBUG)
        logging.getLogger('ij.mode_select').setLevel(logging.DEBUG)
        logging.getLogger('ij.raven_bar').setLevel(logging.DEBUG)
        logging.getLogger('ij.match').setLevel(logging.DEBUG)
        logging.getLogger('game.vdriver').setLevel(logging.ERROR)
        logging.getLogger('game.driver').setLevel(logging.DEBUG)
        logging.getLogger('game.sound').setLevel(logging.ERROR)


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

        except Exception, err:
                log = logging.getLogger()
                log.exception('We are stopping here!:')
                
	finally:
		del game
                


if __name__ == '__main__': main()
