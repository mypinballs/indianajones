# Mini Playfield Logic

__author__="jim"
__date__ ="$Dec 22, 2010 3:01:38 PM$"

import procgame
import locale
from procgame import *
from random import *

base_path = "/Users/jim/Documents/Pinball/p-roc/p-roc system/src/"
game_path = base_path+"games/indyjones/"

class Hand_Of_Fate(game.Mode):

	def __init__(self, game, priority):
            super(Hand_Of_Fate, self).__init__(game, priority)
            
            self.text_layer1 = dmd.TextLayer(128/2, 2, self.game.fonts['tiny7'], "center", opaque=False)
            self.text_layer2 = dmd.TextLayer(128/2, 10, self.game.fonts['tiny7'], "center", opaque=False)
            self.text_layer3 = dmd.TextLayer(128/2, 18, self.game.fonts['tiny7'], "center", opaque=False)
            self.text_layer4 = dmd.TextLayer(128/2, 27, self.game.fonts['tiny7'], "center", opaque=False)

            self.list =['Lite Extra Ball','Dog Fight Hurry Up','Eternal Life','Bonus X','10 Million','20 Million','Super Jets','Lock Ball','Lite POA','Loop Person','Quick Multi-Ball']
            
            self.reset()


        def reset(self):
            self.status = "off"
            self.countdown=20
            self.chosen_list = ['','','','']


        def mode_started(self):
            pass

        
        def mode_ended(self):
            pass
        

        def get_status(self,value):
            self.status=value
            return True

        def set_status(self,value):
            self.status=value
            self.update_lamps()


        def update_lamps(self):
            if self.status=='lit':
                self.game.drive_lamp('handOfFate','fast')
                self.game.lamps.gi05.disable()
            elif self.status=='ready':
                self.game.lamps.gi05.pulse(0)
            elif self.status=='off':
                self.game.lamps.gi05.disable()
                self.game.drive_lamp('handOfFate','off')


        def ready(self):
            
            if self.countdown>0:
                self.set_status('ready')
                self.countdown-=1
                self.delay(name='counter', event_type=None, delay=1, handler=self.ready)
            else:
                self.clear()


            self.update_lamps()
            

        def feature(self):
            if self.status=='lit':
                self.animation()
            else:
                self.eject()


        def animation(self):
            #time = 2
            anim = dmd.Animation().load(game_path+"dmd/hand_of_fate.dmd")
            hof_animation_1 = dmd.AnimatedLayer(frames=anim.frames,hold=False)
            hof_animation_1.add_frame_listener(-1, self.choices)
            self.layer = hof_animation_1
            #self.delay(name='callback', event_type=None, delay=time, handler=self.choices)

#        def animation2(self):
#            anim = dmd.Animation().load(game_path+"dmd/hand_of_fate.dmd")
#            self.layer = dmd.AnimatedLayer(frames=anim.frames,hold=False)


        def choices(self):

            #set time to show choices
            time=4
            #shuffle the possible selections
            shuffle(self.list)

            #set the choice
            self.chosen_list = [self.list[0],self.list[1],self.list[2],self.list[3]]
            print(self.list[0]+", "+self.list[1]+", "+self.list[2]+", "+self.list[3])
            
            #display the choice
            choice_bgnd = dmd.Animation().load(game_path+"dmd/hof_choose.dmd")
            self.choices_bgnd_layer = dmd.AnimatedLayer(frames=choice_bgnd.frames,opaque=False,hold=False)
            self.text_layer1.set_text(self.list[0],seconds=time)
            self.text_layer2.set_text(self.list[1],seconds=time)
            self.text_layer3.set_text(self.list[2],seconds=time)
            self.text_layer4.set_text(self.list[3],seconds=time)
            
            choices_layer = dmd.GroupedLayer(128, 32, [self.text_layer1,self.text_layer2,self.text_layer3,self.text_layer4,self.choices_bgnd_layer])
            choices_layer.transition = dmd.ExpandTransition(direction='vertical')
            self.layer = choices_layer


            #set the callback to next section
            self.delay(name='callback', event_type=None, delay=time, handler=self.chosen)


        def chosen(self):

            #time to show chosen award
            time=3
            #shuffle possible choices
            shuffle(self.chosen_list)

            #display the award chosen
            chosen_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)
            chosen_layer.transition = dmd.ExpandTransition(direction='vertical')
            chosen_layer.set_text(self.chosen_list[0],seconds=time,blink_frames=10)
            self.layer = chosen_layer

            #award logic
            self.award(self.chosen_list[0])

            #set the callback to eject ball
            self.delay(name='callback', event_type=None, delay=time, handler=self.eject)

        def award(self,option):
            #this is where we will add the awards logic
            if option==self.list[4]: #10 mil
                self.game.score(10000000)
            elif option==self.list[5]: #20 mil
                self.game.score(20000000)

        def clear(self):
            self.set_status('off')
            self.layer = None
            self.update_lamps()

        def eject(self):
            self.game.coils.leftEject.pulse(30)
            self.clear()
            
        def sw_leftEject_active_for_500ms(self,sw):
            self.feature()

        def sw_leftInlane_active(self,sw):
            if self.get_status('ready'):
                self.set_status('lit')

        def sw_rightInlane_active(self,sw):
            if self.get_status('ready'):
                self.set_status('lit')