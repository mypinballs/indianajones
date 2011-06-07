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
            self.list = ['miniTopLeft','miniTopRight','miniMiddleTopLeft','miniMiddleTopRight','miniMiddleBottomLeft','miniMiddleBottomRight','miniBottomLeft','miniBottomRight','miniTopArrow','miniBottomArrow']
            self.lamp_flag = [False,False,False,False,False,False,False,False,False,False]

            self.level = 1
            self.lamps = 2
            self.level_completed = False
            self.lamps_to_go = 0
            self.pit_value_active = False
            self.extra_ball_active = False

            self.loop_num = 0
            self.loop = 1
            self.status = 'initialise'
            self.game_status = 'idle'
            
            self.position =None

            if self.game.switches.miniLeftLimit.is_active():
                self.postion='left'
            elif self.game.switches.miniRightLimit.is_active():
                self.position ='right'
            else:
                self.position = 'unknown'


            self.dirn_time = 150 #default timing for movement
            self.centre_time = self.dirn_time/2
            self.motor_off()
            pass


        def mode_started(self):
            print("Mini Playfield Mode Started")

            #setup mechanism
            #self.game.set_status(self.position)
            #self.calibrate()
            #self.game.coils.miniMotorRight.pulse(self.centre_time)
            #self.game.coils.miniMotorLeft.pulse(self.centre_time)


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

            self.game_status='mode'
            

            #set level and sequence
            if self.level_completed or self.level==0:
                self.level+=1
                self.level_completed = False;

            #setup num of lamps to put out
            self.lamps_to_go = self.level*self.lamps
            self.reset_lamps()

            #create random lamp sequences
            if self.level<=4:
                for i in range(0,self.lamps_to_go):
                    lamp_number = random.randint(0, 7)
                    print("Lamp chosen "+self.list[lamp_number])
                    self.game.effects.drive_lamp(self.list[lamp_number],'medium')
                    self.lamp_flag[lamp_number]=True


            if self.level%2==0:
                 self.game.effects.drive_lamp(self.list[9],'medium')
                 self.lamp_flag[9]=True
                 self.extra_ball_active = True

            if self.level>=3:
                 self.game.effects.drive_lamp(self.list[8],'medium')
                 self.lamp_flag[8]=True
                 self.pit_value_active = True


        def inc_pit_value(self):
            self.game.poa.pit_value += 5000000+(1000000*self.level)


        def path_ended(self):

            self.game_status ='idle'
            #turn off all mini playfield lamps
            self.reset_lamps()
            self.centre_playfield()

            

        def reset_lamps(self):
            for i in range(len(self.list)):
                self.game.effects.drive_lamp(self.list[i],'off')
                self.lamp_flag[i]=False

        def update_lamps(self):
            print("Updating Mini Playfield lane lamps")
            for i in range(len(self.list)):
                if self.lamp_flag[i]:
                    self.game.effects.drive_lamp(self.list[i],'medium')



        def centre_playfield(self):

            if self.status !='broken':
                if self.position=='left':
                    self.game.coils.miniMotorRight.pulse(self.centre_time)
                elif self.position=='right':
                    self.game.coils.miniMotorLeft.pulse(self.centre_time)



        def motor_on(self,dirn):
            
            if self.status !='broken':
                if dirn=='left' and self.position!='left':
                    self.game.coils.miniMotorLeft.pulse(self.dirn_time)#
                    self.position='left' #set value in case pulse short
                elif dirn=='right'and self.position!='right':
                    self.game.coils.miniMotorRight.pulse(self.dirn_time)#.schedule(schedule=0x33333333 , cycle_seconds=0, now=True)
                    self.position='right' #set value in case pulse short
                else: #safety catch
                    self.motor_off()
           

        def motor_off(self):
            self.game.coils.miniMotorLeft.disable()
            self.game.coils.miniMotorRight.disable()
            self.motor_dirn='off'



        def calibrate(self,num=1):
#            if num:
#                self.loop_num = num
#                self.loop = 0

            time1 = self.game.switches.miniLeftLimit.last_changed*100
            time2 = self.game.switches.miniRightLimit.last_changed*100

            print("Time 1:"+str(time1))
            print("Time 2:"+str(time2))

            if time1>time2:
                dirn_time = time1-time2
            elif time2>time1:
                dirn_time = time2-time1

            center_time = dirn_time/2

            print("Max Posn Time is:"+str(dirn_time))
            print("Center Time is:"+str(centre_time))


            if self.loop<=12: #self.loop_num:
                print("Mini Playfield Position is:"+str(self.position))

                if self.loop%2!=0:#odd
                    print("Odd")
                    self.motor_on('left')
                else:
                    print("Even")
                    self.motor_on('right')

                self.loop+=1
                self.delay(name='calibration_loop', event_type=None, delay=0.5, handler=self.calibrate)

            else:
                self.centre_playfield()


        def check_switches(self):

            if self.game.switches.miniLeftLimit.is_active() and self.game.switches.miniRightLimit.is_active():
                self.status='broken'
            else:
                self.status='working'


        def sw_flipperLwL_active(self,sw):
            if self.game_status !='idle':
                self.cancel_delayed('centre_timeout')
                self.motor_on('left')
            

        def sw_flipperLwR_active(self,sw):
            if self.game_status !='idle':
                self.cancel_delayed('centre_timeout')
                self.motor_on('right')


        def sw_flipperLwL_inactive(self,sw):
            if self.game_status !='idle':
                self.delay(name='centre_timeout', event_type=None, delay=1, handler=self.centre_playfield)

            
        def sw_flipperLwR_inactive(self,sw):
            if self.game_status !='idle':
                self.delay(name='centre_timeout', event_type=None, delay=1, handler=self.centre_playfield)
            


        def sw_miniLeftLimit_active(self,sw):
            print("left limit")
            self.game.set_status("left limit")
            self.position = 'left'
            self.motor_off()
            self.check_switches()

        def sw_miniRightLimit_active(self,sw):
            print("right limit")
            self.game.set_status("right limit")
            self.position = 'right'
            self.motor_off()
            self.check_switches()

            

        def sw_miniTopHole_active(self, sw):
            if self.pit_active:
                 self.game.score(self.game.poa.pit_value)
                 self.game.poa.reset_pit_value()
                 
            self.game.enable_flippers(enable=True)

        def sw_miniBottomHole_active(self, sw):
            if self.extra_ball_active:
                 self.game.extra_ball()

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
                self.pit_value()

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

                self.game.enable_flippers(enable=True)

        def sw_miniBottomRight_active(self, sw):
            if self.game.lamps.miniBottomRight.is_active():

                self.game.lamps.miniBottomRight.disable()
                self.lamps_to_go -=1

                if self.lamps_to_go==0:
                    self.level_completed = True
                    self.path_sequence()

                self.game.enable_flippers(enable=True)

        def sw_topPost_active_for_2000ms(self, sw):
                self.game.coils.topLockupMain.pulse()
                self.game.coils.topLockupHold.pulse(200)

                #disable flippers
                self.game.enable_flippers(enable=False)
                
            #return procgame.game.SwitchStop
