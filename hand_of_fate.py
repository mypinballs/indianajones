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
            self.text_layer1.composite_op='blacksrc'
            self.text_layer2 = dmd.TextLayer(128/2, 14, self.game.fonts['tiny7'], "center", opaque=False)
            self.text_layer2.composite_op='blacksrc'
            self.text_layer3 = dmd.TextLayer(128/2, 20, self.game.fonts['tiny7'], "center", opaque=False)
            self.text_layer3.composite_op='blacksrc'
            self.text_layer4 = dmd.TextLayer(128/2, 26, self.game.fonts['tiny7'], "center", opaque=False)
            self.text_layer4.composite_op='blacksrc'

            self.game.sound.register_sound('hof_lit', sound_path+"hand_of_fate_1.aiff")
            self.game.sound.register_sound('hof_selected', sound_path+"hand_of_fate_2.aiff")


            self.list =['Lite Extra Ball','Dog Fight Hurry Up','Eternal Life','Bonus X','10 Million','20 Million','Super Jets','Lock Ball','Lite POA','Lite Loops','Spot Friend','Quick Multi-Ball']

            self.mode_select = mode_select
            self.reset()
            
            #mode links
            self.advance_bonusx = None


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
                self.choices()
                

            #mode select takes care of eject and other saucer functions

            #else:#if self.game.get_player_stats('mode_enabled')==False:
             #   self.eject()


#        def animation(self):
#            #time = 2
#            anim = dmd.Animation().load(game_path+"dmd/hof_title_trans.dmd")
#            hof_animation_1 = dmd.AnimatedLayer(frames=anim.frames,hold=False)
#            hof_animation_1.add_frame_listener(-1, self.choices)
#            self.layer = hof_animation_1
#
#            self.game.sound.play('hof_lit')
            #self.delay(name='callback', event_type=None, delay=time, handler=self.choices)


        def choices(self):
            
            #shuffle the possible selections
            shuffle(self.list)

            #set the choice
            self.chosen_list = [self.list[0],self.list[1],self.list[2],self.list[3]]
            self.log.info(self.list[0]+", "+self.list[1]+", "+self.list[2]+", "+self.list[3])
            
            #display the choice
            choice_anim = dmd.Animation().load(game_path+"dmd/hof_choose.dmd" ) 
            choice_bgnd_layer = dmd.FrameLayer(frame=choice_anim.frames[0])
            
            
            self.text_layer1.set_text(self.list[0].upper())
            self.text_layer2.set_text(self.list[1].upper())
            self.text_layer3.set_text(self.list[2].upper())
            self.text_layer4.set_text(self.list[3].upper())
            
            self.choices_layer = dmd.GroupedLayer(128, 32, [choice_bgnd_layer,self.text_layer1,self.text_layer2,self.text_layer3,self.text_layer4])
            #choices_layer.transition = dmd.ExpandTransition(direction='vertical')
            
            title_frame = dmd.Animation().load(game_path+"dmd/hof_banner.dmd")
            title_layer = dmd.FrameLayer(frame=title_frame.frames[0])
            title_layer.composite_op="invertedmask"
            mask_anim = dmd.Animation().load(game_path+"dmd/hof_mask.dmd")
            mask_layer = dmd.AnimatedLayer(frames=mask_anim.frames,hold=True,frame_time=4)
            mask_layer.add_frame_listener(-2, self.queue_chosen)
            
            curtain_layer = dmd.GroupedLayer(128,32,[mask_layer,title_layer])
            curtain_layer.composite_op = "blacksrc"
            
            hand_anim = dmd.Animation().load(game_path+"dmd/hof_hand.dmd")
            hand_layer = dmd.AnimatedLayer(frames=hand_anim.frames,hold=True,frame_time=4)
            hand_layer.composite_op = "blacksrc"
            
            display_layer = dmd.GroupedLayer(128,32,[self.choices_layer,curtain_layer,hand_layer])
            #display_layer.composite_op = "blacksrc"
            
            self.layer = display_layer
            
            self.game.sound.play('hof_lit')


