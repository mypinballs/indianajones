# Rope Bridge Game Mode

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
music_path = game_path +"music/"

#locale.setlocale(locale.LC_ALL, 'en_GB')
class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="center", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,justify)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()

#mpc animation layer for sprites
#class SpriteLayer(dmd.AnimatedLayer):
#
#        dot_type=None
#
#        def __init__(self, opaque=False, hold=True, repeat=False, frame_time=6, frames=None, x=0,y=0,dot_type=None):
#		super(SpriteLayer, self).__init__(opaque,x,y,dot_type)
#                self.target_x = x
#                self.target_y = y
#                self.dot_type = dot_type
#                self.composite_op = "blacksrc"
#
#                self.hold = hold
#		self.repeat = repeat
#		if frames == None:
#			self.frames = list()
#		else:
#			self.frames = frames
#
#		self.frame_time = frame_time # Number of frames each frame should be displayed for before moving to the next.
#		self.frame_time_counter = self.frame_time
#
#		self.frame_listeners = []
#
#		self.reset()
#
#	def next_frame(self):
#
#		frame = super(SpriteLayer, self).next_frame()
#
#		if frame:
#			if self.dot_type == 1:
#				for x in range(128):
#					for y in range(32):
#						color = frame.get_dot(x,y)
#						if color == 5: # These are the same dots as in dot_type 2, so we remove them by letting blacksrc hide them. Possibly this could be an additional tint in other animations?
#							frame.set_dot(x,y,0) # Ideally this should be set to alpha 0%
#						elif color == 15:
#							# These are the highlights of the sprite
#							pass
#                                                elif color == 10:
#                                                        frame.set_dot(x,y,12)
#			elif self.dot_type == 2:
#				for x in range(128):
#					for y in range(32):
#						color = frame.get_dot(x,y)
#						if color == 5:
#							frame.set_dot(x,y,1) # Ideally this should be 0 at alpha 100% if we could use blendmode alpha. Now we use 1 to come as close to black as possible.
#						elif color == 15:
#							#These are the midtones of the sprite
#							frame.set_dot(x,y,6)
#
#		return frame

