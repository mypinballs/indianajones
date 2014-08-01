# Mini Playfield Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:38 PM$"

import procgame
import locale
import logging
from procgame import *
from random import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Hand_Of_Fate(game.Mode):

	def __init__(self, game, priority, mode_select):
            super(Hand_Of_Fate, self).__init__(game, priority)

            self.log = logging.getLogger('ij.HandOfFate')
            
            self.text_layer1 = dmd.TextLayer(128/2, 8, self.game.fonts['tiny7'], "center", opaque=False)
            self.text_layer2 = dmd.TextLayer(128/2, 14, self.game.fonts['tiny7'], "center", opaque=False)
            self.text_layer3 = dmd.TextLayer(128/2, 20, self.game.fonts['tiny7'], "center", opaque=False)
            self.text_layer4 = dmd.TextLayer(128/2, 26, self.game.fonts['tiny7'], "center", opaque=False)

            self.game.sound.register_sound('hof_lit', sound_path+"hand_of_fate_1.aiff")
            self.game.sound.register_sound('hof_selected', sound_path+"hand_of_fate_2.aiff")


            self.list =['Lite Extra Ball','Dog Fight Hurry Up','Eternal Life','Bonus X','10 Million','20 Million','Super Jets','Lock Ball','Lite POA','Lite Loops','Spot Friend','Quick Multi-Ball']

            self.mode_select = mode_select
            self.reset()


        def reset(self):
            self.status = self.game.get_player_stats('hof_status')
            self.countdown=20
            self.chosen_list = ['','','','']


        def mode_started(self):
            self.ready()

        
        def mode_stopped(self):
            self.set_status('off')
        

        def get_status(self):
            value = self.game.get_player_stats('hof_status')
            return value

        def set_status(self,value):
            self.status=value
            self.game.set_player_stats('hof_status',self.status)
            self.update_lamps()


        def update_lamps(self):
            if self.status=='lit':
                self.game.drive_lamp('handOfFate','fast')
                self.game.lamps.gi05.disable()
            elif self.status=='ready':
                self.game.lamps.gi05.enable()
            elif self.status=='off':
                self.game.lamps.gi05.disable()
                self.game.drive_lamp('handOfFate','off')


        def ready(self):
            self.set_status('ready')
            self.update_lamps()
            

        def feature(self):
            if self.status=='lit':
                self.animation()

            #mode select takes care of eject and other saucer functions

            #else:#if self.game.get_player_stats('mode_enabled')==False:
             #   self.eject()


        def animation(self):
            #time = 2
            anim = dmd.Animation().load(game_path+"dmd/hand_of_fate.dmd")
            hof_animation_1 = dmd.AnimatedLayer(frames=anim.frames,hold=False)
            hof_animation_1.add_frame_listener(-1, self.choices)
            self.layer = hof_animation_1

            self.game.sound.play('hof_lit')
            #self.delay(name='callback', event_type=None, delay=time, handler=self.choices)

#        def animation2(self):
#            anim = dmd.Animation().load(game_path+"dmd/hand_of_fate.dmd")
#            self.layer = dmd.AnimatedLayer(frames=anim.frames,hold=False)


        def choices(self):

            #set time to show choices
            time=3
            #shuffle the possible selections
            shuffle(self.list)

            #set the choice
            self.chosen_list = [self.list[0],self.list[1],self.list[2],self.list[3]]
            self.log.info(self.list[0]+", "+self.list[1]+", "+self.list[2]+", "+self.list[3])
            
            #display the choice
            bgnd_anim = dmd.Animation().load(game_path+"dmd/hof_choose.dmd")
            bgnd_layer = dmd.FrameLayer(frame=bgnd_anim.frames[0])
            
            self.text_layer1.set_text(self.list[0].upper())
            self.text_layer2.set_text(self.list[1].upper())
            self.text_layer3.set_text(self.list[2].upper())
            self.text_layer4.set_text(self.list[3].upper())
            
            choices_layer = dmd.GroupedLayer(128, 32, [bgnd_layer,self.text_layer1,self.text_layer2,self.text_layer3,self.text_layer4])
            #choices_layer.transition = dmd.ExpandTransition(direction='vertical')
            self.layer = choices_layer

            #set the callback to next section
            self.delay(name='chosen_delay', event_type=None, delay=time, handler=self.chosen)


        def chosen(self):

            #time to show chosen award
            time=3
            #shuffle possible choices
            shuffle(self.chosen_list)

            
            #award logic
            self.award(self.chosen_list[0])

            #play sound
            self.game.sound.play('hof_selected')


            #set the cleanup timer
            self.delay(name='end_delay', event_type=None, delay=time, handler=self.clear)

        def award(self,option):
            #this is where we will add the awards logic
            #debug
            #option=self.list[3]
            
            if option==self.list[0]:
                self.game.extra_ball.lit()
            elif option==self.list[2]:
                self.eternal_life_award(15)
            elif option==self.list[3]:
                self.bonusx_award()
            elif option==self.list[4]: #10 mil
                self.score_award(10000000)
            elif option==self.list[5]: #20 mil
                self.score_award(20000000)
            else:
                self.name_award()

        def eternal_life_award(self,timer):
            #display the animation
            anim = dmd.Animation().load(game_path+"dmd/eternal_life.dmd")
            self.layer = dmd.AnimatedLayer(frames=anim.frames,hold=False)
            self.game.sound.play('electricity')
            
            #start the ball saver
            self.game.ball_save.start(num_balls_to_save=1, time=timer, now=True, allow_multiple_saves=False)

        def name_award(self):
            #display the award chosen
            chosen_layer = dmd.TextLayer(128/2, 7, self.game.fonts['8x6'], "center", opaque=True)
            chosen_layer.set_text(self.chosen_list[0].upper(),blink_frames=2)
            #chosen_layer.transition = dmd.ExpandTransition(direction='vertical')
            self.layer = chosen_layer

            self.game.score(2000000)

        def bonusx_award(self):
            bonusx = self.game.get_player_stats('bonus_x')+1
            #display the award chosen
            chosen_layer = dmd.TextLayer(128/2, 7, self.game.fonts['8x6'], "center", opaque=True)
            chosen_layer.set_text('BONUS X'+str(bonusx),blink_frames=2)
            #chosen_layer.transition = dmd.ExpandTransition(direction='vertical')
            self.layer = chosen_layer

            self.game.score(2000000)
            self.game.set_player_stats('bonus_x',bonusx)

        def score_award(self,score):
            time=3
            value_layer = dmd.TextLayer(128/2, 4, self.game.fonts['23x12'], "center", opaque=True)
            value_layer.set_text(locale.format("%d",score,True),blink_frames=2)
            self.layer = value_layer

            self.game.score(score)


        def clear(self):
            #housekeepig
            self.set_status('off')
            self.layer = None
            self.update_lamps()

            #add a callback to mode select to continue logic - start any modes enabled
            self.mode_select.start_scene()

            #remove self
            self.game.modes.remove(self)


#        def eject(self):
#            self.game.coils.leftEject.pulse()
#            self.clear()
            
        def sw_leftEject_active_for_500ms(self,sw):
            if self.status=='lit':
                self.animation()
                #return procgame.game.SwitchStop

        def sw_leftInlane_active(self,sw):
            if self.status=='ready':
                self.set_status('lit')

        def sw_rightInlane_active(self,sw):
            if self.status=='ready':
                self.set_status('lit')