#        def choices(self):
#            #shuffle the possible selections
#            shuffle(self.list)
#
#            #set the choice
#            self.chosen_list = [self.list[0],self.list[1],self.list[2],self.list[3]]
#            self.log.info(self.list[0]+", "+self.list[1]+", "+self.list[2]+", "+self.list[3])
#            
#            #main_anim
#            anim = dmd.Animation().load(game_path+"dmd/hof_title_trans.dmd")
#            hof_animation = dmd.AnimatedLayer(frames=anim.frames,hold=False, frame_time=4)
#            hof_animation.composite_op ="blacksrc"
#            hof_animation.add_frame_listener(-1, self.queue_chosen)
#            
#            #display the choice
#            bgnd_anim = dmd.Animation().load(game_path+"dmd/hof_choose.dmd")
#            bgnd_layer = dmd.FrameLayer(frame=bgnd_anim.frames[0])
#            
#            self.text_layer1.set_text(self.list[0].upper())
#            self.text_layer2.set_text(self.list[1].upper())
#            self.text_layer3.set_text(self.list[2].upper())
#            self.text_layer4.set_text(self.list[3].upper())
#            
#            self.choices_layer = dmd.GroupedLayer(128, 32, [bgnd_layer,self.text_layer1,self.text_layer2,self.text_layer3,self.text_layer4,hof_animation])
#            #choices_layer.transition = dmd.ExpandTransition(direction='vertical')
#            self.layer = self.choices_layer
#            
#            #play sound
#            self.game.sound.play('hof_lit')


        def queue_chosen(self):
            #set time to show choices
            time=3
            #set the callback to next section
            #self.delay(name='chosen_delay', event_type=None, delay=time, handler=self.chosen)
            
            self.delay(name='chosen_delay', event_type=None, delay=time, handler=self.chosen)


        def chosen(self):
            #shuffle possible choices
            shuffle(self.chosen_list)
            
            self.award(type='banner') #generate awards and the award layer with correct banners
            
            self.choices_layer.composite_op="invertedmask"
            mask_anim = dmd.Animation().load(game_path+"dmd/hof_mask.dmd")
            mask_layer = dmd.AnimatedLayer(frames=mask_anim.frames,hold=True,frame_time=4)
            mask_layer.add_frame_listener(-2, self.queue_award)
            
            curtain_layer = dmd.GroupedLayer(128,32,[mask_layer,self.choices_layer])
            curtain_layer.composite_op = "blacksrc"
            
            hand_anim = dmd.Animation().load(game_path+"dmd/hof_hand.dmd")
            hand_layer = dmd.AnimatedLayer(frames=hand_anim.frames,hold=True,frame_time=4)
            hand_layer.composite_op = "blacksrc"
            
            display_layer = dmd.GroupedLayer(128,32,[self.award_layer,curtain_layer,hand_layer])
            #display_layer.composite_op = "blacksrc"
            
            self.layer = display_layer
            
             #play sound
            self.game.sound.play('hof_selected') 
            

#        def chosen(self):
#            #main_anim
#            anim = dmd.Animation().load(game_path+"dmd/hof_second_trans.dmd")
#            anim_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False, frame_time=4)
#            anim_layer.composite_op ="blacksrc"
#            anim_layer.add_frame_listener(-1,self.award)
#            
#            self.layer = dmd.GroupedLayer(128, 32, [self.choices_layer,anim_layer])
#
#            #play sound
#            self.game.sound.play('hof_selected') 
           
        def queue_award(self):
            time=1
            self.delay(name='award_delay', event_type=None, delay=time, handler=self.award)

            
        def award(self,type='anim'):
           
            option = self.chosen_list[0]
    
            #debug
            #option=self.list[0]
            clear_time=3
            
            if option==self.list[0]:
                clear_time=1.5
                self.extra_ball_lit(type)
            elif option==self.list[1]:
                self.dog_fight_award(type)
            elif option==self.list[2]:
                self.eternal_life_award(timer=15,type=type)
            elif option==self.list[3]:
                clear_time=1.5
                self.bonusx_award(type)
            elif option==self.list[4]: #10 mil
                self.score_award(10000000)
            elif option==self.list[5]: #20 mil
                self.score_award(20000000)
            else:
                self.name_award()
                
            if type=='anim':            
                self.delay(name='end_delay', event_type=None, delay=clear_time, handler=self.clear)
            
                
            
