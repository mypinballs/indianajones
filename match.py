# Match Mode

__author__="jim"


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


class Match(game.Mode):

	def __init__(self, game, priority):
            super(Match, self).__init__(game, priority)

            self.log = logging.getLogger('ij.match')

            self.match_layer = dmd.TextLayer(24, 11, self.game.fonts['num_09Bx7'], "left", opaque=False)
            self.p1_layer = dmd.TextLayer(0, 0, self.game.fonts['6x6_bold'], "left", opaque=False)
            self.p2_layer = dmd.TextLayer(20, 0, self.game.fonts['6x6_bold'], "left", opaque=False)
            self.p3_layer = dmd.TextLayer(108, 0, self.game.fonts['6x6_bold'], "right", opaque=False)
            self.p4_layer = dmd.TextLayer(128, 0, self.game.fonts['6x6_bold'], "right", opaque=False)

            self.value_range = 9
            

            self.game.sound.register_sound('see_you', speech_path+"see_you_tomorrow.aiff")
            self.game.sound.register_sound('top_men', speech_path+"top_men.aiff")
            self.game.sound.register_sound('success', sound_path+"match_success.aiff")
            self.game.sound.register_sound('fail', sound_path+"match_fail.aiff")
            self.game.sound.register_music('raiders_march', music_path+"raiders_march.aiff")
            
            self.reset()


        def reset(self):
            self.value = 0
            self.player_digits = []
            self.play=False


        def mode_started(self):
            self.reset()

            self.game.sound.stop_music()
            self.generate_digits()
            self.generate_match()
            self.play_anim()



        def mode_stopped(self):
            #set the status
            self.game.system_status='game_over'
            
            #add the attact mode and play the see you tommorow sample
            self.game.modes.add(self.game.attract_mode)
            self.game.sound.play_voice('see_you')
            
            self.game.sound.play_music('raiders_march', loops=10)


        def play_anim(self):

            self.bgnd_anim = dmd.Animation().load(game_path+"dmd/match_bgnd.dmd")
            #if xxx:
            self.bgnd_layer = dmd.FrameLayer(frame=self.bgnd_anim.frames[0])
            #else:
            #    
                
            self.bgnd_layer.composite_op = "blacksrc"

            man_frames = dmd.Animation().load("dmd/match_man.dmd").frames
            box_frames = dmd.Animation().load("dmd/match_cart.dmd").frames

            #create man sprite
            #set the sprite posn
            x = -50
            y = 1

            self.man_sprite_layer = dmd.AnimatedLayer(frames=man_frames,hold=False,repeat=True,frame_time=6)
            self.man_sprite_layer.target_x=x
            self.man_sprite_layer.target_y=y
            self.man_sprite_layer.composite_op ="blacksrc"

            self.log.debug("man sprite created")

            #create box sprite
            #set the sprite posn
            x = -25
            y = 3
            
            self.box_sprite_layer = dmd.AnimatedLayer(frames=box_frames,hold=False,repeat=True,frame_time=6)
            self.box_sprite_layer.target_x=x
            self.box_sprite_layer.target_y=y       
            self.box_sprite_layer.composite_op ="blacksrc"

            self.log.debug("box sprite created")

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.match_layer,self.p1_layer,self.p2_layer,self.p3_layer,self.p4_layer,self.bgnd_layer,self.box_sprite_layer,self.man_sprite_layer])

            #play speech
            self.game.sound.play_voice('top_men')


            self.move_sprite(self.box_sprite_layer,self.man_sprite_layer)


        def move_sprite(self,layer1,layer2):
            layer1.target_x +=4
            layer2.target_x +=4

            self.cancel_delayed('move_sprite_forward')
            self.delay(name='move_sprite_forward',delay=0.2,handler=lambda:self.move_sprite(layer1,layer2))

            if layer1.target_x>128:
                self.cancel_delayed('move_sprite_forward')
            elif layer1.target_x>=100 and not self.play:
                self.play=True
                self.bgnd_layer = dmd.AnimatedLayer(frames=self.bgnd_anim.frames,repeat=False,frame_time=3)
                self.bgnd_layer.composite_op = "blacksrc"
                self.layer = dmd.GroupedLayer(128, 32, [self.match_layer,self.p1_layer,self.p2_layer,self.p3_layer,self.p4_layer,self.bgnd_layer,self.box_sprite_layer,self.man_sprite_layer])

                #check for match
                self.check()

        def generate_match(self):
        #create the match value for comparison

            self.value = (random.randint(0, self.value_range))*10
            if self.value==0:
                display = "0"+str(self.value)
            else:
                display = str(self.value)

            #set text
            self.match_layer.set_text(display,color=dmd.PURPLE)



        def generate_digits(self):
        #extract and display the last 2 score digits for each player

            player_layers=[self.p1_layer,self.p2_layer,self.p3_layer,self.p4_layer]

            for i in range(len(self.game.players)):
                score = self.game.players[i].score
                digit = str(score)[-2:-1]
                player_layers[i].set_text(str(score)[-2:],color=dmd.YELLOW)
                #set var for comparison
                self.player_digits.append(int(digit))


        def check(self):
            #self.credits = audits.display(self.game,'general','creditsCounter') for ewhen audit system is added to indy :)

            for i in range(len(self.player_digits)):
                self.log.debug("%s:%s",self.player_digits[i],self.value)
                if self.player_digits[i]==self.value:
                     #audits.update_counter(self.game,'credits',self.credits+1)
                     self.game.sound.play('success')
                else:
                    self.game.sound.play('fail')

            #queue the cleanup and removal of the mode now its all done
            self.delay(name='cleanup',delay=1.5,handler=self.clear)


        def clear(self):
            self.layer = None
            self.game.modes.remove(self)