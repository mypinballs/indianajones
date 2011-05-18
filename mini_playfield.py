# Mini Playfield Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:38 PM$"

import procgame
import locale
from procgame import *
import random

class Mini_Playfield(game.Mode):

	def __init__(self, game, priority):
            super(Mini_Playfield, self).__init__(game, priority)

            self.reset()

        def reset(self):
            self.list = ['miniTopLeft','miniTopRight','miniMiddleTopLeft','miniMiddleTopRight','miniMiddleBottomLeft','miniMiddleBottomRight','miniBottomLeft','miniBottomRight']
            self.level = 1
            self.lamps = 2
            self.level_completed = False
            self.lamps_to_go = 0
            pass


        def mode_started(self):
            print("Mini Playfield Mode Started")

            if self.game.switches.topPost.is_active():

                #setup sequence
                self.path_sequence()

                #wait few seconds before releasing ball
                if self.game.switches.topPost.time_since_change() >= 3:
                    self.game.coils.topLockupMain.pulse(50)



        def continue_adventure(self):
            print("Continue Adventure?")
#            top = dmd.TextLayer(20, 7, self.game.fonts['18x12'], "center", opaque=False)
#            bottom = dmd.TextLayer(30, 7, self.game.fonts['07x5'], "center", opaque=False)
#            self.layer = dmd.GroupedLayer(128, 32, [top,bottom])
#
#            if self.level_complete==True:
#                top.setText("LEVEL "+str(self.level))
#                bottom.setText("COMPLETED!")
#
    #        if 4 exit switches not activated for 2 secs
#            #countdown timer - call mode_ended when expired
#            num=15
#            top.setText(str(num))
#            bottom.setText("Continue Adventure?")
            #call delay to end mode reset time if shot remade?





        def path_sequence(self):

            #disable flippers
            self.game.enable_flippers(enable=False)

            #set level and sequence
            if self.level_completed or self.level==0:
                self.level+=1
                self.level_completed = False;

                #setup no of lamps to put out
                self.lamps_to_go = self.level*self.lamps

                #create random lamp sequences
                if self.level<=4:
                    for i in range(0,self.lamps_to_go):
                        lamp_number = randint(0, len(self.list)-1)
                        print("Lamp chosen "+self.list[lamp_number])
                        self.game.drive_lamp(self.list[lamp_number],'medium')



        def mode_ended(self):
            #turn off all mini playfield lamps
            pass

        def centre_playfield(self):
            pass

        def sw_flipperLwL_active(self,sw):
            if self.sw_miniLeftLimit.is_inactive():
                self.game.coils.miniMotorLeft.pulse(0)

            if self.sw_miniLeftLimit.is_active():
                self.game.coils.miniMotorLeft.disable()

        def sw_flipperLwR_active(self,sw):
            if self.sw_miniRightLimit.is_inactive():
                self.game.coils.miniMotorRight.pulse(0)

            if self.sw_miniRightLimit.is_active():
                self.game.coils.miniMotorRight.disable()



        def sw_miniTopHole_active(self, sw):
            self.game.enable_flippers(enable=True)

        def sw_miniBottomHole_active(self, sw):
            self.game.enable_flippers(enable=True)

#        def sw_miniBottomRight_inactive_for_500ms(self, sw):
#            self.game.enable_flippers(enable=True)
#
#        def sw_miniBottomLeft_inactive_for_500ms(self, sw):
#            self.game.enable_flippers(enable=True)


        def sw_miniTopLeft_active(self, sw):
            if self.game.lamps.miniTopLeft.is_active():

                self.game.lamps.miniTopLeft.disable()
                self.lamps_to_go -=1

                if self.lamps_to_go==0:
                    self.level_completed = True
                    self.path_sequence()

        def sw_miniTopRight_active(self, sw):
            if self.game.lamps.miniTopRight.is_active():

                self.game.lamps.miniTopRight.disable()
                self.lamps_to_go -=1

                if self.lamps_to_go==0:
                    self.level_completed = True
                    self.path_sequence()

        def sw_miniMiddleTopLeft_active(self, sw):
            if self.game.lamps.miniMiddleTopLeft.is_active():

                self.game.lamps.miniMiddleTopLeft.disable()
                self.lamps_to_go -=1

                if self.lamps_to_go==0:
                    self.level_completed = True
                    self.path_sequence()

        def sw_miniMiddleTopRight_active(self, sw):
            if self.game.lamps.miniMiddleTopRight.is_active():

                self.game.lamps.miniMiddleTopRight.disable()
                self.lamps_to_go -=1

                if self.lamps_to_go==0:
                    self.level_completed = True
                    self.path_sequence()


        def sw_miniMiddleBottomLeft_active(self, sw):
            if self.game.lamps.miniMiddleBottomLeft.is_active():

                self.game.lamps.miniMiddleBottomLeft.disable()
                self.lamps_to_go -=1

                if self.lamps_to_go==0:
                    self.level_completed = True
                    self.path_sequence()


        def sw_miniMiddleBottomRight_active(self, sw):
            if self.game.lamps.miniMiddleBottomRight.is_active():

                self.game.lamps.miniMiddleBottomRight.disable()
                self.lamps_to_go -=1

                if self.lamps_to_go==0:
                    self.level_completed = True
                    self.path_sequence()


        def sw_miniBottomLeft_active(self, sw):
            if self.game.lamps.miniBottomLeft.is_active():

                self.game.lamps.miniBottomLeft.disable()
                self.lamps_to_go -=1

                if self.lamps_to_go==0:
                    self.level_completed = True
                    self.path_sequence()

        def sw_miniBottomRight_active(self, sw):
            if self.game.lamps.miniBottomRight.is_active():

                self.game.lamps.miniBottomRight.disable()
                self.lamps_to_go -=1

                if self.lamps_to_go==0:
                    self.level_completed = True
                    self.path_sequence()

        def sw_topPost_active_for_500ms(self, sw):
            if self.game.switches.topPost.time_since_change() >= 3:
                self.game.coils.topLockupMain.pulse(50)
                
            return procgame.game.SwitchStop
