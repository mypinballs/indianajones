# Multiball Code
#
# This mode handles the ball lock count and the multiball features such as jackpots,how many balls are in play etc.
# All Idol functions are handles by the idol mode. The number of balls locked is not the same as the number of balls in the idol!

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


class Multiball(game.Mode):

	def __init__(self, game, priority):
            super(Multiball, self).__init__(game, priority)

            self.text_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)
            
            self.lock_animation_1 = "dmd/xxx.dmd"
            self.lock_animation_2 = "dmd/xxx.dmd"
            self.lock_animation_3 = "dmd/xxx.dmd"

            self.game.sound.register_sound('xxx', sound_path+"xxx.aiff")
            self.game.sound.register_music('multiball_play', music_path+"multiball.aiff")
            
            self.balls_needed = self.game.idol.ball_max
            self.balls_in_play = 1

            self.lock_lit = self.game.get_player_stats('lock_lit')
            self.mode_running = self.game.get_player_stats('mode_running')
            self.balls_locked = self.game.get_player_stats('balls_locked')
            self.multiball_running = self.game.get_player_stats('multiball_running')

            self.lock_ball_score = 500000
            self.jackpot_base = 25000000
            self.jackpot_boost = 20000000
            self.jackpot_value = self.jackpot_base
            self.jackpot_x = 1
            self.jackpot_collected = 0
            self.jackpot_lamps = ['arkJackpot','stonesJackpot','grailJackpot']
            self.super_jackpot_enabled = False
            self.super_jackpot_value = 100000000
            self.next_ball_ready = False
            
            self.reset()


        def reset(self):
            self.update_lamps()


        def mode_started(self):
            pass

        def mode_tick(self):
            pass


        def lock_ball(self):

            #up the balls locked count
            self.balls_locked +=1

            #self.game.trough.num_balls_locked = self.balls_locked #update trough mode regarding locked balls
            #self.game.idol.balls_in_idol = self.balls_locked #update idol mode regarding locked balls
            self.game.set_player_stats('balls_locked',self.balls_locked)

            #debug
            self.game.set_status("Lock "+str(self.balls_locked)) #debug

          
            #update idol state
            self.game.idol.lock()

            #animations
            anim = dmd.Animation().load(game_path+"dmd/lock_"+str(self.balls_locked)+".dmd")
            self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,frame_time=3)
            self.animation_layer.add_frame_listener(-1,self.clear)
            self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer])

            self.game.lampctrl.play_show('ball_lock', repeat=False,callback=self.game.update_lamps)#self.restore_lamps
            self.game.score(self.lock_ball_score)
                
            #reset drops after delay
            self.delay(name='reset_drops', event_type=None, delay=1, handler=self.reset_drops)

            if self.balls_locked==self.balls_needed:
                self.multiball_running = True;
                self.game.set_player_stats('multiball_running',self.multiball_running)
                #temp whilst no animation
                #self.multiball_start()
                self.animation_layer.add_frame_listener(-30, self.multiball_start)
            else:
                #temp whilst no animation
                #self.launch_next_ball()
                self.animation_layer.add_frame_listener(-30,self.launch_next_ball)

        def launch_next_ball(self):
                self.game.trough.launch_balls(1,stealth=True) #set stealth to true so balls in play does not increase from lock
                self.next_ball_ready = True
                self.game.ball_save.start(time=5)


        def multiball_start(self):
            #jackpot build
            #ball tracking

            #animations
            self.game.set_status("MULTIBALL!") #debug

            anim = dmd.Animation().load(game_path+"dmd/multiball_start.dmd")
            self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,frame_time=3)
            self.animation_layer.add_frame_listener(-1,self.delayed_clear)
            self.animation_layer.add_frame_listener(-1,self.game.idol.empty)
            self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer])

            self.game.lampctrl.play_show('ball_lock', repeat=False,callback=self.game.update_lamps)#self.restore_lamps
            self.game.score(self.lock_ball_score)

            #start multiball music
            self.game.sound.play_music('multiball_play', loops=-1)

            self.balls_locked=0  

            #empty idol
            #temp whilst no animation
            #self.delay(name='mt_loop', event_type=None, delay=3, handler=self.game.idol.empty)

            
            #turn on ball save
            self.game.ball_save.start(num_balls_to_save=3,allow_multiple_saves=True,time=10)

            #start tracking
            self.multiball_tracking()
    


        def multiball_tracking(self):
            self.balls_in_play = self.game.trough.num_balls_in_play

            #debug
            self.game.set_status(str(self.balls_in_play))

            #track end
            if self.balls_in_play==1:
                self.multiball_running=False
                self.game.set_player_stats('multiball_running',self.multiball_running)
                
                self.game.sound.stop_music()
                self.game.sound.play_music('general_play', loops=-1)

                #light jackpot if not collected during multiball otherwise cancel
                if self.jackpot_collected==0:
                    self.jackpot('lit')
                    self.delay(name='jackpot_timeout', event_type=None, delay=10, handler=self.jackpot, param='cancelled')
                else:
                    self.jackpot('cancelled')

                self.cancel_delayed('mt_loop')

            else:
                self.delay(name='mt_loop', event_type=None, delay=0, handler=self.multiball_tracking)

        def jackpot(self,status=None):

            #if self.multiball_running:
                if status=='lit':
                    self.game.coils.flasherLiteJackpot.disable()
                    self.game.coils.flasherJackpot.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
                    self.game.coils.divertorMain.pulse(50)
                    self.game.coils.divertorHold.pulse(0)
                    self.game.coils.topLockupMain.pulse(50)
                    self.game.coils.topLockupHold.pulse(0)
                elif status=='unlit':
                    self.game.coils.flasherLiteJackpot.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
                    self.game.coils.divertorHold.disable()
                    self.game.coils.topLockupHold.disable()
                elif status=='made':
                    self.game.coils.flasherJackpot.disable()
                    self.game.lampctrl.play_show('jackpot', repeat=False,callback=self.game.update_lamps)#self.restore_lamps

       #            anim = dmd.Animation().load(game_path+"dmd/lock_animation_"+self.balls_locked+".dmd")
       #            self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=2)
