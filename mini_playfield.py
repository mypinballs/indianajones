# Mini Playfield Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:38 PM$"

import procgame
import locale
import random
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Mini_Playfield(game.Mode):

	def __init__(self, game, priority):
            super(Mini_Playfield, self).__init__(game, priority)

            self.log = logging.getLogger('ij.miniPlayfield')

            #setup sound calls
            self.game.sound.register_sound('poa_lane_lit', sound_path+'poa_lane_lit.aiff')
            self.game.sound.register_sound('poa_lane_unlit', sound_path+'poa_lane_unlit_1.aiff')
            self.game.sound.register_sound('poa_lane_unlit', sound_path+'poa_lane_unlit_2.aiff')
            self.game.sound.register_sound('poa_lane_unlit', sound_path+'poa_lane_unlit_3.aiff')
            self.game.sound.register_sound('falling_scream', sound_path+'falling_scream.aiff')

            self.reset()

        def reset(self):
            self.list = ['miniTopLeft','miniTopRight','miniMiddleTopLeft','miniMiddleTopRight','miniMiddleBottomLeft','miniMiddleBottomRight','miniBottomLeft','miniBottomRight','miniTopArrow','miniBottomArrow']
            self.lamp_flag = [False,False,False,False,False,False,False,False,False,False]

            self.level = 1
            #self.lamps = 2
            self.level_completed = False
            self.lamps_to_go = 0
            self.adv_sequence_num = 0
            self.pit_value_active = False
            self.extra_ball_active = False

            self.lane_lit_value = 5000000 
            self.lane_unlit_value = 100000
            self.poa_lane_anim = "dmd/5_million.dmd"

            self.loop = 0
            self.status = 'initialise'
            self.game_status = 'initialise'

            #playfield param setup
            self.position =None

            if self.game.switches.miniLeftLimit.is_active():
                self.set_posn('left')
            elif self.game.switches.miniRightLimit.is_active():
                 self.set_posn('right')
            else:
                self.set_posn('unknown')

            self.dirn_time = 150 #default timing for movement
            self.centre_time = self.dirn_time/2
            self.calibrated_dirn_time = 0
            self.calibrated_centre_time = 0
            self.dirn_time_count = 0

            self.motor_off()


        def mode_started(self):
            self.log.info("Mini Playfield Mode Started")
            self.log.info("MP Position is:"+str(self.position))

            #setup mechanism
            #self.game.set_status(self.position)
            #self.check_switches()
            #self.centre_playfield()
            self.calibrate(6)
            #self.game.coils.miniMotorRight.pulse(self.centre_time)
            #self.game.coils.miniMotorLeft.pulse(self.centre_time)

        def get_status(self):
            return self.game_status
        
        def path_sequence(self,level=None):

            self.game_status='mode'
            self.cancel_delayed('path_timeout')
            self.reset_lamps()

            #special setter - pass in level directly for use by other modes
            if level !=None:
                self.level=level

            #set level and sequence
            if self.level_completed or self.level==0:
                self.level+=1
                self.level_completed = False;

            if self.level<=3:

                #setup num of lamps to put out
                self.lamps_to_go = self.level+1
                
                #create random lamp sequences
                sequence = [0,1,2,3,4,5,6,7]
                random.shuffle(sequence)
                lamp_number=0

                for i in range(self.lamps_to_go):
                    self.game.effects.drive_lamp(self.list[sequence[lamp_number]],'medium')
                    print("Lamp chosen "+self.list[sequence[lamp_number]])
                    self.lamp_flag[sequence[lamp_number]]=True
                    lamp_number+=1

            else:
                self.adv_path_sequence()


            if self.level%2==0:
                 self.game.effects.drive_lamp(self.list[9],'medium')
                 self.lamp_flag[9]=True
                 self.extra_ball_active = True

            if self.level>=3:
                 self.game.effects.drive_lamp(self.list[8],'medium')
                 self.lamp_flag[8]=True
                 self.pit_value_active = True

        def adv_path_sequence(self):
            self.reset_lamps()

            if self.adv_sequence_num>6:
                self.adv_sequence_num=0

            lamp_number = random.randint(self.adv_sequence_num, self.adv_sequence_num+1)
            self.log.info("Lamp chosen "+self.list[lamp_number])
            self.game.effects.drive_lamp(self.list[lamp_number],'medium')
            self.lamp_flag[lamp_number]=True

            move_delay = 3-self.level*0.3
            if move_delay<=0.3:
                move_delay=0.3

            self.adv_sequence_num+=2

            self.delay(name='path_timeout', event_type=None, delay=move_delay, handler=self.adv_path_sequence)

            return

        def sts_path_sequence(self,num):
            #method for steal the stones, not used for and does not count against poa progress
            
            self.game_status='mode'
            self.reset_lamps()

            #create random lamp sequences
            sequence = [0,1,2,3,4,5,6,7]
            random.shuffle(sequence)
            lamp_number=0

            for i in range(num):
                self.game.effects.drive_lamp(self.list[sequence[lamp_number]],'medium')
                print("Lamp chosen "+self.list[sequence[lamp_number]])
                self.lamp_flag[sequence[lamp_number]]=True
                lamp_number+=1
        

        def inc_pit_value(self):
            pit_value = self.game.get_player_stats('pit_value') + self.lane_lit_value+(1000000*self.level)
            self.game.set_player_stats('pit_value',pit_value)

        def pit_collected(self):
            self.text_layer1.set_text("PIT COLLECTED")
            self.text_layer2.set_text(locale.format("%d",self.game.get_player_stats('pit_value'),True),blink_frames=20)



        def path_ended(self):

            self.game_status ='idle'
            self.cancel_delayed('path_timeout')
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

        def clear(self):
            self.layer = None

        def set_posn(self,dirn):
            self.position=dirn;
            #debug
            #self.log.info(dirn)
            

        def centre_playfield(self):

            if self.status !='broken':
                if self.position=='left':
                    self.game.coils.miniMotorRight.pulse(self.centre_time)
                elif self.position=='right':
                    self.game.coils.miniMotorLeft.pulse(self.centre_time)

                self.set_posn('unknown') #reset position value
                self.delay(name='set_posn', event_type=None, delay=self.centre_time, handler=self.set_posn, param='centre')


        def motor_on(self,dirn):
            
            if self.status !='broken':
                if dirn=='left' and self.position!='left':
                    self.game.coils.miniMotorLeft.pulse(self.dirn_time)
                    self.set_posn('unknown') #reset position value
                    self.delay(name='set_posn', event_type=None, delay=self.dirn_time, handler=self.set_posn, param=dirn)

                elif dirn=='right'and self.position!='right':
                    self.game.coils.miniMotorRight.pulse(self.dirn_time)
                    self.set_posn('unknown') #reset position value
                    self.delay(name='set_posn', event_type=None, delay=self.dirn_time, handler=self.set_posn, param=dirn)

                else: #safety catch
                    self.motor_off()
                



        def motor_off(self):
            self.game.coils.miniMotorLeft.disable()
            self.game.coils.miniMotorRight.disable()
            self.motor_dirn='off'
            self.cancel_delayed('set_posn')



        def calibrate(self,num=6):


            if self.position!='unknown':
                time1 = 0
                time2 = 0
                dirn_time =0

                if self.game.switches.miniLeftLimit.last_changed !=None:
                    time1 = self.game.switches.miniLeftLimit.last_changed*100
              
                if self.game.switches.miniRightLimit.last_changed !=None:
                    time2 = self.game.switches.miniRightLimit.last_changed*100

                self.log.info("Time 1:"+str(time1))
                self.log.info("Time 2:"+str(time2))

                if time1>time2:
                    dirn_time = time1-time2
                elif time2>time1:
                    dirn_time = time2-time1

                self.dirn_time_count += dirn_time
                self.log.info("Posn Time is:"+str(dirn_time))


            if self.loop<num: #self.loop_num:
                self.log.info("Mini Playfield Position is:"+str(self.position))

                if self.loop%2!=0:#odd
                    self.motor_on('left')
                else:
                    self.motor_on('right')

                self.loop+=1
                self.delay(name='calibration_loop', event_type=None, delay=0.2, handler=self.calibrate)#change time here to slow calibration

            else:
                self.calibrated_dirn_time = self.dirn_time_count/num
                self.calibrated_centre_time = self.calibrated_dirn_time/2
                
                self.log.info("Calibrated Full Posn Time is:"+ str(self.calibrated_dirn_time))
                self.log.info("Calibrated Centre Posn Time is:"+ str(self.calibrated_centre_time))
                
                self.centre_playfield()


        def check_switches(self):

            if self.game.switches.miniLeftLimit.is_active() and self.game.switches.miniRightLimit.is_active():
                self.status='broken'
            else:
                self.status='working'


        def sw_flipperLwL_active(self,sw):
            if self.game_status =='mode':
                self.cancel_delayed('centre_timeout')
                self.motor_on('left')
            

        def sw_flipperLwR_active(self,sw):
            if self.game_status  =='mode':
                self.cancel_delayed('centre_timeout')
                self.motor_on('right')


        def sw_flipperLwL_inactive(self,sw):
            if self.game_status  =='mode' or self.game_status  =='countdown':
                self.delay(name='centre_timeout', event_type=None, delay=5, handler=self.centre_playfield)

            
        def sw_flipperLwR_inactive(self,sw):
            if self.game_status  =='mode' or self.game_status  =='countdown':
                self.delay(name='centre_timeout', event_type=None, delay=5, handler=self.centre_playfield)
            


        def sw_miniLeftLimit_active(self,sw):
            self.log.info("left limit")
            self.set_posn('left')
            self.motor_off()

        def sw_miniRightLimit_active(self,sw):
            self.log.info("right limit")
            self.set_posn('right')
            self.motor_off()

            

        def sw_miniTopHole_active(self, sw):

            if self.game_status=='mode':
                if self.pit_value_active:

                    self.game.score(self.game.get_player_stats('pit_value'))

                    anim = dmd.Animation().load(game_path+"dmd/pit_collected.dmd")
                    self.text_layer1 = dmd.TextLayer(128/2, 2, self.game.fonts['num_09Bx7'], "center", opaque=False)
                    self.text_layer2 = dmd.TextLayer(128/2, 15, self.game.fonts['18x12'], "center", opaque=False)
                    self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,frame_time=2)
                    self.animation_layer.add_frame_listener(-1,self.pit_collected)
                    self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer1,self.text_layer2])
                    self.delay(name='clear', event_type=None, delay=5, handler=self.clear)

                    self.game.sound.play('pit_collected')

                    #self.game.poa.reset_pit_value()
                    
                else:
                    #play fall anim
                    anim = dmd.Animation().load(game_path+"dmd/poa_fall.dmd")
                    self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,frame_time=2)
                    self.layer.add_frame_listener(-1,self.clear)
                    self.game.sound.play('falling_scream')
                 
                self.game.enable_flippers(enable=True)
                self.game_status = 'countdown'

        def sw_miniBottomHole_active(self, sw):

            if self.game_status=='mode':
                if self.extra_ball_active:
                     self.game.extra_ball.collect()
                else:
                    #play fall anim
                    anim = dmd.Animation().load(game_path+"dmd/poa_fall.dmd")
                    self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,frame_time=2)
                    self.layer.add_frame_listener(-1,self.clear)
                    self.game.sound.play('falling_scream')

                self.game.enable_flippers(enable=True)
                self.game_status = 'countdown'


        def lanes(self,id):
            
           if self.game_status=='mode':
               
                if self.lamp_flag[id] == True:

                    self.lamp_flag[id]=False;
                    self.game.effects.drive_lamp(self.list[id],'off')
                    self.lamps_to_go -=1
                    self.inc_pit_value()

                    if self.lamps_to_go==0:
                        self.level_completed = True
                        self.path_sequence()

                    #score
                    self.game.score(self.lane_lit_value)
                
                    #play anim
                    anim = dmd.Animation().load(game_path+self.poa_lane_anim)
                    self.layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=2)
                    self.delay(name='clear', event_type=None, delay=1, handler=self.clear)

                    #play sounds
                    self.game.sound.play('poa_lane_lit')

                else:
                    self.game.score(self.lane_unlit_value)
                    #play sounds
                    self.game.sound.play('poa_lane_unlit')


        def sw_miniTopLeft_active(self, sw):
            self.lanes(0)

        def sw_miniTopRight_active(self, sw):
            self.lanes(1)

        def sw_miniMiddleTopLeft_active(self, sw):
            self.lanes(2)

        def sw_miniMiddleTopRight_active(self, sw):
            self.lanes(3)

        def sw_miniMiddleBottomLeft_active(self, sw):
            self.lanes(4)

        def sw_miniMiddleBottomRight_active(self, sw):
            self.lanes(5)

        def sw_miniBottomLeft_active(self, sw):
            self.lanes(6)
            self.game.enable_flippers(enable=True)
            self.game_status = 'countdown'

        def sw_miniBottomRight_active(self, sw):
            self.lanes(7)
            self.game.enable_flippers(enable=True)
            self.game_status = 'countdown'


        def sw_topPost_active(self,sw):
            if self.game.get_player_stats('multiball_started')==False and self.game.get_player_stats('quick_multiball_running')==False:
                self.game.enable_flippers(enable=False)
                #update game status
                self.game_status = 'mode'
            
