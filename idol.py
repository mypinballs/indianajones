#Idol Mech Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:06 PM$"

import procgame
import locale
from procgame import *


class Idol(game.Mode):

	def __init__(self, game, priority):
            super(Idol, self).__init__(game, priority)

            self.position = 0
            self.balls_in_idol = 0
            self.idol_state="initialise"
            self.idol_moving = False
            self.balls_waiting = False
            self.release= False
            self.lock_lit = False

        def reset(self):
            pass


        def mode_started(self):
            #self.test()
            #self.empty()
            pass

        def mode_tick(self):
            #self.move_to_posn(1)
            self.idol_control()
            #pass


        def move_to_posn(self,posn_num):
            
            if self.position==posn_num and self.idol_moving:
                self.game.coils.wheelMotor.disable()
                self.idol_moving =False
                self.game.set_status("Position: "+str(self.position))
                self.release=False

                print("Reached Idol Destination - Posn: "+str(self.position))

            elif self.position!=posn_num and self.idol_moving==False:
                self.game.coils.wheelMotor.pulse(0)
                self.idol_moving=True
                
                print("First Reported Idol Position was: "+str(self.position))
                
            
        def idol_control(self):
            
            if self.idol_state=='initialise':
                self.move_to_posn(1)
                
            elif self.idol_state=='empty':
                self.move_to_posn(2)
                if self.position==2 and self.idol_moving==False and self.release==False:
                    self.game.coils.idolRelease.pulse(150)
                    self.release = True
                    #print("coil fired at posn 2")
                    self.delay(name='move_posn', event_type=None, delay=3, handler=self.set_state, param='empty2')
                    #print("delay called")
            elif self.idol_state=='empty2':
                self.move_to_posn(4)
                if self.position==4 and self.idol_moving==False and self.release==False:
                    self.game.coils.idolRelease.pulse(150)
                    self.release = True
                    self.delay(name='move_posn', event_type=None, delay=3, handler=self.set_state, param='empty3')
            elif self.idol_state=='empty3':
                self.move_to_posn(6)
                if self.position==6 and self.idol_moving==False and self.release==False:
                    self.game.coils.idolRelease.pulse(150)
                    self.release = True
                    self.delay(name='move_posn', event_type=None, delay=3, handler=self.set_state, param='initialise')

#               
            elif self.idol_state=='no_lock':
                self.move_to_posn(4)
                if self.position==4 and self.idol_moving==False and self.release==False:
                    self.game.coils.idolRelease.pulse(150)
                    self.release = True
                    self.delay(name='move_posn', event_type=None, delay=3, handler=self.set_state, param='initialise')



            elif self.idol_state=='lock':
                    if self.position==2 or self.position==4 or self.position==6:
                        self.next_posn()
                    elif self.balls_in_idol >0:
                        self.next_lock_posn()
                        
            elif self.idol_state=='release_single':
                    self.next_release_posn()
                        



        def empty(self):
            self.set_state('empty')

        def home(self):
            print("Moving To Home Position")
            self.set_state('initialise')

        def set_state(self,value):
            self.idol_state=value


        def next_lock_posn(self):
            if self.position==1:
                self.move_to_posn(3)
            elif self.position==3:
                self.move_to_posn(5)
            elif self.position==5:
                self.move_to_posn(1)
                
        def next_release_posn(self):
            if self.position==2:
                self.move_to_posn(4)
            elif self.position==4:
                self.move_to_posn(6)
            elif self.position==6:
                self.move_to_posn(2)

        def next_posn(self):
            if self.position==1:
                self.move_to_posn(2)
            elif self.position==2:
                self.move_to_posn(3)
            elif self.position==3:
                self.move_to_posn(4)
            elif self.position==4:
                self.move_to_posn(5)
            elif self.position==5:
                self.move_to_posn(6)
            elif self.position==6:
                self.move_to_posn(1)

        def sw_wheelPosition2_active(self, sw):
            if self.game.switches.wheelPosition1.is_inactive() and self.game.switches.wheelPosition3.is_active():
                self.position =1
            print "Position: "+str(self.position)

        def sw_wheelPosition2_inactive(self, sw):
            if self.game.switches.wheelPosition1.is_active() and self.game.switches.wheelPosition3.is_inactive():
                self.position =4
            print "Position: "+str(self.position)

        def sw_wheelPosition1_active(self, sw):
            if self.game.switches.wheelPosition2.is_active() and self.game.switches.wheelPosition3.is_inactive():
                self.position =3
            print "Position: "+str(self.position)

        def sw_wheelPosition1_inactive(self, sw):
            if self.game.switches.wheelPosition2.is_inactive() and self.game.switches.wheelPosition3.is_active():
                self.position =6
            print "Position: "+str(self.position)

        def sw_wheelPosition3_active(self, sw):
            if self.game.switches.wheelPosition1.is_active() and self.game.switches.wheelPosition2.is_inactive():
                self.position =5
            print "Position: "+str(self.position)

        def sw_wheelPosition3_inactive(self, sw):
            if self.game.switches.wheelPosition1.is_inactive() and self.game.switches.wheelPosition2.is_active():
                self.position =2
            print "Position: "+str(self.position)


        #idol upkicker
        def sw_rightPopper_active_for_1s(self, sw):
           # if self.game.switches.topIdolEnter.is_inactive():
            self.game.coils.ballPopper.pulse(50)
        
#        def sw_rightPopper_inactive(self, sw):
#            if self.game.switches.subwayLockup.is_active():
#                self.game.coils.subwayRelease.pulse(20)


        #subway

        #subway entrance needs using

        def sw_subwayLockup_active(self, sw):
            #self.idol_state='lock'
            if self.game.switches.rightPopper.is_inactive():
                self.game.coils.subwayRelease.pulse(20)
        
#        def sw_subwayLockup_inactive(self, sw):
#            pass


        #idol entrance
        def sw_topIdolEnter_time_since_change_500ms(self, sw):
            self.balls_in_idol+=1
            if self.idol_state !='empty':
                if self.balls_in_idol>3:
                   self.set_state('release_single')
                elif self.lock_lit==False:
                    self.set_state('no_lock')
                else:
                    self.set_state('lock')

#        def sw_topIdolEnter_inactive(self, sw):
#            if self.game.switches.subwayLockup.is_active():
#                self.game.coils.subwayRelease.pulse(20)


        def sw_exitIdol_active(self, sw):
            self.balls_in_idol-=1

        def sw_buyInButton_active_for_500ms(self, sw):
            self.idol_state='empty'


