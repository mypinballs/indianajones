import procgame
from procgame import *
import locale


base_path = "/Users/jim/Documents/Pinball/p-roc/p-roc system/src/"
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Bonus(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
		super(Bonus, self).__init__(game, priority)

                self.title_layer = dmd.TextLayer(128/2, 2, self.game.fonts['num_09Bx7'], "center")
		self.value_layer = dmd.TextLayer(128/2, 17, self.game.fonts['num_14x10'], "center")
		self.bonus_layer = dmd.GroupedLayer(128, 32, [self.title_layer, self.value_layer])
                #self.bonus_layer.transition = dmd.ExpandTransition(direction='vertical')

                self.mode_bonus_bgnd = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/mode_bonus_bgnd.dmd').frames[0])
                self.mode_bonus_layer = dmd.GroupedLayer(128, 32, [self.title_layer, self.value_layer,self.mode_bonus_bgnd])
                #self.mode_bonus_layer.transition = dmd.ExpandTransition(direction='vertical')

		self.bonus_counter = 0
                self.mode_counter =0
                self.mode_total = 0
		self.delay_time = 1.5

                self.game.sound.register_music('bonus', music_path+"bonus.aiff")

	def mode_started(self):
		# Disable the flippers
		self.game.enable_flippers(enable=False)

	def mode_stopped(self):
		# Enable the flippers
		self.game.enable_flippers(enable=True)

        def get_bonus_value(self):
            friends = self.game.get_player_stats('friends_collected') * 40000
            ramps =  self.game.get_player_stats('ramps_made') * 10000
            adventure_lettters = self.game.get_player_stats('adventure_letters_collected') * 5000

            return friends+ramps+adventure_lettters

        def get_bonus_x(self):
            bonus_x = self.game.get_player_stats('bonus_x')
            return bonus_x

        def calculate(self,callback):
            self.game.sound.play_music('bonus', loops=1)
	    self.callback = callback
            self.base()

	def base(self):
            
            self.bonus_x = self.get_bonus_x()
            self.total_base = self.get_bonus_value()

            if self.bonus_x>1:
                x_display = ' X'+str(self.bonus_x)
            else:
                x_display=''

            self.title_layer.set_text('BONUS'+ x_display)
            self.value_layer.set_text(locale.format("%d", self.total_base, True))
            self.layer = self.bonus_layer

            self.delay(name='bonus_total', event_type=None, delay=self.delay_time, handler=self.modes)

        def modes(self):
            

            self.elements = []
            self.value = []
#            for element, value in mode_stats.iteritems():
#		self.elements.append(element)
#		self.value.append(value)
            
            if self.mode_counter <len(self.elements):
                self.title_layer.set_text(self.elements[self.mode_counter],seconds=self.delay_time)
                self.value_layer.set_text(locale.format("%d", self.value[self.mode_counter], True),seconds=self.delay_time)
                self.layer = self.mode_bonus_layer

                self.mode_total =self.mode_total+self.value[self.mode_counter]
                self.delay(name='mode_bonus', event_type=None, delay=self.delay_time, handler=self.modes)
            else:
                self.total()

            self.mode_counter += 1


	
	def total(self):
            
            if self.bonus_counter == 0:
                self.game.sound.fadeout_music()
                self.game.sound.play('bonus')
                total_bonus = (self.total_base * self.bonus_x)+self.mode_total
                self.title_layer.set_text('TOTAL BONUS',seconds=self.delay_time)
                self.value_layer.set_text(locale.format("%d", total_bonus, True),seconds=self.delay_time)
                self.layer = self.bonus_layer

                self.game.score(total_bonus)
    
                self.delay(name='bonus_total', event_type=None, delay=self.delay_time, handler=self.total)
            else:
                self.callback()

            self.bonus_counter += 1

	def sw_flipperLwL_active(self, sw):
		if self.game.switches.flipperLwR.is_active():
			self.delay_time = 0.250

	def sw_flipperLwR_active(self, sw):
		if self.game.switches.flipperLwL.is_active():
			self.delay_time = 0.250