#                   self.animation_layer.add_frame_listener(-1,self.clear)
#                   self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer])

                    self.jackpot_x = self.game.idol.balls_in_idol+1

                    self.game.score(self.jackpot_value*self.jackpot_x)
                    self.jackpot_collected+=1
                    self.game.effects.drive_lamp(self.jackpot_lamps[self.jackpot_collected],'smarton')
                    if self.jackpot_collected==3:
                        self.super_jackpot()
                    else:
                        self.delay(name='reset_jackpot', event_type=None, delay=1, handler=self.jackpot, param='unlit')

                elif status=='cancelled':
                    self.game.coils.flasherLiteJackpot.disable()
                    self.game.coils.flasherJackpot.disable()
                    self.game.coils.divertorHold.disable()
                    self.game.coils.topLockupHold.disable()

        def super_jackpot(self):
            self.game.coils.flasherSuperJackpot.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.super_jackpot_enabled = True




        def lock_enabled(self):
            #temp add in rules for enabling lock
            self.lock_lit = True;
            self.game.idol.lock_lit=  self.lock_lit
            self.game.set_player_stats('lock_lit',self.lock_lit)

            self.update_lamps()
          

        
        def reset_drops(self):
            if self.game.switches.dropTargetLeft.is_active() or self.game.switches.dropTargetMiddle.is_active() or  self.game.switches.dropTargetRight.is_active():
                self.game.coils.centerDropBank.pulse(100)


        def update_lamps(self):
            if self.lock_lit:
                self.game.effects.drive_lamp('centerLock','medium')
            else:
                self.game.effects.drive_lamp('centerLock','off')


        def delayed_clear(self,timer=2):
            self.delay(name='clear_delay', event_type=None, delay=timer, handler=self.clear)
            
        def clear(self):
            self.layer = None


        def sw_dropTargetLeft_active(self, sw):
            self.lock_enabled()

        def sw_dropTargetMiddle_active(self, sw):
            self.lock_enabled()

        def sw_dropTargetRight_active(self, sw):
            self.lock_enabled()


        def sw_centerEnter_active(self, sw):
            if self.multiball_running==False and self.mode_running==False:
                self.lock_ball()
            elif self.multiball_running:
                self.game.idol.hold()
                self.jackpot_x+=1
            else:
                self.game.idol.lock_release()

        def sw_leftRampMade_active(self, sw):
            if self.multiball_running:
                self.jackpot('lit')
                self.game.score(500000)

        def sw_topPost_active(self, sw):
            if self.multiball_running:
                self.jackpot('made')

        def sw_leftRampEnter_active(self, sw):
            pass

        def sw_rightRampEnter_active(self, sw):
            pass

        #jackpot value increase
        def sw_leftEject_active(self, sw):
            self.jackpot_value+=2000000

        def sw_captiveBallFront_active(self, sw):
            self.jackpot_value+=5000000
            
        def sw_captiveBallBack_active(self, sw):
            self.jackpot_value+=10000000

        def sw_centerStandup_active(self, sw):
            self.jackpot_value+=1000000

        #start ball save for next ball after lock
        def sw_shooterLane_open_for_1s(self,sw):
            if self.next_ball_ready:

            	ball_save_time = 5
                self.game.ball_save.start(num_balls_to_save=1, time=ball_save_time, now=True, allow_multiple_saves=False)


