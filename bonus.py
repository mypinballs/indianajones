import procgame
from procgame import *
import locale


base_path = config.value_for_key_path('base_path')
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

                self.mode_bonus_bgnd = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/scene_ended_bgnd.dmd').frames[0])
                self.mode_bonus_layer = dmd.GroupedLayer(128, 32, [self.title_layer, self.value_layer,self.mode_bonus_bgnd])
                #self.mode_bonus_layer.transition = dmd.ExpandTransition(direction='vertical')

		self.bonus_counter = 0
                self.mode_counter =0
                self.mode_total = 0
		self.delay_time = 1.6
                self.base_value = 100000

                self.game.sound.register_music('bonus', music_path+"bonus.aiff")
                self.game.sound.register_sound('bonus_end', sound_path+"bonus_end_jingle.aiff")
                self.game.sound.register_sound('bonus_mode_completed1', sound_path+"bonus_mode_completed1.aiff")
                self.game.sound.register_sound('bonus_mode_completed2', sound_path+"bonus_mode_completed2.aiff")
                self.game.sound.register_sound('bonus_mode_completed3', sound_path+"bonus_mode_completed3.aiff")
                self.game.sound.register_sound('bonus_mode_completed4', sound_path+"bonus_mode_completed4.aiff")
                self.game.sound.register_sound('bonus_mode_completed5', sound_path+"bonus_mode_completed5.aiff")
                self.game.sound.register_sound('bonus_mode_completed6', sound_path+"bonus_mode_completed6.aiff")
                self.game.sound.register_sound('bonus_mode_completed7', sound_path+"bonus_mode_completed7.aiff")
                self.game.sound.register_sound('bonus_mode_completed8', sound_path+"bonus_mode_completed8.aiff")
                self.game.sound.register_sound('bonus_mode_completed9', sound_path+"bonus_mode_completed9.aiff")
                self.game.sound.register_sound('bonus_mode_completed10', sound_path+"bonus_mode_completed10.aiff")
                self.game.sound.register_sound('bonus_mode_completed11', sound_path+"bonus_mode_completed11.aiff")
                self.game.sound.register_sound('bonus_mode_completed12', sound_path+"bonus_mode_completed12.aiff")


	def mode_started(self):
		# Disable the flippers
		self.game.enable_flippers(enable=False)
                print("Debug, Bonus Mode Started")


	def mode_stopped(self):
		# Enable the flippers
		self.game.enable_flippers(enable=True)
                self.game.sound.stop_music()
                print("Debug, Bonus Mode Ended")


        def get_bonus_value(self):
            friends = self.game.get_player_stats('friends_collected') * 40000
            ramps =  self.game.get_player_stats('ramps_made') * 10000
            adventure_letters = self.game.get_player_stats('adventure_letters_collected') * 5000
            slingshots = self.game.get_player_stats('slingshot_hits')*3000

            return self.base_value+friends+ramps+adventure_letters+slingshots

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
            mode_stats = self.game.get_player_stats("bonus_mode_tracking")
            for item in mode_stats:
		self.elements.append(item['name'])
		self.value.append(item['score'])

            self.mode_counter = 0
            self.modes_display()

        def modes_display(self):
            if self.mode_counter<len(self.elements):
                self.title_layer.set_text(self.elements[self.mode_counter])
                self.value_layer.set_text(locale.format("%d", self.value[self.mode_counter], True))
                self.layer = self.mode_bonus_layer
                self.game.sound.play('bonus_mode_completed'+str(self.mode_counter+1))
                self.mode_total =self.mode_total+self.value[self.mode_counter]
                self.mode_counter+=1
                
                self.delay(name='mode_bonus', event_type=None, delay=self.delay_time, handler=self.modes_display)
                
            else:
                self.total()

	
	def total(self):
            
            if self.bonus_counter == 0:
                self.game.sound.fadeout_music()
                self.game.sound.play('bonus_end')
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

