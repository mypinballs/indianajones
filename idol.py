#Idol Mech Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:06 PM$"

import procgame
import locale
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Idol(game.Mode):

	def __init__(self, game, priority):
            super(Idol, self).__init__(game, priority)

            self.position = 0
            self.balls_in_idol = 0
            self.balls_in_play = 0
            self.ball_max = 3 #make this a game setting
            self.idol_state="initialise"
            self.idol_moving = False
            self.balls_waiting = False
            self.release= False
            self.lock_lit = False
            self.next_posn_set=False
            self.next_posn_num=0

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


        def move_to_posn(self,posn_num):
            
            if self.position==posn_num and self.idol_moving:
                self.game.coils.wheelMotor.disable()
                self.idol_moving =False
                self.game.set_status("Position: "+str(self.position))
                self.release=False
                self.idol_state='idle'
                self.next_posn_num=self.position
                self.next_posn_set=False

                print("Reached Idol Destination - Posn: "+str(self.position))

            elif self.position!=posn_num and self.idol_moving==False:
                self.game.coils.wheelMotor.pulse(0)
                self.idol_moving=True
                
                print("First Reported Idol Position was: "+str(self.position))


#            if self.idol_moving:
#                self.delay(name='mtp_repeat', event_type=None, delay=0, handler=self.move_to_posn, param=posn_num)

                
            
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

              
            elif self.idol_state=='no_lock':
                self.move_to_posn(4)
                if self.position==4 and self.idol_moving==False and self.release==False:
                    self.game.coils.idolRelease.pulse(150)
                    self.release = True
                    self.delay(name='move_posn', event_type=None, delay=3, handler=self.set_state, param='initialise')


            elif self.idol_state=='lock':
                self.next_lock_posn()
                        
            elif self.idol_state=='release':
                self.next_posn()
                if self.idol_moving==False and self.release==False:
                    self.game.coils.idolRelease.pulse(150)
                    self.release = True
                        

        def set_state(self,value):
            self.idol_state=value



        def empty(self):
            self.set_state('empty')

        def lock(self):
            self.set_state('lock')

        def lock_release(self):
            self.set_state('release')

        def hold(self):
            self.set_state('lock')

        def home(self):
            print("Moving To Home Position")
            self.set_state('initialise')


        def next_lock_posn(self):
#            if self.position==1 or self.position==2:
#                self.move_to_posn(3)
#            elif self.position==3 or self.position==4:
#                self.move_to_posn(5)
#            elif self.position==5 or self.position==6:
#                self.move_to_posn(1)

            if self.balls_in_idol==1:
                self.delay(name='move_posn', event_type=None, delay=1.5, handler=self.move_to_posn, param=3)
            elif self.balls_in_idol==2:
                self.delay(name='move_posn', event_type=None, delay=1.5, handler=self.move_to_posn, param=5)
            elif self.balls_in_idol==3:
                pass
                
#        def next_release_posn(self):
#            if self.position==1 or self.position==2:
#                self.move_to_posn(4)
#            elif self.position==3 or self.position==4:
#                self.move_to_posn(6)
#            elif self.position==5 or self.position==6:
#                self.move_to_posn(2)

        def next_posn(self):
            if self.next_posn_set==False:

                if self.position<6:
                    self.next_posn_num+=1
                else:
                    self.next_posn_num=1

                self.next_posn_set=True


            self.move_to_posn(self.next_posn_num)
           

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


        def check_popper(self):
            if self.balls_in_idol<3 and self.game.switches.rightPopper.is_active():
                self.game.coils.ballPopper.pulse(50)
            elif self.balls_in_idol==3 and self.game.switches.rightPopper.is_active():
                self.lock_release()


        #idol upkicker
        def sw_rightPopper_active_for_500ms(self, sw):
            self.check_popper()
        
#        def sw_rightPopper_inactive(self, sw):
#            if self.game.switches.subwayLockup.is_active():
#                self.game.coils.subwayRelease.pulse(30)


        #subway

        #subway entrance needs using

        def sw_subwayLockup_active(self, sw):
            #self.idol_state='lock'
            if self.game.switches.rightPopper.is_inactive():
                self.game.coils.subwayRelease.pulse(100)
        
#        def sw_subwayLockup_inactive(self, sw):
#            pass

        def update_trough(self):
            self.game.trough.num_balls_locked = self.balls_in_idol
            print("Balls in Idol: "+str(self.balls_in_idol))
           

        #idol entrance
        def sw_topIdolEnter_active(self, sw):
             self.balls_in_idol+=1
             self.update_trough()


#        def sw_topIdolEnter_time_since_change_500ms(self, sw):
#            self.balls_in_idol+=1
#            if self.idol_state !='empty':
#                if self.balls_in_idol>3:
#                   self.set_state('release_single')
#                elif self.lock_lit==False:
#                    self.set_state('no_lock')
#                else:
#                    self.set_state('lock')

#        def sw_topIdolEnter_inactive(self, sw):
#            if self.game.switches.subwayLockup.is_active():
#                self.game.coils.subwayRelease.pulse(20)


        def sw_exitIdol_active(self, sw):
            if self.game.ball>0:
                self.balls_in_idol-=1
                self.update_trough()
                self.game.trough.num_balls_in_play +=1
                self.check_popper()
                self.game.sound.play("ball_release")


        def sw_buyInButton_active_for_500ms(self, sw):
            self.idol_state='empty'


