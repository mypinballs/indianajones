import procgame
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Tilt(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
            super(Tilt, self).__init__(game, priority)

            self.game.sound.register_sound('tilt warning', speech_path+"carefully.aiff")
            self.game.sound.register_sound('tilt', sound_path+"tilt.aiff")
            self.game.sound.register_sound('tilt_speech', speech_path+"behave_like_civilised_people.aiff")

            self.tilt_callback = None


        def reset(self):
            self.status = 0
            self.times_warned = 0
            self.layer = None
            self.tilted = False


	def mode_started(self):
            self.num_tilt_warnings = self.game.user_settings['Machine (Standard)']['Tilt Warnings']
            self.reset()
		

        def get_status(self):
            if self.status==0:
                return False
            elif self.status==1:
                return True


        def tilt_display(self,text,timer=0):

            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])
            text_layer = dmd.TextLayer(128/2, 12, self.game.fonts['num_09Bx7'], "center")

            text_layer.set_text(text.upper())

            #update display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,text_layer])

            if timer>0:
                self.delay(name='clear_display_delay', event_type=None, delay=timer, handler=self.clear)

        def tilt(self):

                #check if already in a tilt state
		if self.status == 0:

                        #set status
                        self.status = 1
                        self.tilted = True

			#update display
                        self.cancel_delayed('clear_display_delay')
                        self.tilt_display('Tilt')

                        #play sound
                        self.game.sound.stop('tilt warning')
                        self.game.sound.stop_music()
                        self.game.sound.play('tilt')
                        self.delay('tilt_speech_delay',delay=2,handler=lambda:self.game.sound.play_voice('tilt_speech'))

			#turn off flippers
			self.game.enable_flippers(enable=False)

			# Make sure ball won't be saved when it drains.
			self.game.ball_save.disable()

			# Make sure the ball search won't run while ball is draining.
			self.game.ball_search.disable()

			#turn off all lamps
			for lamp in self.game.lamps:
				lamp.disable()

                        #check for stuck balls
			self.game.utility.release_stuck_balls()

                        if self.tilt_callback:
                            self.tilt_callback()

			
        def warning(self):
            self.game.sound.stop('tilt warning')
            self.game.sound.play('tilt warning')
            self.tilt_display('Warning',3)


        def slam_tilt(self):
            self.tilt_display('Slam Tilt',3)
            self.delay('reset_system',delay=3,handler=self.system_reset)


        def clear(self):
            self.layer = None

        def system_reset(self):
            self.game.reset()
            

       


	def sw_tilt_active(self, sw):
            self.times_warned += 1
            
            if self.times_warned == self.num_tilt_warnings:
                if not self.tilted:
                    self.tilt()
            else:
                self.warning()



	def sw_slamTilt_active(self, sw):
            self.slam_tilt()
		

