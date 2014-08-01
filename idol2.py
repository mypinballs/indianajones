#Idol Mech Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:06 PM$"

import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Idol(game.Mode):

	def __init__(self, game, priority):
            super(Idol, self).__init__(game, priority)

            self.log = logging.getLogger('ij.idol')
            self.position = 0
            self.balls_in_idol = 0
            self.balls_in_play = 0
            self.ball_max = 3 #make this a game setting
            self.idol_state="initialise"
            self.idol_moving = False
            self.balls_waiting = False
            self.idol_ready_for_lock = False
            self.release= False
            self.lock_lit = False
            self.next_posn_set=False
            self.next_posn_num=0
            self.hasBall = [False,False,False]

            self.game.sound.register_sound('ball_release', sound_path+"elephant.aiff")

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


        def move_to_posn(self,posn_num,callback=None):
            
            if self.position==posn_num:
             if self.idol_moving:
                self.game.coils.wheelMotor.disable()
                self.idol_moving =False
                #self.game.set_status("Position: "+str(self.position))
                #self.release=False
                self.idol_state='idle'
                self.next_posn_num=self.position
                #self.next_posn_set=False

                #callback once at position
                self.callback=callback
                if self.callback:
                    self.callback()
                   
                self.log.info("Reached Idol Destination - Posn: "+str(self.position))

             else: #catch to make sure state is reset even if position is already correct without moving idol
                self.idol_state='idle'


            elif self.position!=posn_num and self.idol_moving==False:
                self.game.coils.wheelMotor.enable()
                self.idol_moving=True
                self.idol_ready_for_lock = False
                
                self.log.info("Idol Moving To Position:"+str(posn_num)+" From Posn:"+str(self.position))
                

        def idol_control(self):
            #mech should always be left idle in a lock position - 1,3,5
            #self.cancel_delayed('move_posn')
            
            if self.idol_state=='initialise':
                self.move_to_posn(1,self.lock_ready)
                
            elif self.idol_state=='empty':
                self.move_to_posn(2,self.ball_release)
                self.delay(name='move_posn', event_type=None, delay=2.5, handler=self.set_state, param='empty2')

            elif self.idol_state=='empty2':
                self.move_to_posn(4,self.ball_release)
                self.delay(name='move_posn', event_type=None, delay=2.5, handler=self.set_state, param='empty3')

            elif self.idol_state=='empty3':
                self.move_to_posn(6,self.ball_release)
                self.delay(name='move_posn', event_type=None, delay=2.5, handler=self.set_state, param='initialise')

            elif self.idol_state=='no_lock':

                #if 1 or more balls in idol release one immediately
                if self.balls_in_idol>=1:
                    self.move_to_posn(self.next_release_posn(),self.ball_release2)
                #otherwise wait for ball to be locked then release it
                else:
                    self.move_to_posn(self.next_lock_posn(),self.single_release)

            elif self.idol_state=='lock':
                #move mech to next free lock posn
                self.move_to_posn(self.next_lock_posn(),self.lock_ready)
                        
            elif self.idol_state=='release':
                #immediately release the nearest ball in mech
                self.move_to_posn(self.next_release_posn(),self.ball_release)


            elif self.idol_state=='hold':
                self.move_to_posn(self.next_lock_posn(),self.lock_ready)
                self.delay(name='move_posn', event_type=None, delay=10, handler=self.lock_release)

        #switch stuff
        #self.game.switches.topIdolEnter.reset_timer()
        #if self.game.switches.topIdolEnter.active(0.5):
        #if self.game.switches.topIdolEnter.time_since_change()>=0.5:

        def lock_ready(self):
            self.idol_ready_for_lock = True

        def ball_release(self):
            self.log.info("Ball Release")
            self.game.coils.idolRelease.pulse(150)
            #self.log.info("IDOL State is:"+self.idol_state)

        def ball_release2(self):
            self.log.info("Ball Release 2")
            self.game.coils.idolRelease.pulse(150)
            #self.log.info("IDOL State is:"+self.idol_state)
            self.delay(name='move_posn', event_type=None, delay=0.5, handler=self.lock)

        def single_release(self):
            self.log.info("Single Release")
            #allow ball to be locked
            self.idol_ready_for_lock = True
            #tell the idol to release it
            self.delay(name='move_posn', event_type=None, delay=2, handler=self.release)

        def set_state(self,value):
            self.idol_state=value

        def empty(self):
            self.set_state('empty')

        def lock(self):
            self.set_state('lock')

        def no_lock(self):
            self.set_state('no_lock')

        def lock_release(self):
            self.set_state('release')

        def hold(self):
            self.set_state('hold')

        def home(self):
            self.log.info("Moving To Home Position")
            self.set_state('initialise')

        def next_lock_posn(self):
            #return the next position to move the idol mech to which will accomodate a ball

            if self.position==1 or self.position==6:
                if self.hasBall[0]==False:
                    self.next_posn_num=1
                elif self.hasBall[1]==False:
                    self.next_posn_num=3
                elif self.hasBall[2]==False:
                    self.next_posn_num=5
            elif self.position==2 or self.position==3:
                if self.hasBall[1]==False:
                    self.next_posn_num=3
                elif self.hasBall[2]==False:
                    self.next_posn_num=5
                elif self.hasBall[0]==False:
                    self.next_posn_num=1
            elif self.position==4 or self.position==5:
                if self.hasBall[2]==False:
                    self.next_posn_num=5
                elif self.hasBall[0]==False:
                    self.next_posn_num=1
                elif self.hasBall[1]==False:
                    self.next_posn_num=3

            return self.next_posn_num
                
        def next_release_posn(self):

            if self.position==1 or self.position==2:
                if self.hasBall[2]:
                    self.next_posn_num=2
                elif self.hasBall[0]:
                    self.next_posn_num=4
                elif self.hasBall[1]:
                    self.next_posn_num=6
            elif self.position==3 or self.position==4:
                if self.hasBall[0]:
                    self.next_posn_num=4
                elif self.hasBall[1]:
                    self.next_posn_num=6
                elif self.hasBall[2]:
                    self.next_posn_num=2
            elif self.position==5 or self.position==6:
                if self.hasBall[1]:
                    self.next_posn_num=6
                elif self.hasBall[2]:
                    self.next_posn_num=2
                elif self.hasBall[0]:
                    self.next_posn_num=4

            return self.next_posn_num