class Rope_Bridge(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Rope_Bridge, self).__init__(game, priority)

            self.log = logging.getLogger('ij.rope_bridge')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Rope Bridge Timer'])
            self.log.info("Rope Bridge Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(128/2, 0, self.game.fonts['9x7_bold'], self)
            self.score_layer.composite_op ="blacksrc"
            
            self.award_layer = dmd.TextLayer(128/2, 0, self.game.fonts['23x12'], "center", opaque=False)
            self.award_layer.composite_op ="blacksrc"
            
            #sound setup
            self.game.sound.register_music('background_play', music_path+"rope_bridge.aiff")
            self.game.sound.register_sound('rb_shot_hit', sound_path+"out_of_breath.aiff")
            self.game.sound.register_sound('rb_s0', speech_path+"come_on_indy.aiff")
            self.game.sound.register_sound('rb_s1', sound_path+"sword_chop.aiff")
            self.game.sound.register_sound('rb_s2', sound_path+"bridge_fall.aiff")

            #lamps setup
            self.lamps = ['leftRampArrow','rightRampArrow']
            
            self.reset()


        def reset(self):
            #var setup
            self.count = 0
            self.score_value_boost = 1000000
            self.score_value_start = 10000000
            self.score_value_completed = self.score_value_start*2
            self.score_value_extra = 2000000
            
            self.bridge_x_posn = 0
            self.indy_x_posn = 0
            self.indy_y_posn = 0

        def load_scene_anim(self,count):
            
            max_count=5 # should be a setting
            #range=120/max_count #20

            if count<max_count:
                self.bridge_move_completed = False
                self.indy_move_completed = False

                self.move_sprite(layer=self.bridge_sprite_layer,amount=-3,range=30,x_store=self.bridge_x_posn,callback=self.bridge_move_callback)
                self.load_indy(x_posn=self.indy_x_posn,y_posn=self.indy_y_posn,status='run')
                self.move_indy(amount=2,range=22,callback=self.indy_move_callback)
                self.award_score()
                self.layer = dmd.GroupedLayer(128, 32, [self.sky_layer,self.bridge_sprite_layer,self.award_layer,self.indy_sprite_layer])
                
            else:
                self.completed()

        def completed(self):
            self.bgnd_anim = "dmd/rope_bridge_completed.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=6)
            self.scene_layer.add_frame_listener(-10,self.completed_sound1)
            self.scene_layer.add_frame_listener(-6,self.completed_sound2)
            self.scene_layer.add_frame_listener(-1,self.award_completed_score)
            self.scene_layer.add_frame_listener(-1,self.end_scene_delay)
            self.layer = self.scene_layer
            
            
        def completed_sound1(self):
            self.game.sound.play('rb_s1')
        
        
        def completed_sound2(self):
            self.game.sound.play('rb_s2')
            
            
        def end_scene_delay(self):
            self.delay(name='end_scene_delay', event_type=None, delay=2, handler=self.mode_select.end_scene)


        def load_start_anim(self):
            self.log.info('Indy X Store posn:%s',self.indy_x_posn)
            self.load_bridge_animation(x_posn=self.bridge_x_posn)
            self.load_indy(x_posn=self.indy_x_posn,y_posn=self.indy_y_posn)
            
            self.layer = dmd.GroupedLayer(128, 32, [self.sky_layer,self.bridge_sprite_layer,self.score_layer,self.award_layer,self.indy_sprite_layer,self.timer_layer,self.info_layer])
          
          
        def load_continue_anim(self):
            if self.indy_move_completed and self.bridge_move_completed:
                self.log.info('Indy X Store posn:%s',self.indy_x_posn)
                self.load_indy(x_posn=self.indy_x_posn,y_posn=self.indy_y_posn,status='stand')
                self.layer = dmd.GroupedLayer(128, 32, [self.sky_layer,self.bridge_sprite_layer,self.score_layer,self.award_layer,self.indy_sprite_layer,self.timer_layer,self.info_layer])
          
          
        def indy_move_callback(self):
            self.indy_move_completed = True
            self.load_continue_anim()
            
        def bridge_move_callback(self):
            self.bridge_move_completed = True
            self.load_continue_anim()
            
            
        def load_bridge_animation(self,x_posn=0,y_posn=0):
            bridge_sprites = dmd.Animation().load("dmd/rb_bgnd.dmd").frames
            
            #set posn of sprite
            x=x_posn
            y=y_posn
            y+=6
            
            sprite_data_layers = []
            
            for i in range(len(bridge_sprites)):
                #remember - frames start at 0
#                even_frames = bridge_sprites[i][0::2] # This layer gets hilight frames
#                odd_frames = bridge_sprites[i][1::2] # This layer gets the low colour and mask frames
#                
#                sprite_data1 = SpriteLayer(frames=even_frames, opaque=False, hold=True, repeat=False, x=x,y=y, dot_type=1)
#                sprite_data2 = SpriteLayer(frames=odd_frames, opaque=False, hold=True, repeat=False, x=x,y=y, dot_type=2)
#            
#                sprite_data_layers += [sprite_data2]
#                sprite_data_layers += [sprite_data1]

                sprite_data = dmd.FrameLayer(frame=bridge_sprites[i])
                sprite_data.target_x=x
                sprite_data.target_y=y
                sprite_data_layers += [sprite_data]
                
                x=128

            self.bridge_sprite_layer = dmd.layers.GroupedLayer(384,32, sprite_data_layers)
            self.bridge_sprite_layer.composite_op ="blacksrc"
            

            self.log.info("bridge created")
            
            
        def load_indy(self, x_posn=0, y_posn=0, status='stand'):
            indy_standing_body_sprite = dmd.Animation().load("dmd/rb_sprites_indy_standing_body.dmd").frames
            indy_standing_head_sprite = dmd.Animation().load("dmd/rb_sprites_indy_standing_head.dmd").frames
            indy_running_sprite = dmd.Animation().load("dmd/rb_sprites_indy_running.dmd").frames

            #set posn of sprite
            x=x_posn
            y=y_posn
            x-=26
            y-=2
            
            sprite_data_layers = []
            
            if status=='stand':
                #remember - frames start at 0
#                even_frames = indy_standing_body_sprite[0::2] # This layer gets hilight frames
#                odd_frames = indy_standing_body_sprite[1::2] # This layer gets the low colour and mask frames
#                
#                sprite_data1 = SpriteLayer(frames=even_frames, opaque=False, hold=True, repeat=False, x=x,y=y, dot_type=1)
#                sprite_data2 = SpriteLayer(frames=odd_frames, opaque=False, hold=True, repeat=False, x=x,y=y, dot_type=2)
#                
#                even_frames = indy_standing_head_sprite[0::2] # This layer gets hilight frames
#                odd_frames = indy_standing_head_sprite[1::2] # This layer gets the low colour and mask frames
#                
#                sprite_data3 = SpriteLayer(frames=even_frames, opaque=False, hold=False, repeat=True, x=x,y=y-9, dot_type=1)
#                sprite_data4 = SpriteLayer(frames=odd_frames, opaque=False, hold=False, repeat=True, x=x,y=y-9, dot_type=2)
                
                sprite_data1 = dmd.AnimatedLayer(frames=indy_standing_body_sprite,hold=True,repeat=False,frame_time=6)
                sprite_data1.target_x=x
                sprite_data1.target_y=y
                sprite_data1.composite_op ="blacksrc"
                
                sprite_data2 = dmd.AnimatedLayer(frames=indy_standing_head_sprite,hold=False,repeat=True,frame_time=12)
                sprite_data2.target_x=x
                sprite_data2.target_y=y-9
                sprite_data2.composite_op ="blacksrc"

                sprite_data_layers += [sprite_data2]
                sprite_data_layers += [sprite_data1]
                #sprite_data_layers += [sprite_data4]
                #sprite_data_layers += [sprite_data3]
                
                self.indy_sprite_layer = dmd.layers.GroupedLayer(128,32, sprite_data_layers) 
               

            elif status=='run':
#                even_frames = indy_running_sprite[0::2] # This layer gets hilight frames
#                odd_frames = indy_running_sprite[1::2] # This layer gets the low colour and mask frames
#                
#                sprite_data1 = SpriteLayer(frames=even_frames, opaque=False, hold=False, repeat=True, x=x,y=y, dot_type=1)
#                sprite_data2 = SpriteLayer(frames=odd_frames, opaque=False, hold=False, repeat=True, x=x,y=y, dot_type=2)
                
#                sprite_data_layers += [sprite_data2]
#                sprite_data_layers += [sprite_data1]
           
                self.indy_sprite_layer = dmd.AnimatedLayer(frames=indy_running_sprite,hold=False,repeat=True,frame_time=6)
                self.indy_sprite_layer.target_x=x
                self.indy_sprite_layer.target_y=y
                
                
            self.indy_sprite_layer.composite_op ="blacksrc"

            self.log.info("indy sprite created")
            
            
#        def move_bridge(self,range=20):
#            x=range
#            if x>0:
#                self.bridge_sprite_layer.target_x -=2
#                x-=2
#                self.delay(name='move_bridge_loop',delay=0.2,handler=lambda:self.move_bridge())
#            else:
#                self.cancel_delayed('move_bridge_loop')

                
        def move_sprite(self,layer,amount,range,x_store,callback=None):
            layer.target_x +=amount
            x_store +=amount
            
            self.delay(name='move_sprite_forward',delay=0.2,handler=lambda:self.move_sprite(layer,amount,range,x_store,callback))

            if layer.target_x%range==0:
                self.cancel_delayed('move_sprite_forward')
                
                if callback:
                    callback()
        
        
        def move_indy(self,amount,range,callback=None):
            self.indy_sprite_layer.target_x +=amount
            self.indy_x_posn +=amount
             
            #loop
            self.delay(name='move_indy_sprite',delay=0.2,handler=lambda:self.move_indy(amount,range,callback))
            
            #determine when to stop indy moving
            if self.indy_sprite_layer.target_x%range==0:
                self.cancel_delayed('move_indy_sprite')            
                if callback:
                    callback()
                    
            #work out when to shift indy in the y plane
            self.log.info('indy x posn:%s',self.indy_x_posn)
            if self.indy_x_posn<38 and self.indy_x_posn%10==0:
                self.indy_sprite_layer.target_y+=1
                self.indy_y_posn+=1
            elif self.indy_x_posn>48 and self.indy_x_posn%10==0:
                self.indy_sprite_layer.target_y-=1
                self.indy_y_posn-=1    
        

        def mode_started(self):
            #load player stats
            self.rope_bridge_distance = self.game.get_player_stats('rope_bridge_distance');
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(0, -1, self.game.fonts['07x5'],self.timer,"left")
            self.timer_layer.composite_op="blacksrc"
            
            self.info_layer = dmd.TextLayer(128/2, 20, self.game.fonts['07x5'], "center", opaque=False)
            #self.info_layer.set_text("SHOOT LIT SHOTS",blink_frames=1000)
        
            sky_bgnd = dmd.Animation().load(game_path+"dmd/blue_sky_bgnd.dmd")
            self.sky_layer = dmd.FrameLayer(frame=sky_bgnd.frames[0])

            #load animation
            self.load_start_anim()
            
            
            #start mode music & speech
            self.game.sound.play_music('background_play', loops=-1)
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

            self.rope_bridge_distance+=self.count
            self.game.set_player_stats('rope_bridge_distance',self.rope_bridge_distance)

            score_value = self.score_value_start*self.count
            self.game.set_player_stats('rope_bridge_score',score_value)
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


        def voice_call(self,count,delay=None,label="rb_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

            #additional speech calls
#            if count==0:
#                self.delay(name='aux_mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=1)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True), color=dmd.YELLOW)
     

        def mode_progression(self):

            self.count+=1

            #load progression animation
            #self.delay(name='scene_anim_delay', event_type=None, delay=2, handler=self.load_scene_anim, param=self.count)
            self.load_scene_anim(self.count)
            
            #play sound
            self.game.sound.play('rb_shot_hit')


        def award_score(self,score_value=0):
            score_value = self.score_value_start

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3, color=dmd.MAGENTA)
            self.game.score(score_value)

        def award_completed_score(self,score_value=0):
            score_value = self.score_value_completed

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3, color=dmd.PURPLE)
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


        def sw_leftRampMade_active(self, sw):
            self.mode_progression()

            return procgame.game.SwitchStop

        def sw_rightRampMade_active(self, sw):
            self.mode_progression()

            return procgame.game.SwitchStop
        