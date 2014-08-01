import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"


class mpcBallSearch(procgame.modes.BallSearch):
	"""Ball Search mode improvements."""
	def __init__(self, game, priority, countdown_time, coils=[], reset_switches=[], stop_switches=[], enable_switch_names=[], special_handler_modes=[]):
                super(mpcBallSearch, self).__init__(game, priority, countdown_time, coils=[], reset_switches=[], stop_switches=[], enable_switch_names=[], special_handler_modes=[])

                self.log = logging.getLogger('ij.ballSearch')
                self.game.sound.register_sound('elephant_alert', sound_path+"elephant.aiff")
                
    

	def perform_search(self, completion_wait_time, completion_handler = None):
		if (completion_wait_time != 0):
			self.ball_missing()
		delay = .150
		for coil in self.coils:
			self.delay(name='ball_search_coil1', event_type=None, delay=delay, handler=self.pop_coil, param=str(coil))
			delay = delay + .150
		self.delay(name='start_special_handler_modes', event_type=None, delay=delay, handler=self.start_special_handler_modes)

		if (completion_wait_time != 0):
			pass
		else:
			self.cancel_delayed(name='ball_search_countdown');
			self.delay(name='ball_search_countdown', event_type=None, delay=self.countdown_time, handler=self.perform_search, param=0)

        def ball_missing(self):
            info_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)
            bgnd_layer = dmd.FrameLayer(opaque=False)
            bgnd_layer.frame = dmd.Animation().load(game_path+'dmd/scene_ended_bgnd.dmd').frames[0]

            multiple = ''
            balls_missing = self.game.num_balls_total - self.game.trough.num_balls()
            if balls_missing>1:
                multiple='s'

            message = str(balls_missing)+" BALL"+multiple+" LOST!"
            info_layer.set_text(message,2,5)#on for 1.5 seconds 5 blinks
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_layer])
            self.game.sound.play('elephant_alert')
            self.log.info(message)

            self.delay(name='clear',delay=2, handler=self.clear)

            
        def clear(self):
            self.layer = None