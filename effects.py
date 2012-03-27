# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"

class Effects(game.Mode):

	def __init__(self, game):
            super(Effects, self).__init__(game, 4)


        def drive_lamp(self, lamp_name, style='on',time=2):
            if style == 'slow':
       		self.game.lamps[lamp_name].schedule(schedule=0x00ff00ff, cycle_seconds=0, now=True)
            elif style == 'medium':
      		self.game.lamps[lamp_name].schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            elif style == 'fast':
		self.game.lamps[lamp_name].schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            elif style == 'superfast':
		self.game.lamps[lamp_name].schedule(schedule=0x99999999, cycle_seconds=0, now=True)
            elif style == 'on':
		self.game.lamps[lamp_name].enable()
            elif style == 'off':
		self.game.lamps[lamp_name].disable()
            elif style == 'smarton':
		self.game.lamps[lamp_name].schedule(schedule=0xaaaaaaaa, cycle_seconds=0, now=True)
                self.delay(name=lamp_name+'_on', event_type=None, delay=0.6, handler=self.game.lamps[lamp_name].enable)
            elif style == 'timeout':
                self.game.lamps[lamp_name].schedule(schedule=0x55555555, cycle_seconds=0, now=True)
                if time>10:
                    self.delay(name=lamp_name+'_medium', event_type=None, delay=time-10, handler=self.drive_medium, param=lamp_name)
                if time>5:
                    self.delay(name=lamp_name+'_fast', event_type=None, delay=time-5, handler=self.drive_fast, param=lamp_name)
                if time>1:
                    self.delay(name=lamp_name+'_superfast', event_type=None, delay=time-1, handler=self.drive_super_fast, param=lamp_name)
                self.delay(name=lamp_name+'_off', event_type=None, delay=time, handler=self.game.lamps[lamp_name].disable)

        def drive_super_fast(self, lamp_name):
            self.game.lamps[lamp_name].schedule(schedule=0x99999999, cycle_seconds=0, now=True)

        def drive_fast(self, lamp_name):
            self.game.lamps[lamp_name].schedule(schedule=0x55555555, cycle_seconds=0, now=True)

        def drive_medium(self, lamp_name):
            self.game.lamps[lamp_name].schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)