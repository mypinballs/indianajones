# Attract Mode

import procgame
import locale
import logging
import audits
import time
import ep
from procgame import *
from random import *
from service import *
from time import strftime


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


class Attract(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game):
		super(Attract, self).__init__(game, 1)
                self.log = logging.getLogger('ij.attract')
                self.display_order = [0,1,2,3,4,5,6,7,8,9]
		self.display_index = 0

		self.game.sound.register_sound('burp',speech_path+'burp.wav')

                #setup coin switches
                self.coin_switchnames=[]
                for switch in self.game.switches.items_tagged('coin'):
                    self.coin_switchnames.append(switch.name)
                    self.log.info("Coin Switch is:"+switch.name)

                for switch in self.coin_switchnames:
			self.add_switch_handler(name=switch, event_type='active', \
				delay=None, handler=self.coin_switch_handler)

	def mode_topmost(self):
		pass

	def mode_started(self):

		# Blink the start button to notify player about starting a game.
		self.game.lamps.startButton.schedule(schedule=0x00ff00ff, cycle_seconds=0, now=False)

                # Turn on GI lamps
		self.delay(name='gi_on_delay', event_type=None, delay=0, handler=self.gi)

                self.log.info("attract mode after gi turn on")

                # run feature lamp patterns
                self.lamp_show_set=True
                self.change_lampshow()

                #debug subway release issues
                self.game.coils.subwayRelease.pulse(100)

                #check for stuck balls
                self.delay(name='idol_empty_delay', event_type=None, delay=2, handler=self.empty_idol)
                self.delay(name='stuck_balls_release_delay', event_type=None, delay=2, handler=self.game.utility.release_stuck_balls)


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

                #self.game_over_layer = dmd.TextLayer(128/2, 10, self.game.fonts['num_09Bx7'], "center", opaque=True).set_text("GAME OVER")
                self.game_over_layer = dmd.TextLayer(128/2, 10, self.game.fonts['num_09Bx7'], "center", opaque=True).set_text("GAME OVER",color=dmd.ORANGE)
                self.game_over_layer.transition = dmd.ExpandTransition(direction='horizontal')#dmd.CrossFadeTransition(width=128,height=32)

                self.scores_layer = dmd.TextLayer(128/2, 11, self.game.fonts['num_09Bx7'], "center", opaque=True).set_text("HIGH SCORES",color=dmd.BROWN)
		self.scores_layer.transition = dmd.PushTransition(direction='west')

                #setup date & time info
                self.day_layer = dmd.DateLayer(128/2, 5, self.game.fonts['tiny7'],"day", "center", opaque=False, colour=dmd.ORANGE)
                self.date_layer = dmd.DateLayer(128/2, 13, self.game.fonts['tiny7'],"date", "center", opaque=False, colour=dmd.YELLOW)
                self.time_layer = dmd.DateLayer(128/2, 21, self.game.fonts['tiny7'],"time", "center", opaque=False, colour=dmd.BROWN)
                self.date_time_layer = dmd.GroupedLayer(128, 32, [self.day_layer,self.date_layer,self.time_layer])
                self.date_time_layer.transition = dmd.PushTransition(direction='west')

                #update the pricing
                self.update_pricing()

                #run attract dmd screens
                self.attract_display()

                #fadeout music (if any running)
                self.delay(name='music_fadeout_delay', event_type=None, delay=10, handler=lambda:self.game.sound.fadeout_music(3000))


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

        def empty_idol(self):
            #total_balls = self.game.trough.num_balls()+self.game.trough.num_balls_locked
            #if total_balls<self.game.num_balls_total:
                #empty the idol mech
                self.game.idol.empty()

       
        def change_lampshow(self):
		shuffle(self.game.lampshow_keys)
                delay=10

                self.game.lampctrl.stop_show()

                #turn gi on or off depending on lampshow chosen from shuffle
                if self.game.lampshow_keys[0].find('flasher',0)>0:
                    self.gi_off()
                else:
                    self.gi()

                if not self.lamp_show_set:
                    #self.log.info('running pattern lamp show')
                    self.game.lampctrl.play_show(self.game.lampshow_keys[0], repeat=True)
                    self.lamp_show_set=True
                else:
                    #self.log.info('running standard lamp show')
                    self.standard_lampshow()
                    self.lamp_show_set=False
                    delay=30

		self.delay(name='lampshow', event_type=None, delay=delay, handler=self.change_lampshow)


        def standard_lampshow(self, enable=True):
		#flash all lamps in groups of 8 ordered by columns
		schedules = [0xffff0000, 0xfff0000f, 0xff0000ff, 0xf0000fff, 0x0000ffff, 0x000ffff0, 0x00ffff00, 0x0ffff000]
		for index, lamp in enumerate(sorted(self.game.lamps, key=lambda lamp: lamp.number)):
                    if lamp.yaml_number.startswith('L'):
			if enable:
				sched = schedules[index%len(schedules)]
				lamp.schedule(schedule=sched, cycle_seconds=0, now=False)
			else:
				lamp.disable()


        def update_pricing(self):
            self.pricing_top = ''
            self.pricing_bottom = ''

            if self.game.user_settings['Machine (Standard)']['Free Play'].startswith('Y'):
                self.pricing_top='FREE PLAY'
            else:
                self.pricing_top=str(audits.display(self.game,'general','creditsCounter')+" CREDITS")

            if audits.display(self.game,'general','creditsCounter') >0 or self.game.user_settings['Machine (Standard)']['Free Play'].startswith('Y'):
                self.pricing_bottom = 'PRESS START'
            else:
                self.pricing_bottom = 'INSERT COINS'

            self.coins_top_layer = dmd.TextLayer(128/2, 6, self.game.fonts['num_09Bx7'], "center", opaque=True).set_text(self.pricing_top,color=dmd.BROWN)
            #self.coins_top_layer.transition = dmd.PushTransition(direction='north')
            self.coins_bottom_layer = dmd.TextLayer(128/2, 18, self.game.fonts['num_09Bx7'], "center", opaque=False).set_text(self.pricing_bottom,color=dmd.DARK_GREEN)
            #self.coins_bottom_layer.transition = dmd.PushTransition(direction='south')

            self.coins_layer = dmd.GroupedLayer(128, 32, [self.coins_top_layer, self.coins_bottom_layer])


        def show_pricing(self):
            self.update_pricing()
            self.layer = self.coins_layer
            
            
        def create_high_scores(self,script):
            # Read the categories
            for category in self.game.highscore_categories:
                title = None # just pre-sets to make the IDE happy
                initLine1 = None
                scoreLine1 = None

                
                for index, score in enumerate(category.scores):
                    score_str = locale.format("%d", score.score, True) # Add commas to the score.

                    ## For the standard high scores
                    if category.game_data_key == 'ClassicHighScoreData':
                        ## score 1 is the grand champion, gets its own frame
                        if index == 0:
                            # this is the new style for the 12 init max
                            
                            title = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text("Grand Champion".upper(),color=dmd.YELLOW)
                            initsLine = dmd.TextLayer(64, 7, self.game.fonts['9px_az'], "center", opaque=False).set_text(score.inits,color=dmd.GREEN)
                            scoreLine = dmd.TextLayer(64, 18, self.game.fonts['10x7_bold'], "center", opaque=False).set_text(score_str)
                            # combine the parts together
                            combined = dmd.GroupedLayer(128, 32, [title, initsLine, scoreLine])
                            combined.transition = dmd.PushTransition(direction='west')
                            # add it to the stack
                            script.append({'seconds':6.0, 'layer':combined})
                            
                             # this section handles scores 2 through 5 (high scores 1 through 4)
                        else:
                            
                            title = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text("Highest Scores".upper(),color=dmd.ORANGE)
                            initsLine = dmd.TextLayer(64, 7, self.game.fonts['9px_az'], "center", opaque=False).set_text(str(index) + ") " + score.inits,color=dmd.YELLOW)
                            scoreLine = dmd.TextLayer(64, 18, self.game.fonts['10x7_bold'], "center", opaque=False).set_text(score_str,color=dmd.BROWN)
                            combined = dmd.GroupedLayer(128, 32, [title, initsLine, scoreLine])
                            combined.transition = dmd.PushTransition(direction='west')
                            # add it to the stack
                            script.append({'seconds':4.0, 'layer':combined})
                            
                    # generate screens for Treasure Champion
                    if category.game_data_key == 'TreasureChampionData':
                        bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
                        title = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text(category.titles[0].upper(),color=dmd.DARK_BROWN)
                        initsLine = dmd.TextLayer(64, 7, self.game.fonts['9px_az'], "center", opaque=False).set_text(score.inits,color=dmd.YELLOW)
                        scoreLine = dmd.TextLayer(64, 18, self.game.fonts['10px_az'], "center", opaque=False).set_text(score_str+" "+category.score_suffix_plural.upper() ,color=dmd.GREY)
                        combined = dmd.GroupedLayer(128,32,[bgnd_layer,initsLine,scoreLine,title])
                        combined.transition = dmd.PushTransition(direction='west')
                        # add it to the stack
                        script.append({'seconds':5.0, 'layer':combined})
                            
                    # generate screens for POA Champion
                    if category.game_data_key == 'POAChampionData':
                        bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
                        title = dmd.TextLayer(128/2, 0, self.game.fonts['5px_az'], "center", opaque=False).set_text(category.titles[0].upper(),color=dmd.DARK_BROWN)
                        initsLine = dmd.TextLayer(64, 7, self.game.fonts['9px_az'], "center", opaque=False).set_text(score.inits,color=dmd.YELLOW)
                        scoreLine = dmd.TextLayer(64, 18, self.game.fonts['10px_az'], "center", opaque=False).set_text(score_str+" "+category.score_suffix_plural.upper(),color=dmd.GREY)
                        combined = dmd.GroupedLayer(128,32,[bgnd_layer,initsLine,scoreLine,title])
                        combined.transition = dmd.PushTransition(direction='west')
                        # add it to the stack
                        script.append({'seconds':5.0, 'layer':combined})


        def attract_display(self):
                script = list()

                script.append({'seconds':5.0, 'layer':self.mypinballs_logo})
                script.append({'seconds':7.0, 'layer':self.williams_logo})
                script.append({'seconds':3.0, 'layer':self.indy_logo})
		script.append({'seconds':3.0, 'layer':self.coins_layer})
		#script.append({'seconds':20.0, 'layer':self.credits_layer})
		script.append({'seconds':3.0, 'layer':None})

                #script.append({'seconds':3.0, 'layer':self.scores_layer})
#		for frame in highscore.generate_highscore_frames(self.game.highscore_categories):
#                    new_layer = dmd.FrameLayer(frame=frame)
#                    new_layer.transition = dmd.PushTransition(direction='west')
#                    script.append({'seconds':2.0, 'layer':new_layer})
                
                self.create_high_scores(script)

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
		if self.game.trough.is_full():
			# Remove attract mode from mode queue - Necessary?
			self.game.modes.remove(self)
			# Initialize game
			self.game.start_game()
			# Add the first player
			self.game.add_player()
			# Start the ball.  This includes ejecting a ball from the trough.
			self.game.start_ball()
		else:

			#self.game.set_status("Ball Search!")
			self.game.ball_search.perform_search(5)
		return True

        def coin_switch_handler(self, sw):
            self.credits =  audits.display(self.game,'general','creditsCounter')
            audits.update_counter(self.game,'credits',self.credits+1)
            self.show_pricing()
            self.game.sound.play("coin")
