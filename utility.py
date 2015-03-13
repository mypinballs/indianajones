# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"

class Utility(game.Mode):

	def __init__(self, game):
            super(Utility, self).__init__(game, 5)

            self.log = logging.getLogger('ij.utility')
            self.game.sound.register_sound('elephant_alert', sound_path+"elephant.aiff")

        def ball_missing(self):
            text_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)

            multiple = ''
            balls_missing = self.game.num_balls_total - self.game.num_balls()
            if balls_missing>1:
                multiple='s'
            text_layer.set_text(str(balls_missing)+" BALL"+multiple+" MISSING",1.5,5)#on for 1.5 seconds 5 blinks
            self.layer = text_layer
            self.game.sound.play('elephant_alert')


        def release_stuck_balls(self):
            #Release Stuck Balls code

            total_balls = self.game.trough.num_balls()+self.game.trough.num_balls_locked
            if total_balls<self.game.num_balls_total:

                self.log.info('Trough is full::%s',self.game.trough.is_full())
                self.log.info('Balls in trough::%s',self.game.trough.num_balls())
                self.log.info('Subway Switch::%s',self.game.switches.subwayLockup.is_active())
                self.log.info('Popper Switch::%s',self.game.switches.rightPopper.is_active())
                self.log.info('Balls Locked::%s',self.game.trough.num_balls_locked)

                if self.game.switches.leftEject.is_active():
                    self.game.coils.leftEject.pulse()

                #popper
                if self.game.switches.rightPopper.is_active():
                    self.game.coils.ballPopper.pulse(50)

                #subway
                if self.game.switches.subwayLockup.is_active():
                    self.game.coils.subwayRelease.pulse()

                #reset drops
                if self.game.switches.dropTargetLeft.is_active() or self.game.switches.dropTargetMiddle.is_active() or self.game.switches.dropTargetRight.is_active():
                    self.game.coils.centerDropBank.pulse(100)

                if self.game.switches.singleDropTop.is_active():
                    self.game.coils.totemDropUp.pulse()

                #check shooter lane
                if self.game.switches.shooterLane.is_active():
                    self.game.coils.ballLaunch.pulse()

                if self.game.switches.topPost.is_active():
                    self.game.coils.topLockupMain.pulse()
                    self.game.coils.topLockupHold.pulse(200)

                self.delay(name='release_stuck_balls_loop', event_type=None, delay=5, handler=self.release_stuck_balls)
            else:
                self.cancel_delayed('release_stuck_balls_loop')


        def pause_game(self,active=True):
            self.game.paused = active
            self.game.enable_flippers(True) #update flipper rules
            
            if active:
                self.game.sound.pause()
                #self.game.coils.flipperLwRHold.enable()
                self.game.effects.drive_flasher('flasherPlaneGuns','fast')
                self.game.ball_search.disable()
                
            else:
                self.game.sound.un_pause()
                #self.game.coils.flipperLwRHold.disable()
                self.game.effects.drive_flasher('flasherPlaneGuns','off')
                self.game.ball_search.enable()