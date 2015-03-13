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
            self.stored_posn =0
            self.balls_in_idol = 0
            self.balls_in_play = 0
            self.ball_max = 3 #make this a game setting
            self.idol_state="initialise"
            self.idol_moving = False
            self.balls_waiting = False
            
            #self.release= False
            self.lock_lit = False
            self.next_posn_set=False
            self.next_posn_num=0
            self.lock_ready_flag = False
            self.complete = True
            self.stored_state = None
            
            #subway tracking vars
            self.balls_in_subway = 0
            self.subway_active=False
            self.subway_coil_fired = False
            

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


        def move_to_posn(self,posn_num,delay=0,callback1=None,callback2=None,delay1=0,delay2=0):
            
            if self.position==posn_num and self.idol_moving:
                self.game.coils.wheelMotor.disable()
                self.idol_moving =False
                #self.game.set_status("Position: "+str(self.position))
                #self.release=False
                #if self.game.switches.rightPopper.is_inactive(): #don't reset state if ball waiting in popper
                self.idol_state='idle'
                #self.next_posn_num=self.position
                #self.next_posn_set=False
                self.stored_posn = self.position

                #callback once at position
                self.callback1=callback1
                self.callback2=callback2
                if self.callback1:
                    #self.cancel_delayed('callback_delay1')
                    self.delay(name='callback_delay1', event_type=None, delay=delay1, handler=self.callback1)
                else:
                    self.complete = True
                if self.callback2:
                    #self.cancel_delayed('callback_delay2')
                    self.delay(name='callback_delay2', event_type=None, delay=delay2, handler=self.callback2)

                #log posn
                self.log.info("Reached Idol Destination - Posn: "+str(self.position))

            elif self.position!=posn_num and self.idol_moving==False:
                #self.game.coils.wheelMotor.enable()
                #self.cancel_delayed('motor_on_delay')
                self.delay(name='motor_on_delay', event_type=None, delay=delay, handler=self.game.coils.wheelMotor.enable)
                self.idol_moving=True
                self.complete = False
                
                self.log.info("Idol Moving To Position:"+str(posn_num)+" From Posn:"+str(self.position)+" With Delay:"+str(delay))

         
        def idol_control(self):
            
            if self.idol_state=='initialise':
                self.move_to_posn(1)
                
            elif self.idol_state=='empty':
                self.move_to_posn(posn_num=2,callback1=self.ball_release,callback2=lambda:self.set_state('empty2'),delay2=2)
                
            elif self.idol_state=='empty2':
                self.move_to_posn(posn_num=4,callback1=self.ball_release,callback2=lambda:self.set_state('empty3'),delay2=2)

            elif self.idol_state=='empty3':
                self.move_to_posn(posn_num=6,callback1=self.ball_release,callback2=lambda:self.set_state('initialise'),delay2=2)

            elif self.idol_state=='lock':
                if self.balls_in_idol==1:
                    self.move_to_posn(posn_num=3,delay=1)
                elif self.balls_in_idol==2:
                    self.move_to_posn(posn_num=5,delay=1)
                elif self.balls_in_idol==3:
                    #self.idol_state='idle'
                    self.move_to_posn(posn_num=1,delay=1)
                        
            elif self.idol_state=='relock': #- for 4th bal lock only - release a ball then pick up extra one to maintain max 3 in idol

                #work out position for release
                posn = self.next_posn()
                #move to set posn and callback for ball release & next stage of relock
                self.move_to_posn(posn_num=posn,callback1=self.ball_release,callback2=lambda:self.set_state('half_turn'),delay2=0.5)

            elif self.idol_state=='half_turn': #for 4th ball lock only

                #move half way to pick up waiting ball, then callback as complete
                #check this works!
                posn = self.next_posn()
                for i in range(2):
                    if posn<6:
                        posn+=1
                    else:
                        posn=1

                self.move_to_posn(posn_num=posn)

            elif self.idol_state=='nolock':

                #move 3 posns - 2 from the initial move then callback release for move+1,eject,move+1
                if self.balls_in_idol==1:

                    posn = self.next_posn()
                    for i in range(1):
                        if posn<6:
                            posn+=1
                        else:
                            posn=1

                    self.move_to_posn(posn_num=posn,delay=1,callback1=self.release)

              
            elif self.idol_state=='hold':
                hold_time = 10

                # +2 to stored posn
                posn = self.next_posn()
                if posn<6:
                    posn+=1
                else:
                    posn=1

                if self.balls_in_idol==1:
                    self.move_to_posn(posn_num=3,delay=1,callback1=self.relock,delay1=hold_time)
                elif self.balls_in_idol==2:
                    self.move_to_posn(posn_num=5,delay=1,callback1=self.relock,delay1=hold_time)
                elif self.balls_in_idol==3:
                    self.move_to_posn(posn_num=1,delay=1,callback1=self.relock,delay1=hold_time)
                    #self.relock()


            elif self.idol_state=='release': #used with hold or after a ball is locked only
                #move to +1 posn
                #callback to release ball no delay
                #callback t0 move to +1 posn after 1sec delay
                posn = self.next_posn()
                self.log.info("Calculated Posn Data, Posn is:%s",posn)
                self.move_to_posn(posn_num=posn,callback1=self.ball_release,callback2=lambda:self.set_state('advance'),delay2=0.5)

            elif self.idol_state=='advance': #move +1 position
                posn = self.next_posn()
                self.log.info("Calculated Posn Data, Next Posn is:%s",posn)
                self.move_to_posn(posn_num=posn)

        def ball_release(self):
            self.log.info("Ball Release")
            self.game.coils.idolRelease.pulse(150)
            if self.game.ball>0:
                self.game.sound.play("ball_release")

        def next_posn(self):
            next_num = self.stored_posn
            if next_num<6:
                next_num+=1
            else:
                next_num=1

            return next_num

        def set_state(self,value):
            self.idol_state=value

        def set_stored_state(self,value):
            self.stored_state=value

        def empty(self):
            self.set_state('empty')

        def lock(self):
            #self.set_state('lock')
            if self.complete:
                self.set_state('lock')

            self.set_stored_state('lock')

        def relock(self): 
            self.set_state('relock')

        def release(self): 
            self.set_state('release')

        def hold(self):
            #self.set_state('hold')
            #self.stored_state = 'hold'
            if self.complete:
                self.set_state('hold')

            self.set_stored_state('hold')

        def nolock(self):
            if self.complete: #set state if idol moves are complete
                self.set_state('nolock')

            self.set_stored_state('nolock') # always store the state in case balls get held in popper


        def home(self):
            self.log.info("Moving To Home Position")
            self.set_state('initialise')
           

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
            #setup repeat
            self.delay(name='check_popper_repeat', event_type=None, delay=0.5, handler=self.check_popper)

            if self.game.switches.rightPopper.is_active() and self.complete:
                if self.balls_in_subway>0: #record the sucessfull movement of a ball out of subway
                    self.balls_in_subway-=1 
                self.subway_coil_fired = False #reset subway fired flag

                if self.balls_in_idol<3:
                    #kick the ball
                    self.game.coils.ballPopper.pulse(50)
                    #restore the state if ball has been waiting in nolock mode
                    if self.stored_state!=None:
                        self.idol_state = self.stored_state
                    #cancel repeat if ball kicked
                    self.cancel_delayed('check_popper_repeat')
                elif self.balls_in_idol==3 and self.game.get_player_stats('multiball_started')==False:
                    #start the relock process
                    self.relock()

            

        def subway_logic(self):
            self.subway_active=True
            self.log.debug('Subway Logic is running, Balls:%s Subway Lock SW:%s',self.balls_in_subway,self.game.switches.subwayLockup.is_active())
            #debug_ball_data = "BIS:"+str(self.balls_in_subway)+" SUBWAY SW:"+str(self.game.switches.subwayLockup.is_active())
            #self.game.set_status(debug_ball_data)
            
            if self.balls_in_subway >0:
                #check for settled ball and no ball in popper
                if self.game.switches.subwayLockup.is_active() and self.game.switches.rightPopper.is_inactive():
                    self.game.coils.subwayRelease.pulse()
                    self.subway_coil_fired = True
                
                #check if ball got caught by subway release
                elif self.subway_coil_fired and self.game.switches.rightPopper.is_inactive(): 
                    self.game.coils.subwayRelease.pulse(50)
                    
                self.delay(name='subway_logic_repeat', delay=1, handler=self.subway_logic)
            else:
                self.cancel_delayed('subway_logic_repeat') #cancel subway check repeat
                self.log.debug('Subway Logic is stopped, Balls:%s',self.balls_in_subway)
                self.subway_active=False
                self.subway_coil_fired = False
                

        #idol upkicker
        def sw_rightPopper_active_for_500ms(self, sw):
            self.check_popper()
        
        


        #subway