#        def next_posn(self):
#
#            if self.position<6:
#                self.next_posn_num+=1
#            else:
#                self.next_posn_num=1
#
#            return self.next_posn_num


        def sw_wheelPosition2_active(self, sw):
            if self.game.switches.wheelPosition1.is_inactive() and self.game.switches.wheelPosition3.is_active():
                self.position =1
            self.log.info("Position: "+str(self.position))

        def sw_wheelPosition2_inactive(self, sw):
            if self.game.switches.wheelPosition1.is_active() and self.game.switches.wheelPosition3.is_inactive():
                self.position =4
            self.log.info("Position: "+str(self.position))

        def sw_wheelPosition1_active(self, sw):
            if self.game.switches.wheelPosition2.is_active() and self.game.switches.wheelPosition3.is_inactive():
                self.position =3
            self.log.info("Position: "+str(self.position))

        def sw_wheelPosition1_inactive(self, sw):
            if self.game.switches.wheelPosition2.is_inactive() and self.game.switches.wheelPosition3.is_active():
                self.position =6
            self.log.info("Position: "+str(self.position))

        def sw_wheelPosition3_active(self, sw):
            if self.game.switches.wheelPosition1.is_active() and self.game.switches.wheelPosition2.is_inactive():
                self.position =5
            self.log.info("Position: "+str(self.position))

        def sw_wheelPosition3_inactive(self, sw):
            if self.game.switches.wheelPosition1.is_inactive() and self.game.switches.wheelPosition2.is_active():
                self.position =2
            self.log.info("Position: "+str(self.position))


        def check_popper(self):
            self.log.info("Check Popper Called")
            if self.idol_ready_for_lock:
                if self.balls_in_idol<3 and self.game.switches.rightPopper.is_active():
                    self.game.coils.ballPopper.pulse(50)
                elif self.balls_in_idol==3 and self.game.switches.rightPopper.is_active():
                    self.lock_release()
                self.cancel_delayed('check_popper_repeat')
            else:
                 self.delay(name='check_popper_repeat', event_type=None, delay=0.5, handler=self.check_popper)

        #idol upkicker
        def sw_rightPopper_active_for_500ms(self, sw):
            self.check_popper()
        
#        def sw_rightPopper_inactive(self, sw):
#            if self.game.switches.subwayLockup.is_active():
#                self.game.coils.subwayRelease.pulse(30)


        #subway

        def sw_subwayLockup_active(self, sw):
            #self.idol_state='lock'
            if self.game.switches.rightPopper.is_inactive():
                self.game.coils.subwayRelease.pulse(100)
        
#        def sw_subwayLockup_inactive(self, sw):
#            pass

        def update_ball_tracking(self,num):
            self.game.trough.num_balls_locked = self.balls_in_idol
            self.game.trough.num_balls_in_play +=num
            self.log.info("Balls in Idol: "+str(self.balls_in_idol))

            self.update_has_ball()

        def update_has_ball(self):
            if self.position==1:
                self.hasBall[0] = True
            elif self.position==4:
                self.hasBall[0] = False

            elif self.position==3:
                self.hasBall[1] = True
            elif self.position==6:
                self.hasBall[1] = False
                
            elif self.position==5:
                self.hasBall[2] = True
            elif self.position==2:
                self.hasBall[2] = False

            self.log.info("Ball Locked Positions are:%s",self.hasBall)

        #idol entrance
        def sw_topIdolEnter_active(self, sw):
            if self.game.ball>0:
                self.balls_in_idol+=1
                self.update_ball_tracking(-1)
               

        def sw_exitIdol_active(self, sw):
            if self.game.ball>0:
                self.balls_in_idol-=1
                self.update_ball_tracking(1)
                self.check_popper()
                self.game.sound.play("ball_release")


        def sw_buyInButton_active_for_500ms(self, sw):
            #debug
            self.idol_state='empty'
            self.log.info(str(self.position))
            #self.game.coils.wheelMotor.pulse(250)