#        def end(self):
#            #time to show chosen award
#            time=3  
#            #set the cleanup timer
#            self.delay(name='end_delay', event_type=None, delay=time, handler=self.clear)
            

        def extra_ball_lit(self,type):
            self.award_layer = self.game.extra_ball.lit(type)
                
        def dog_fight_award(self,type):
            self.name_award(type)
            
        def eternal_life_award(self,timer,type):
            anim = dmd.Animation().load(game_path+"dmd/eternal_life.dmd")
            #display the animation
            if type=='banner':
                self.award_layer = dmd.FrameLayer(frame=anim.frames[0])
            elif type=='anim':
                self.layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=3)
                self.game.sound.play('electricity')
                #start the ball saver
                self.game.ball_save.start(num_balls_to_save=1, time=timer, now=True, allow_multiple_saves=False)


        def name_award(self,type):
            chosen_layer = dmd.TextLayer(128/2, 7, self.game.fonts['9x7_bold'], "center", opaque=True)
            if type=='banner':
                chosen_layer.set_text(self.chosen_list[0].upper(),color=dmd.CYAN)
                self.award_layer=chosen_layer
            elif type=='anim':    
                #display the award chosen
                chosen_layer.set_text(self.chosen_list[0].upper(),blink_frames=2,color=dmd.CYAN)
                #chosen_layer.transition = dmd.ExpandTransition(direction='vertical')
                self.layer = chosen_layer
                self.game.score(2000000)


        def bonusx_award(self,type):
            if type=='banner':
                chosen_layer = dmd.TextLayer(128/2, 7, self.game.fonts['9x7_bold'], "center", opaque=True)
                chosen_layer.set_text('Advance Bonus X'.upper(),color=dmd.PURPLE)
                #chosen_layer.transition = dmd.ExpandTransition(direction='vertical')
                self.award_layer=chosen_layer
            elif type=='anim':
                self.advance_bonusx()
            
            #bonusx = self.game.get_player_stats('bonus_x')+1
            #display the award chosen
            #chosen_layer = dmd.TextLayer(128/2, 7, self.game.fonts['9x7_bold'], "center", opaque=True)
            #chosen_layer.set_text('BONUS X'+str(bonusx),blink_frames=2,color=dmd.PURPLE)
            #chosen_layer.transition = dmd.ExpandTransition(direction='vertical')
            #self.layer = chosen_layer

            #self.game.score(2000000)
            #self.game.set_player_stats('bonus_x',bonusx)


        def score_award(self,score):
            time=3
            value_layer = dmd.TextLayer(128/2, 4, self.game.fonts['23x12'], "center", opaque=True)
            if type=='banner':
                value_layer.set_text(locale.format("%d",score,True),color=dmd.GREEN)
                self.award_layer=chosen_layer
            elif type=='anim':   
                value_layer.set_text(locale.format("%d",score,True),blink_frames=2,color=dmd.GREEN)
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
                #self.animation()
                self.choices()
                #return procgame.game.SwitchStop

        def sw_leftInlane_active(self,sw):
            if self.status=='ready':
                self.set_status('lit')

        def sw_rightInlane_active(self,sw):
            if self.status=='ready':
                self.set_status('lit')