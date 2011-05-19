import random
# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *


class Mode_Select(game.Mode):

	def __init__(self, game, priority):
            super(Mode_Select, self).__init__(game, priority)
            self.text_layer = dmd.TextLayer(128/2, 7, self.game.fonts['07x5'], "center")
            self.info_layer = dmd.TextLayer(128/2, 17, self.game.fonts['num_14x10'], "center")
           
            self.lamp_list = ['getTheIdol','streetsOfCairo','wellOfSouls','ravenBar','monkeyBrains','stealTheStones','mineCart','ropeBridge','castleGrunwald','tankChase','theThreeChallenges','chooseWisely']
            self.select_list = [0,0,0,0,0,0,0,0,0,0,0,0]
            self.current_mode_num = self.game.get_player_stats('current_mode_num')
            self.choice_id =0
            self.reset()


        def reset(self):
            print("Main Mode Select Started")
            self.reset_lamps()

        def reset_lamps(self):
            #loop round and turn off all lamps
            for i in range(len(self.lamp_list)):
                self.game.effects.drive_lamp(self.lamp_list[i],'off')


        def mode_started(self):
            self.unplayed_scenes()

        def mode_tick(self):
            pass

        def update_lamps(self):
            print("Updating Selected Mode Lamp")
            self.game.effects.drive_lamp(self.lamp_list[self.current_mode_num],'medium')


        def unplayed_scenes(self,dirn=None):

            #turn off current mode lamp
            self.game.drive_lamp(self.lamp_list[self.current_mode_num],'off')

            #create list of unplayed scene numbers
            choice_list=[]
            for i in range(len(self.select_list)):
                if self.select_list[i]==0:
                    choice_list.append(i)
           
            #adjust choice number
            if dirn=='left':
                self.choice_id -=1
            elif dirn=='right':
                self.choice_id +=1
            else:
                self.choice_id = random.randint(0, len(choice_list)-1)

            #create wrap around
            if self.choice_id>len(choice_list)-1:
                self.choice_id=0
            elif self.choice_id<0:
                self.choice_id=len(choice_list)-1

            #set new mode number
            self.current_mode_num = choice_list[self.choice_id]

            #turn on relevent lamp
            self.game.effects.drive_lamp(self.lamp_list[self.current_mode_num],'medium')
            print("mode now active:"+str(self.lamp_list[self.current_mode_num]))

            #update player stats
            self.game.set_player_stats('current_mode_num',self.current_mode_num)

            #use this when a mode is completed, not here
            #self.select_list[self.current_mode_num] =1


        def move_left(self):
            
            self.unplayed_scenes('left')

            self.game.coils.flasherLeftRamp.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.delay(name='disable_flasher', event_type=None, delay=2, handler=self.game.coils.flasherLeftRamp.disable)


        def move_right(self):
            
            self.unplayed_scenes('right')

            self.game.coils.flasherRightRamp.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.delay(name='disable_flasher', event_type=None, delay=2, handler=self.game.coils.flasherRightRamp.disable)



        def sw_leftRampMade_active(self, sw):

            self.move_left()


        def sw_rightRampMade_active(self, sw):

            self.move_right()

       