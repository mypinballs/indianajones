# Tank Chase Game Mode
# Jim
# Nov 2012

import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

#locale.setlocale(locale.LC_ALL, 'en_GB')
class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="center", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,mode)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


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


class Tank_Chase(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Tank_Chase, self).__init__(game, priority)

            self.log = logging.getLogger('ij.tankChase')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen seetup
            self.score_layer = ModeScoreLayer(0, -1, self.game.fonts['07x5'], self)
            self.award_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            self.award_layer.composite_op ="blacksrc"
            self.sprite_layer = None
            #self.sprite_layer2 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)

            #sound setup
            self.game.sound.register_music('tc_background_play', music_path+"tank_chase.aiff")
            self.game.sound.register_sound('tc_shot_hit', sound_path+"horse_gallap.aiff")
            self.game.sound.register_sound('tc_tank_fall', sound_path+"tumble.aiff")
            self.game.sound.register_sound('tc_tank_crash', sound_path+"crash.aiff")
            self.game.sound.register_sound('tc_s0', speech_path+"wheres_my_father.aiff")
            self.game.sound.register_sound('tc_s1', speech_path+"have_him_steel_beast.aiff")
            self.game.sound.register_sound('tc_s4', speech_path+"come_on_dad.aiff")
            self.game.sound.register_sound('tc_s5', speech_path+"great_shot.aiff")

            #lamps setup
            self.lamps = ['leftLoop','rightLoop',]


        def reset(self):
            #load stored vars from settings
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Tank Chase Timer'])
            self.log.info("Tank Chase Timer is:"+str(self.timer))

            #var setup
            self.count = 0
            self.score_value_boost = 1000000
            self.score_value_start = 10000000
            self.score_value_completed = self.score_value_start*2
            self.score_value_extra = 2000000

        def load_scene_anim(self,count):

            if count<4:
#                self.scene_anim = "dmd/tank_chase_scene_"+str(count)+".dmd"
#                anim = dmd.Animation().load(game_path+self.scene_anim)
#                self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=2)
#                self.scene_layer.add_frame_listener(-1,self.award_score)
#                self.scene_layer.add_frame_listener(-1, self.load_bgnd_anim)
#                self.layer = self.scene_layer

                #move the horse sprite
                self.move_sprite(self.sprite_layer)
                self.award_score()
                self.game.sound.play('tc_shot_hit')

            elif count<5:
                #run rescue animation
                self.rescue_part1()
                self.award_score()
                self.voice_call(count)
            else:
                #cancel the scene timout timer
                #self.cancel_delayed("scene_timeout")
                self.mode_select.cancel_timeout()
                #run completion animation
                self.completed()
                self.voice_call(count)

        def rescue_part1(self):
            escape_frames = dmd.Animation().load("dmd/tank_chase_jones_snr_escape.dmd").frames

            #set the sprite posn
            x = 24
            y = -10

            #remember - frames start at 0
            even_frames = escape_frames[0::2] # This layer gets hilight frames
            odd_frames = escape_frames[1::2] # This layer gets the low colour and mask frames

            sprite_data1 = SpriteLayer(frames=even_frames, opaque=False, hold=False, repeat=False, x=x,y=y, dot_type=1)
            sprite_data2 = SpriteLayer(frames=odd_frames, opaque=False, hold=False, repeat=False, x=x,y=y, dot_type=2)
            #load next animation part at end of this part
            sprite_data1.add_frame_listener(-1,self.rescue_part2)

            #join the data together using group layer
            sprite_data_layers = []
            sprite_data_layers += [sprite_data2]
            sprite_data_layers += [sprite_data1]

            self.sprite_layer2 = dmd.layers.GroupedLayer(128,32, sprite_data_layers)
            self.sprite_layer2.composite_op ="blacksrc"

            self.log.info("jones snr escape sprite created")

            #update the display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sprite_layer,self.sprite_layer2,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])


        def rescue_part2(self):
            file = "dmd/tank_chase_jones_snr_horse.dmd"
            anim = dmd.Animation().load(game_path+file)
            self.sprite_layer2 = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False)
            self.sprite_layer2.composite_op ="blacksrc"
            self.sprite_layer2.target_x =24
            self.sprite_layer2.target_y =4

            #update the display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sprite_layer,self.sprite_layer2,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])

            #setup the reverse movement of both sprites
            self.reverse_sprite(self.sprite_layer)
            self.reverse_sprite(self.sprite_layer2)


        def completed(self):
            
            #create the completion animation
            self.bgnd_anim = "dmd/tank_chase_completed.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            frame_time = 6
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False,frame_time=frame_time)
            self.scene_layer.add_frame_listener(-2*frame_time,self.award_completed_score)
            self.scene_layer.add_frame_listener(-2*frame_time,lambda:self.game.sound.play('tc_tank_fall'))
            self.scene_layer.add_frame_listener(-1*frame_time,lambda:self.game.sound.play('tc_tank_crash'))
            self.scene_layer.add_frame_listener(-1,self.end_scene_delay)
            self.layer = dmd.GroupedLayer(128, 32, [self.scene_layer,self.award_layer])

        def end_scene_delay(self):
            self.delay(name='scene_cleanup', event_type=None, delay=2, handler=self.mode_select.end_scene)

        def load_bgnd_anim(self):
            self.bgnd_anim = "dmd/tank_chase_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])

        def load_main_anim(self,x_posn=0,y_posn=0,delay=None):

            #set posn of sprite
            x=x_posn
            y=y_posn
            x=-44
            y=+6

            if delay:
                self.delay(name='create_sprite_layer', event_type=None, delay=delay, handler=self.create_horse_sprite, param=data)
            else:
                horse_frames = dmd.Animation().load("dmd/tank_chase_horse.dmd").frames

                #remember - frames start at 0
                even_frames = horse_frames[0::2] # This layer gets hilight frames
                odd_frames = horse_frames[1::2] # This layer gets the low colour and mask frames
                
                self.sprite_data1 = SpriteLayer(frames=even_frames, opaque=False, hold=False, repeat=True, x=x,y=y, dot_type=1)
                self.sprite_data2 = SpriteLayer(frames=odd_frames, opaque=False, hold=False, repeat=True, x=x,y=y, dot_type=2)

                self.sprite_data_layers = []
                self.sprite_data_layers += [self.sprite_data2]
                self.sprite_data_layers += [self.sprite_data1]

                self.sprite_layer = dmd.layers.GroupedLayer(128,32, self.sprite_data_layers)
                self.sprite_layer.composite_op ="blacksrc"

                self.log.info("sprite created")

                self.bgnd_anim = "dmd/tank_chase_bgnd.dmd"
                anim = dmd.Animation().load(game_path+self.bgnd_anim)
                self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sprite_layer,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])


        def move_sprite(self,layer):
            layer.target_x +=2
            
            self.delay(name='move_sprite_forward',delay=0.2,handler=lambda:self.move_sprite(layer))

            if layer.target_x%22==0:
                self.cancel_delayed('move_sprite_forward')

        def reverse_sprite(self,layer,callback=None):
            layer.target_x -=5

            self.delay(name='move_sprite_back',delay=0.2,handler=lambda:self.reverse_sprite(layer))

            if layer.target_x<-80:
                self.cancel_delayed('move_sprite_back')
                #if callback:
                    #callback()

        def mode_started(self):
            #reset
            self.reset()

            #load player stats
            self.distance = self.game.get_player_stats('tank_chase_distance')
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(128, -1, self.game.fonts['07x5'],self.timer,"right")
            self.info_layer = dmd.TextLayer(128/2, 20, self.game.fonts['07x5'], "center", opaque=False)
            #self.info_layer.set_text("SHOOT LIT SHOTS",blink_frames=1000)

            #load animation
            self.load_main_anim()
            #self.load_bgnd_anim()
            
            #start mode music & speech
            self.game.sound.play_music('tc_background_play', loops=-1)
            self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.voice_call, param=self.count)

            #open gates
            self.open_gates('left')
            self.open_gates('right')

            #update_lamps
            self.update_lamps()

        def mode_stopped(self):
            #save player stats