#        def sw_subwayLockup_active(self, sw):
#            #check for clear path
#            self.log.info("Subway Active")
#            if self.game.switches.rightPopper.is_inactive():
#                self.game.coils.subwayRelease.pulse()

        def sw_centerEnter_active(self, sw):
            if self.game.ball>0 or len(self.game.players)>0:
                self.balls_in_subway+=1
                if not self.subway_active:
                    self.subway_logic() #start the subway logic
            

        def update_ball_tracking(self,num):
            self.game.trough.num_balls_locked = self.balls_in_idol
            self.game.trough.num_balls_in_play +=num
            self.log.info("Balls in Idol: "+str(self.balls_in_idol))
           

        #idol entrance
        def sw_topIdolEnter_active(self, sw):
            if self.game.ball>0 or len(self.game.players)>0:
                self.balls_in_idol+=1
                self.update_ball_tracking(-1)


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
            if self.game.ball>0 or len(self.game.players)>0:
                self.balls_in_idol-=1
                self.update_ball_tracking(1)
                self.check_popper()
                


        #hidden debug button combination
        def sw_buyInButton_active_for_250ms(self, sw):
            if self.game.switches.gunTrigger.is_active(0.5):
                self.idol_state='empty'
            elif self.game.switches.flipperLwL.is_active(0.5):
                self.game.coils.subwayRelease.pulse()
