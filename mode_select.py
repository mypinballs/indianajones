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
            self.current_mode_num = 0
            self.reset()


        def reset(self):
            print("Main Mode Select Started")
            self.reset_lamps()

        def reset_lamps(self):
            #loop round and turn off all lamps
            for i in range(len(self.lamp_list)):
                self.game.drive_lamp(self.lamp_list[i],'off')


        def mode_started(self):
            self.unplayed_scenes()

        def mode_tick(self):
            pass


        def unplayed_scenes(self):
            #create list of unplayed scenes (0)
            choice_list=[]
            for i in range(len(self.select_list)):
                if self.select_list[i]==0:
                    choice_list.append(i)

            #set current mode var
            num = random.randint(0, len(choice_list)-1)
            self.current_mode_num = num

            #turn on relevent lamp
            self.game.drive_lamp(self.lamp_list[self.current_mode_num],'medium')

            #update select list
            self.select_list[self.current_mode_num] =1


        def move_left(self):
            #turn off current mode lamp
            self.game.drive_lamp(self.lamp_list[self.current_mode_num],'off')

            #find next non attempted mode
            modes_available =self.select_list[0:self.current_mode_num]
            next_mode_num = modes_available[::-1].index(0)

            #flash new mode lamp
            self.game.drive_lamp(self.lamp_list[next_mode_num],'medium')

            #update tracking vars
            self.select_list[self.current_mode_num] =0
            self.select_list[next_mode_num] =1
            self.current_mode_num = next_mode_num

            #dmd stuff here
            #self.info_layer.set_text("duh duh duh duh!!!")
            #self.layer = dmd.GroupedLayer(128, 32, [self.text_layer, self.info_layer])

            self.game.coils.flasherLeftRamp.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.delay(name='disable_flasher', event_type=None, delay=2, handler=self.game.coils.flasherLeftRamp.disable)


        def move_right(self):
            #turn off current mode lamp
            self.game.drive_lamp(self.lamp_list[self.current_mode_num],'off')

            #find next non attempted mode
            modes_available =self.select_list[self.current_mode_num:len(self.select_list)]
            next_mode_num = modes_available.index(0)

            #flash new mode lamp
            self.game.drive_lamp(self.lamp_list[next_mode_num],'medium')

            #update tracking vars
            self.select_list[self.current_mode_num] =0
            self.select_list[next_mode_num] =1
            self.current_mode_num = next_mode_num

            #dmd stuff here
            #self.info_layer.set_text("rah rah rah rah!!!")
            #self.layer = dmd.GroupedLayer(128, 32, [self.text_layer, self.info_layer])

            self.game.coils.flasherRightRamp.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.delay(name='disable_flasher', event_type=None, delay=2, handler=self.game.coils.flasherRightRamp.disable)



        def sw_leftRampMade_active(self, sw):

            self.move_left()


        def sw_rightRampMade_active(self, sw):

            self.move_right()

       