#            current_list = self.game.get_player_stats('mode_status_tracking');
#            updated_list =current_list
#            updated_list[0]=1
#
#            self.game.set_player_stats('mode_status_tracking',updated_list)

            self.distance+=self.count
            self.game.set_player_stats('tank_chase_distance',self.distance)

            score_value = self.score_value_start*self.count
            self.game.set_player_stats('tank_chase_score',score_value)
            self.game.set_player_stats('last_mode_score',score_value)


            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #reset music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)

            #clear display
            self.clear()

            #close gates
            self.close_gates('left')
            self.close_gates('right')

            #reset lamps
            self.reset_lamps()

        def mode_tick(self):
            pass


        def open_gates(self,side):
            if side=='left':
                 self.game.coils.rightControlGate.pulse(0)
            elif side=='right':
                 self.game.coils.leftControlGate.pulse(0)

        def close_gates(self,side):
            if side=='left':
                 self.game.coils.rightControlGate.disable()
            elif side=='right':
                 self.game.coils.leftControlGate.disable()


        def voice_call(self,count,delay=None,label="tc_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

            #additional speech calls
            if count==0:
                self.delay(name='aux_mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=1)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)
     

        def mode_progression(self):

            self.count+=1

            #load progression animation
            #self.delay(name='scene_anim_delay', event_type=None, delay=2, handler=self.load_scene_anim, param=self.count)

            
            self.load_scene_anim(self.count)


        def award_score(self,score_value=0):
            score_value = self.score_value_start

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=1, color=dmd.MAGENTA)
            self.game.score(score_value)

        def award_completed_score(self,score_value=0):
            score_value = self.score_value_completed

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=2, color=dmd.GREEN)
            self.game.score(score_value)

            
        def mode_bonus(self):
            self.game.score(score_value_bonus)


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'on')

        def clear(self):
            self.layer = None


        def sw_leftLoopTop_active(self, sw):
            self.mode_progression()

            return procgame.game.SwitchStop

        def sw_rightLoopTop_active(self, sw):
            self.mode_progression()

            return procgame.game.SwitchStop
        