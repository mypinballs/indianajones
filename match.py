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

#mpc animation layer for sprites
class SpriteLayer(dmd.AnimatedLayer):

        dot_type=None

        def __init__(self, opaque=False, hold=True, repeat=False, frame_time=6, frames=None, x=0,y=0,dot_type=None):
		super(SpriteLayer, self).__init__(opaque,x,y,dot_type)
                self.target_x = x
                self.target_y = y
                self.dot_type = dot_type
                self.composite_op = "blacksrc"

                self.hold = hold
		self.repeat = repeat
		if frames == None:
			self.frames = list()
		else:
			self.frames = frames

		self.frame_time = frame_time # Number of frames each frame should be displayed for before moving to the next.
		self.frame_time_counter = self.frame_time

		self.frame_listeners = []

		self.reset()

	def next_frame(self):

		frame = super(SpriteLayer, self).next_frame()

		if frame:
			if self.dot_type == 1:
				for x in range(128):
					for y in range(32):
						color = frame.get_dot(x,y)
						if color == 5: # These are the same dots as in dot_type 2, so we remove them by letting blacksrc hide them. Possibly this could be an additional tint in other animations?
							frame.set_dot(x,y,0) # Ideally this should be set to alpha 0%
						elif color == 15:
							# These are the highlights of the monkeys face, they should remain white
							pass
                                                elif color == 10:
                                                        frame.set_dot(x,y,12)
			elif self.dot_type == 2:
				for x in range(128):
					for y in range(32):
						color = frame.get_dot(x,y)
						if color == 5:
							frame.set_dot(x,y,1) # Ideally this should be 0 at alpha 100% if we could use blendmode alpha. Now we use 1 to come as close to black as possible.
						elif color == 15:
							#These are the hightlights of the monkeys body, tone them down a little.
							frame.set_dot(x,y,6)

		return frame


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
            self.value = 0
            self.player_digits = [0,0,0,0]
            self.play=False

            self.game.sound.register_sound('see_you', speech_path+"see_you_tomorrow.aiff")
            self.game.sound.register_sound('top_men', speech_path+"top_men.aiff")
            self.game.sound.register_sound('success', sound_path+"match_success.aiff")
            self.game.sound.register_sound('fail', sound_path+"match_fail.aiff")
            self.game.sound.register_music('raiders_march', music_path+"raiders_march.aiff")
            
            self.reset()


        def reset(self):
            pass


        def mode_started(self):
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
            #remember - frames start at 0
            even_frames = man_frames[0::2] # This layer gets hilight frames
            odd_frames = man_frames[1::2] # This layer gets the low colour and mask frames

            #set the sprite posn
            x = -52
            y = 1

            self.sprite_data1 = SpriteLayer(frames=even_frames, opaque=False, hold=False, repeat=True, x=x,y=y, dot_type=1)
            self.sprite_data2 = SpriteLayer(frames=odd_frames, opaque=False, hold=False, repeat=True, x=x,y=y, dot_type=2)

            self.sprite_data_layers = []
            self.sprite_data_layers += [self.sprite_data2]
            self.sprite_data_layers += [self.sprite_data1]

            self.man_sprite_layer = dmd.layers.GroupedLayer(128,32, self.sprite_data_layers)
            self.man_sprite_layer.composite_op ="blacksrc"


            self.log.debug("man sprite created")

            #create box sprite
            #remember - frames start at 0
            even_frames = box_frames[0::2] # This layer gets hilight frames
            odd_frames = box_frames[1::2] # This layer gets the low colour and mask frames

            #set the sprite posn
            x = -25
            y = 3

            self.sprite_data1 = SpriteLayer(frames=even_frames, opaque=False, hold=False, repeat=True, x=x,y=y, dot_type=1)
            self.sprite_data2 = SpriteLayer(frames=odd_frames, opaque=False, hold=False, repeat=True, x=x,y=y, dot_type=2)

            self.sprite_data_layers = []
            self.sprite_data_layers += [self.sprite_data2]
            self.sprite_data_layers += [self.sprite_data1]

            self.box_sprite_layer = dmd.layers.GroupedLayer(128,32, self.sprite_data_layers)
            self.box_sprite_layer.composite_op ="blacksrc"
            

            self.log.debug("box sprite created")

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.match_layer,self.p1_layer,self.p2_layer,self.p3_layer,self.p4_layer,self.bgnd_layer,self.box_sprite_layer,self.man_sprite_layer])

            #play speech
            self.game.sound.play_voice('top_men')


            self.move_sprite(self.box_sprite_layer,self.man_sprite_layer)


        def move_sprite(self,layer1,layer2):
            layer1.target_x +=6
            layer2.target_x +=6

            self.delay(name='move_sprite_forward',delay=0.2,handler=lambda:self.move_sprite(layer1,layer2))

            if layer1.target_x>128:
                self.cancel_delayed('move_sprite_forward')
            elif layer1.target_x>=90 and not self.play:
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
            self.match_layer.set_text(display)



        def generate_digits(self):
        #extract and display the last 2 score digits for each player

            player_layers=[self.p1_layer,self.p2_layer,self.p3_layer,self.p4_layer]

            for i in range(len(self.game.players)):
                score = self.game.players[i].score
                digit = str(score)[-2:-1]
                player_layers[i].set_text(str(score)[-2:])
                #set var for comparison
                self.player_digits[i]=digit


        def check(self):
            #self.credits = audits.display(self.game,'general','creditsCounter') for ewhen audit system is added to indy :)

            for i in range(len(self.player_digits)):
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
